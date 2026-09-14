[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=fff)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=fff)](https://streamlit.io)
[![Foundry Local](https://img.shields.io/badge/Foundry%20Local-On--Device%20AI-0078D4?logo=microsoft&logoColor=fff)](https://foundrylocal.ai)
[![Phi-3.5 Mini](https://img.shields.io/badge/Model-Phi--3.5%20Mini-6B21A8)](https://azure.microsoft.com/products/phi-3)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Offline](https://img.shields.io/badge/Connectivity-Offline-brightgreen)]()

**[Readme_türkçe](README.md)**

# SOC Incident Copilot

A **local** triage assistant for SOC analysts. When an alert lands, it drafts an **English** answer to “what is this, how urgent is it, what should I do now, what evidence should I keep?”, grounded in playbooks, SOPs, and MITRE notes.

Case titles, IOCs, and host names do not go to the cloud. Generation runs **Phi-3.5 Mini** through **[Foundry Local](https://foundrylocal.ai)**. The UI is **Streamlit** (`http://localhost:8501`).

This repository is a Python counterpart of the offline RAG pattern in [leestott/local-rag](https://github.com/leestott/local-rag): documents are chunked, term-frequency (TF) vectors live in SQLite, and queries are ranked with cosine similarity. It is for training, demos, and labs — not live SOC orchestration.

## Contents

- [Scope](#scope)
- [Does and does not](#does-and-does-not)
- [Architecture](#architecture)
- [User interface](#user-interface)
- [Setup](#setup)
- [Usage](#usage)
- [Knowledge base](#knowledge-base)
- [Configuration](#configuration)
- [Project layout](#project-layout)
- [Tests](#tests)
- [Security](#security)
- [Documentation](#documentation)
- [License](#license)

## Scope

The copilot keeps three things together:

1. **Incident card** — title, severity, MITRE, assets, IOCs, analyst notes.
2. **RAG** — playbooks under `docs/`, PDFs, and sample MITRE cards.
3. **Local language model** — retrieved chunks plus card context, as a short or sectioned English draft.

The UI language can be Turkish or English. **The model always answers in English.** That is the language of Phi-3.5 Mini and of the knowledge base.

## Does and does not

| Does | Does not |
|---|---|
| Search local playbook, selectable-text PDF, and MITRE chunks | Scan a live network, query EDR, or collect logs |
| Mirror the card into JSON; when the card is complete, run an approved triage | Send commands to EDR, firewall, Active Directory, or mailboxes |
| Show the supporting snippet and a 0–1 similarity score | Produce exploits, malware, payloads, or attack recipes |
| Export card, chat, and sources as JSON | Claim a definitive CVE, attribution, or legal ruling |
| Index `.md` / `.txt` / `.pdf` uploads at runtime | Read scanned image-only PDFs (no OCR) |
| Skip RAG on greetings; use a smaller token budget on short questions | Multi-user identity, roles, or ticketing |

**You are the decision-maker.** Isolation, account burn, legal notice, and SOAR steps stay outside the copilot.

## Architecture

```
docs/  +  data/mitre_techniques.json
        ↓  ingest
   overlapping chunks (~200 units, 25 overlap)
        ↓
   TF vector + inverted index  →  data/rag.db
        ↓
 analyst question / approved card
        ↓
 candidate chunks → cosine ranking (top-k)
        ↓
 system prompt + chunks + card + question
        ↓
 Foundry Local → Phi-3.5 Mini  →  English answer
        ↓
 Sources panel + chat
```

1. `src/loaders.py` reads Markdown, text, PDF (`pypdf`), and MITRE JSON.
2. `src/chunker.py` splits the body with a sliding window; YAML front-matter, if present, becomes title and category.
3. `src/vector_store.py` writes each chunk’s TF vector into SQLite (WAL). At query time, shared-term candidates are scored with cosine similarity.
4. `src/query_policy.py` keeps greetings short and RAG-free; incident questions get a top-k and token budget.
5. `src/chat_engine.py` calls the model through the Foundry SDK (or an OpenAI-compatible fallback); answers stream.
6. `app.py` draws the three-column analyst workspace.

Retrieval is **TF + cosine**, not an embedding API. Common words are not down-weighted with IDF; that is enough for the demo playbooks and can weaken on a large, noisy corpus.

## User interface

| Area | Role |
|---|---|
| Left | Language, help, incident card, sample case, JSON export, upload, index list, MITRE catalog |
| Center | Quick-question buttons, chat, streaming answer |
| Right | Sources for the last query, active-case JSON, **Approve case and analyze** when the card is complete |

Choosing a sample case fills the card fields; you can edit them afterwards. The four center buttons send a chat question; they do not fill the card.

The top-right **Extra** menu belongs to Streamlit (Rerun, cache, screen recording). It is not an application feature.

## Setup

Development and demo were validated on **Windows 10/11**.

### Requirements

- Python 3.11+ (`Add Python to PATH`)
- [Foundry Local](https://foundrylocal.ai): `winget install Microsoft.FoundryLocal`
- First run downloads `phi-3.5-mini` (~2 GB). Foundry may use CUDA/NPU when present; otherwise CPU
- Browser: Edge or Chrome

If PowerShell blocks the virtual environment:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### First run

```powershell
git clone https://github.com/omrX61/soc-incident-copilot.git
cd soc-incident-copilot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.ingest
streamlit run app.py
```

UI: **http://localhost:8501**

For Windows GPU/NPU, if Foundry’s docs require it:

```powershell
pip install foundry-local-sdk-winml
```

`ingest` prints a chunk count per document and writes `data/rag.db` (not tracked in git). If the index is missing, Streamlit runs ingest on first load. The model loads on the first chat turn and may take several minutes.

## Usage

1. Pick a sample case on the left or fill the card by hand.
2. When every field is set, the approve button appears on the right; approval sends an English triage prompt into chat.
3. Type a free question. Short answers are the default.
4. **Sources** on the right shows which playbook chunk was retrieved.
5. **Export JSON** downloads the card, chat, and sources.

Do not put real IOCs, internal hosts, or usernames in screenshots or a public fork. Samples in this repo (`corp.example`, `hxxps://…`) are synthetic.

## Knowledge base

The repo includes phishing, ransomware, identity, lateral movement, C2, and evidence SOPs; public IR PDFs; 12 sample MITRE cards; and 12 synthetic cases.

Add documents by:

- uploading `.md` / `.txt` / `.pdf` in the UI and clicking **Index**, or
- placing files under `docs/` and using **Re-index entire docs/ folder** (`ingest(clear=True)`).

Markdown front-matter:

```markdown
---
title: Phishing BEC Playbook
category: Playbook
id: pb-phishing-bec
---

# Body
```

## Configuration

Defaults live in `src/config.py`. `.env.example` is a template; the app does not load a `.env` file by itself. Set process environment variables:

```powershell
$env:FOUNDRY_MODEL="phi-3.5-mini"
$env:CHUNK_SIZE="200"
$env:CHUNK_OVERLAP="25"
$env:TOP_K="5"
streamlit run app.py
```

| Variable | Meaning |
|---|---|
| `FOUNDRY_MODEL` | Default `phi-3.5-mini` |
| `FOUNDRY_APP_NAME` | Foundry app name |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | Chunk size and overlap |
| `TOP_K` | Policy may use 3 or 5 depending on the question |

Temperature is low (~0.2). Only the last few chat turns are sent to the model.

## Project layout

```
soc-incident-copilot/
├── app.py                      # Streamlit workspace
├── assets/                     # local app icon
├── docs/                       # playbooks, SOPs, PDFs
├── data/
│   ├── mitre_techniques.json   # sample ATT&CK cards
│   ├── sample_incidents.json   # sample cases
│   └── rag.db                  # after ingest (not in git)
├── src/
│   ├── loaders.py
│   ├── chunker.py
│   ├── vector_store.py
│   ├── ingest.py
│   ├── query_policy.py
│   ├── prompts.py
│   ├── chat_engine.py
│   └── i18n.py
├── tests/
├── SOC_Kılavuzu.md
├── SOC_Guide_EN.md
└── README.md
```

## Tests

They do not call the model; they run without Foundry:

```powershell
python -m pytest tests -q
```

Coverage: chunking, vector store, query policy, repeated-answer trimming.

## Security

- The system prompt forbids exploit and payload generation and asks the model not to invent IOCs or CVEs.
- Uploaded filenames cannot escape `docs/`.
- Do not bind Streamlit to `0.0.0.0` on the internet; there is no authentication.
- Do not publish company playbooks in a public fork. Third-party PDFs keep their own license / TLP terms.

## Documentation

| File | Contents |
|---|---|
| [`SOC_Guide_EN.md`](SOC_Guide_EN.md) | Full English walkthrough, install to analyst flow |
| [`SOC_Kılavuzu.md`](SOC_Kılavuzu.md) | The same guide in Turkish |
| [`README.md`](README.md) | Turkish version of this page |

## License

MIT. Parts of the RAG design are adapted from [leestott/local-rag](https://github.com/leestott/local-rag) (MIT).
