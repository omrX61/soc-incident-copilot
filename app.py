"""SOC Incident Copilot — Streamlit UI."""

from __future__ import annotations

import base64
import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from src.answer_cleanup import trim_repeated_content
from src.chunker import chunk_text, parse_front_matter
from src.config import ROOT, config
import importlib

from src import i18n as i18n_mod

importlib.reload(i18n_mod)
from src.i18n import QUICK_COUNT, QUICK_INCIDENTS, UI
from src.ingest import ingest

def ui_labels(lang: str) -> dict:
    text = dict(UI.get("en") or {})
    text.update(UI.get(lang) or {})
    text.setdefault("approve_case", "Approve case and analyze")
    text.setdefault("approve_hint", "Fill every Incident card field to reveal the approve button.")
    text.setdefault("approve_ready", "Card complete. Approval sends this case to the copilot.")
    text.setdefault("help_title", "How to use")
    text.setdefault("help_body", "See SOC_Kılavuzu.md / SOC_Guide_EN.md")
    return text

LOGO_PATH = ROOT / "assets" / "soc_incident_copilot_icon.png"
SEVERITY_OPTIONS = ["Informational", "Low", "Medium", "High", "Critical"]


def logo_src() -> str:
    if not LOGO_PATH.exists():
        return ""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def apply_sample_case() -> None:
    selected = st.session_state.get("card_sample")
    incidents = load_json(config.incidents_path)
    match = next((item for item in incidents if item["title"] == selected), None)
    if not match:
        return
    st.session_state.card_title = match.get("title", "")
    severity = match.get("severity", "Informational")
    st.session_state.card_severity = severity if severity in SEVERITY_OPTIONS else "Informational"
    st.session_state.card_mitre = match.get("mitre", "")
    st.session_state.card_assets = match.get("assets", "")
    st.session_state.card_iocs = "\n".join(match.get("iocs", []))
    st.session_state.card_notes = match.get("notes", "")

