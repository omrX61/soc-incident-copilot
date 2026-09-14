"""Foundry Local + RAG orchestration for Phi-3.5 Mini."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from src.config import config
from src.prompts import SYSTEM_PROMPT, build_user_prompt
from src.query_policy import QueryPolicy, policy_for
from src.vector_store import SearchHit, VectorStore


class ChatEngine:
    def __init__(self) -> None:
        self.store = VectorStore(config.db_path)
        self.ready = False
        self.status: dict[str, Any] = {"phase": "init", "message": "Starting..."}
        self._status_cb: Callable[[dict[str, Any]], None] | None = None
        self._native_client = None
        self._openai_client = None
        self._model_id = config.model
        self._backend = "none"

    def on_status(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._status_cb = callback

    def _set_status(self, phase: str, message: str) -> None:
        self.status = {"phase": phase, "message": message}
        if self._status_cb:
            self._status_cb(self.status)

    def get_store(self) -> VectorStore:
        return self.store

    def init(self) -> None:
        self._set_status("model", f"Loading {config.model} via Foundry Local...")
        last_error: Exception | None = None
        for loader in (self._init_foundry_v2, self._init_foundry_legacy):
            try:
                loader()
                self.ready = True
                self._set_status("ready", f"Ready ({self._backend})")
                return
            except Exception as exc:  # noqa: BLE001 — try next backend
                last_error = exc
        raise RuntimeError(
            "Foundry Local could not be initialized. Install Foundry Local "
            f"(winget install Microsoft.FoundryLocal) and pip package foundry-local-sdk. Last error: {last_error}"
        )

    def _init_foundry_v2(self) -> None:
        from foundry_local_sdk import Configuration, FoundryLocalManager

        try:
            FoundryLocalManager.initialize(Configuration(app_name=config.app_name))
        except Exception as exc:
            if "already been initialized" not in str(exc).lower() and "singleton" not in str(exc).lower():
                raise
        manager = FoundryLocalManager.instance
        if hasattr(manager, "download_and_register_eps"):
            try:
                manager.download_and_register_eps()
            except Exception:
                pass
        model = manager.catalog.get_model(config.model)
        if hasattr(model, "download"):
            model.download()
        already_loaded = bool(getattr(model, "is_loaded", False))
        if not already_loaded:
            model.load()
        self._native_client = model.get_chat_client()
        self._native_client.settings.temperature = config.temperature
        self._native_client.settings.max_tokens = config.max_tokens
        self._model_id = getattr(model, "id", config.model)
        self._backend = "foundry_local_sdk"

    def _init_foundry_legacy(self) -> None:
        from openai import OpenAI

        try:
            from foundry_local import FoundryLocalManager as LegacyManager
        except ImportError:
            from foundry_local_sdk import FoundryLocalManager as LegacyManager

        manager = LegacyManager(config.model)
        endpoint = getattr(manager, "endpoint", None) or getattr(manager, "service_uri", None)
        api_key = getattr(manager, "api_key", "not-needed")
        model_info = manager.get_model_info(config.model) if hasattr(manager, "get_model_info") else None
        if model_info is not None:
            self._model_id = getattr(model_info, "id", config.model)
        if not endpoint:
            raise RuntimeError("Legacy Foundry Local manager did not expose an endpoint")
        self._openai_client = OpenAI(base_url=endpoint, api_key=api_key)
        self._backend = "foundry_local_openai"

    def retrieve(self, question: str, top_k: int | None = None) -> list[SearchHit]:
        return self.store.search(question, top_k or config.top_k)

    def prepare(
        self,
        question: str,
        history: list[dict[str, str]] | None = None,
        incident_context: str | None = None,
    ) -> tuple[list[SearchHit], list[dict[str, str]], QueryPolicy]:
        policy = policy_for(question)
        hits: list[SearchHit] = []
        if not policy.skip_rag:
            hits = self.retrieve(question, policy.top_k)
        messages = self._messages(question, history or [], hits, incident_context, policy)
        return hits, messages, policy

    def _messages(
        self,
        question: str,
        history: list[dict[str, str]],
        hits: list[SearchHit],
        incident_context: str | None,
        policy: QueryPolicy,
    ) -> list[dict[str, str]]:
        context_blocks = [
            f"[{hit.title} | {hit.category} | score={hit.score:.3f}]\n{hit.content}"
            for hit in hits
        ]
        user = build_user_prompt(question, context_blocks, incident_context, policy)
        messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        if not policy.smalltalk:
            for turn in history[-4:]:
                role = turn.get("role")
                content = turn.get("content")
                if role in {"user", "assistant"} and content:
                    messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user})
        return messages

    def query(
        self,
        question: str,
        history: list[dict[str, str]] | None = None,
        incident_context: str | None = None,
    ) -> dict[str, Any]:
        hits, messages, policy = self.prepare(question, history, incident_context)
        answer = "".join(self._complete(messages, stream=False, max_tokens=policy.max_tokens))
        return {"answer": answer, "sources": [hit.__dict__ for hit in hits]}

    def query_stream(
        self,
        messages: list[dict[str, str]],
        max_tokens: int,
    ) -> Iterator[str]:
        yield from self._complete(messages, stream=True, max_tokens=max_tokens)

    def _complete(self, messages: list[dict[str, str]], stream: bool, max_tokens: int) -> Iterator[str]:
        if self._native_client is not None:
            self._native_client.settings.max_tokens = max_tokens
            self._native_client.settings.temperature = config.temperature
            if stream and hasattr(self._native_client, "complete_streaming_chat"):
                for chunk in self._native_client.complete_streaming_chat(messages):
                    if not getattr(chunk, "choices", None):
                        continue
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
                return
            result = self._native_client.complete_chat(messages)
            yield result.choices[0].message.content or ""
            return

        if self._openai_client is None:
            raise RuntimeError("Chat backend is not initialized")

        response = self._openai_client.chat.completions.create(
            model=self._model_id,
            messages=messages,
            temperature=config.temperature,
            max_tokens=max_tokens,
            stream=stream,
        )
        if stream:
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return
        yield response.choices[0].message.content or ""