st.set_page_config(
    page_title="SOC Incident Copilot",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_json(path: Path) -> list | dict:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def format_incident_card(card: dict) -> str:
    iocs = ", ".join(card.get("iocs", [])) or "none listed"
    return (
        f"Title: {card.get('title')}\n"
        f"Severity: {card.get('severity')}\n"
        f"MITRE: {card.get('mitre')}\n"
        f"Assets: {card.get('assets')}\n"
        f"IOCs: {iocs}\n"
        f"Notes: {card.get('notes', '')}"
    )


def incident_card_complete(card: dict) -> bool:
    return all(
        [
            str(card.get("title") or "").strip(),
            str(card.get("severity") or "").strip(),
            str(card.get("mitre") or "").strip(),
            str(card.get("assets") or "").strip(),
            bool(card.get("iocs")),
            str(card.get("notes") or "").strip(),
        ]
    )


def case_analysis_prompt(card: dict) -> str:
    return (
        "Analyze this SOC incident card and produce a concise English triage.\n\n"
        f"{format_incident_card(card)}\n\n"
        "Cover likely incident type, severity justification, immediate containment, "
        "evidence to collect, and remaining gaps. Use retrieved playbooks when relevant."
    )


def case_filename(title: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", (title or "incident").strip()).strip("-")
    return f"{(slug or 'incident')[:72]}.json"


def pick_quick_incidents(lang: str) -> list[str]:
    pool = QUICK_INCIDENTS[lang]
    return random.sample(pool, k=min(QUICK_COUNT, len(pool)))


ENGINE_REVISION = 4


@st.cache_resource(show_spinner=False)
def get_engine(revision: int = ENGINE_REVISION):
    from src.chat_engine import ChatEngine

    engine = ChatEngine()
    engine.init()
    return engine


def resolve_engine(t: dict):
    engine = st.session_state.get("engine")
    if engine is None or not hasattr(engine, "prepare"):
        with st.spinner(t["loading_model"]):
            engine = get_engine(ENGINE_REVISION)
        st.session_state.engine = engine
    return engine


def ensure_index(t: dict) -> None:
    if not config.db_path.exists() or config.db_path.stat().st_size < 64:
        with st.spinner(t["indexing"]):
            ingest(clear=True)


def open_store():
    from src.vector_store import VectorStore

    if "engine" in st.session_state:
        return st.session_state.engine.get_store()
    return VectorStore(config.db_path)


def index_uploaded_file(uploaded, t: dict) -> dict:
    from src.loaders import SourceDoc, load_pdf

    raw_name = Path(uploaded.name).name
    safe_name = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in raw_name)
    dest = (config.docs_dir / safe_name).resolve()
    if not str(dest).startswith(str(config.docs_dir.resolve())):
        raise ValueError(t["bad_filename"])
    dest.write_bytes(uploaded.getbuffer())

    suffix = dest.suffix.lower()
    if suffix == ".pdf":
        source = load_pdf(dest)
    elif suffix in {".md", ".txt"}:
        text = dest.read_text(encoding="utf-8", errors="replace")
        meta, body = parse_front_matter(text)
        source = SourceDoc(
            meta.get("id") or dest.stem,
            meta.get("title") or dest.stem,
            meta.get("category") or "Uploaded",
            body,
            str(dest),
        )
    else:
        raise ValueError(t["upload_types"])

    store = open_store()
    store.remove_by_doc_id(source.doc_id)
    chunks = chunk_text(source.body, config.chunk_size, config.chunk_overlap)
    for i, chunk in enumerate(chunks):
        store.insert(source.doc_id, source.title, source.category, i, chunk)
    return {"title": source.title, "chunks": len(chunks), "doc_id": source.doc_id}


def render_sources(hits: list[dict], t: dict) -> None:
    if not hits:
        st.caption(t["no_sources"])
        return
    for hit in hits:
        with st.expander(f"{hit['title']}  ·  {hit['score']:.3f}  ·  {hit['category']}"):
            st.write(hit["content"])


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #0b1220; }
        header[data-testid="stHeader"] { background: #0b1220; }
        .stAppDeployButton,
        div[data-testid="stAppDeployButton"] { display: none !important; }
        button[data-testid="stMainMenuButton"] {
            min-width: 57px !important;
            height: 28px !important;
            padding: 0 8px !important;
            border-radius: 8px !important;
            font-size: 14px !important;
            line-height: 14px !important;
            font-weight: 400 !important;
            color: #e8eef7 !important;
        }
        button[data-testid="stMainMenuButton"] svg { display: none !important; }
        button[data-testid="stMainMenuButton"]::after {
            content: "Extra";
            font-size: 14px;
            line-height: 14px;
            font-weight: 400;
            color: #e8eef7;
        }
        .block-container { padding-top: 3.4rem !important; }
        .soc-brand { display: flex; flex-direction: column; align-items: center; gap: 0.45rem; margin: 0.2rem 0 1rem; }
        .soc-brand img { width: 74px; height: 74px; object-fit: cover; border-radius: 20px; box-shadow: 0 8px 22px rgba(0, 0, 0, 0.28); }
        .soc-brand h1 { margin: 0; color: #e8f1ff; font-size: 1.18rem; line-height: 1.2; text-align: center; letter-spacing: -0.02em; }
        div[data-testid="stChatMessage"] {
            background: #121a2b;
            border: 1px solid #223049;
            border-radius: 12px;
        }
        .answer-loading {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            min-height: 1.6rem;
            color: #c5d4ea;
            font-size: 0.98rem;
        }
        .answer-loading .orb {
            width: 13px;
            height: 13px;
            border-radius: 50%;
            background: #f5a524;
            box-shadow: 0 0 0 0 rgba(245, 165, 36, 0.55);
            animation: orb-pulse 1.1s ease-in-out infinite;
        }
        .answer-loading .ellipsis span {
            animation: ellipsis-blink 1.2s infinite;
            font-weight: 700;
            color: #f5a524;
        }
        .answer-loading .ellipsis span:nth-child(2) { animation-delay: 0.2s; }
        .answer-loading .ellipsis span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes orb-pulse {
            0%, 100% { transform: scale(0.72); opacity: 0.45; box-shadow: 0 0 0 0 rgba(245, 165, 36, 0.0); }
            50% { transform: scale(1.18); opacity: 1; box-shadow: 0 0 0 8px rgba(245, 165, 36, 0); }
        }
        @keyframes ellipsis-blink {
            0%, 20% { opacity: 0.15; }
            50% { opacity: 1; }
            100% { opacity: 0.15; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_theme()

    if "ui_lang" not in st.session_state:
        st.session_state.ui_lang = "tr"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_sources" not in st.session_state:
        st.session_state.last_sources = []
    if "engine_error" not in st.session_state:
        st.session_state.engine_error = None
    if "quick_incidents" not in st.session_state:
        st.session_state.quick_incidents = pick_quick_incidents(st.session_state.ui_lang)
        st.session_state.quick_lang = st.session_state.ui_lang
    stale = st.session_state.get("engine")
    if stale is not None and not hasattr(stale, "prepare"):
        st.session_state.pop("engine", None)
        st.session_state.engine_error = None

    t = ui_labels(st.session_state.ui_lang)
    ensure_index(t)

    techniques = load_json(config.mitre_path)
    incidents = load_json(config.incidents_path)

    with st.sidebar:
        icon = logo_src()
        st.markdown(
            f"""
            <div class="soc-brand">
                {'<img src="' + icon + '" alt="SOC Incident Copilot shield icon" />' if icon else ""}
                <h1>SOC Incident Copilot</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(t["caption"])
        with st.expander(t["help_title"]):
            st.markdown(t["help_body"])
        lang_label = st.radio(
            t["language"],
            options=["tr", "en"],
            format_func=lambda code: "Türkçe" if code == "tr" else "English",
            horizontal=True,
            key="ui_lang",
        )
        t = ui_labels(lang_label)
        if st.session_state.get("quick_lang") != lang_label:
            st.session_state.quick_incidents = pick_quick_incidents(lang_label)
            st.session_state.quick_lang = lang_label
        st.divider()

        st.subheader(t["incident_card"])
        sample_titles = [t["empty"]] + [item["title"] for item in incidents]
        st.selectbox(
            t["sample_case"],
            sample_titles,
            key="card_sample",
            on_change=apply_sample_case,
        )
        title = st.text_input(t["alert_title"], key="card_title")
        severity = st.selectbox(t["severity"], SEVERITY_OPTIONS, key="card_severity")
        mitre = st.text_input(t["mitre"], key="card_mitre")
        assets = st.text_input(t["assets"], key="card_assets")
        iocs = st.text_area(t["iocs"], height=80, key="card_iocs")
        notes = st.text_area(t["notes"], height=80, key="card_notes")

        incident_card = {
            "title": title,
            "severity": severity,
            "mitre": mitre,
            "assets": assets,
            "iocs": [x.strip() for x in iocs.splitlines() if x.strip()],
            "notes": notes,
        }
        export_payload = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "incident": incident_card,
            "conversation": st.session_state.messages,
            "sources": st.session_state.last_sources,
        }
        st.download_button(
            label=t["export_json"],
            data=json.dumps(export_payload, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name=case_filename(title),
            mime="application/json",
            use_container_width=True,
        )

        st.divider()
        st.subheader(t["knowledge_base"])
        uploaded = st.file_uploader(t["upload"], type=["md", "txt", "pdf"])
        if uploaded and st.button(t["index"]):
            try:
                result = index_uploaded_file(uploaded, t)
                st.success(t["added"].format(title=result["title"], chunks=result["chunks"]))
            except Exception as exc:
                st.error(str(exc))
        if st.button(t["reindex"]):
            with st.spinner(t["reindexing"]):
                summary = ingest(clear=True)
            if "engine" in st.session_state:
                st.session_state.engine.get_store()._invalidate_cache()
            st.success(
                t["reindexed"].format(documents=summary["documents"], chunks=summary["chunks"])
            )

        docs = open_store().list_docs()
        st.caption(t["indexed"].format(n=len(docs)))
        for doc in docs:
            st.write(f"- {doc['title']} ({doc['chunks']})")

        st.divider()
        st.subheader(t["mitre_catalog"])
        for tech in techniques:
            st.markdown(f"**{tech['id']}** {tech['name']}  \n*{tech['tactic']}*")

    left, right = st.columns([1.35, 0.65], gap="large")
    with left:
        st.header(t["workspace"])
        st.write(t["workspace_blurb"])

        for prompt in st.session_state.quick_incidents:
            if st.button(prompt, use_container_width=True):
                st.session_state.pending_prompt = prompt

        if st.session_state.engine_error:
            st.error(st.session_state.engine_error)

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_text = st.chat_input(t["chat_placeholder"])
        pending = st.session_state.pop("pending_prompt", None)
        query = user_text or pending

        if query:
            st.session_state.messages.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)

            try:
                st.session_state.engine_error = None
                engine = resolve_engine(t)
                history = st.session_state.messages[:-1]
                incident_context = format_incident_card(incident_card) if incident_card.get("title") else None
                hits, messages, policy = engine.prepare(query, history, incident_context)
                st.session_state.last_sources = [hit.__dict__ for hit in hits]
                loading_html = (
                    "<div class='answer-loading'>"
                    "<span class='orb'></span>"
                    f"<span>{t['answering']}</span>"
                    "<span class='ellipsis'><span>.</span><span>.</span><span>.</span></span>"
                    "</div>"
                )
                with st.chat_message("assistant"):
                    box = st.empty()
                    box.markdown(loading_html, unsafe_allow_html=True)
                    chunks: list[str] = []
                    answer = ""
                    for token in engine.query_stream(messages, policy.max_tokens):
                        chunks.append(token)
                        current = "".join(chunks)
                        trimmed = trim_repeated_content(current)
                        box.markdown(trimmed)
                        answer = trimmed
                        if trimmed != current:
                            break
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as exc:
                st.session_state.engine_error = str(exc)
                st.error(str(exc))

    with right:
        st.subheader(t["sources"])
        render_sources(st.session_state.last_sources, t)
        st.subheader(t["active_case"])
        st.json(incident_card)
        if incident_card_complete(incident_card):
            st.caption(t["approve_ready"])
            if st.button(t["approve_case"], type="primary", use_container_width=True):
                st.session_state.pending_prompt = case_analysis_prompt(incident_card)
                st.rerun()
        else:
            st.caption(t["approve_hint"])
        if "engine" in st.session_state:
            st.caption(
                f"Model: {config.model} · backend: {st.session_state.engine._backend} · "
                f"chunks: {st.session_state.engine.get_store().count()}"
            )


if __name__ == "__main__":
    main()
