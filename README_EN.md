[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=fff)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=fff)](https://streamlit.io)
[![Foundry Local](https://img.shields.io/badge/Foundry%20Local-On--Device%20AI-0078D4?logo=microsoft&logoColor=fff)](https://foundrylocal.ai)
[![Phi-3.5 Mini](https://img.shields.io/badge/Model-Phi--3.5%20Mini-6B21A8)](https://azure.microsoft.com/products/phi-3)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Offline](https://img.shields.io/badge/Connectivity-Offline-brightgreen)]()

**[Readme_türkçe](README.md)**

# SOC Incident Copilot

A local, offline **SOC Incident Copilot**. It drafts triage from playbooks, SOPs, and MITRE notes. Case text does not go to the cloud; the model runs **Phi-3.5 Mini** through **[Foundry Local](https://foundrylocal.ai)**. The UI is **Streamlit**.

The architecture is a Python counterpart of the offline RAG pattern in [leestott/local-rag](https://github.com/leestott/local-rag): documents are chunked, term-frequency vectors live in SQLite, and queries are ranked with cosine similarity.

## Does / does not

| Does | Does not |
|---|---|
| Search local playbook, PDF, and MITRE chunks | Scan a live network |
| Mirror the incident card to JSON; after approval, draft a short triage | Send commands to EDR, firewall, or AD |
| Show source snippets and similarity scores | Produce exploits, malware, or payloads |
| Export the case as JSON | Claim a definitive CVE or legal ruling |
| Index uploaded `.md` / `.txt` / `.pdf` files | Read scanned image-only PDFs (no OCR) |
| Show the UI in TR/EN; the model always answers in English | Multi-user login or sending case data to the cloud |

The copilot is not a decision-maker. Isolation, account lockout, and legal steps stay with the analyst.

## Architecture

1. Markdown, PDFs under `docs/`, and `data/mitre_techniques.json` are read.
2. Text is split into overlapping ~200-unit chunks.
3. TF is computed per chunk and written to `data/rag.db`.
4. The analyst question is vectorized; an inverted index narrows candidates; cosine similarity ranks them.
5. Top chunks are added to the prompt; Phi-3.5 Mini generates the answer locally.

## Setup

```powershell
git clone https://github.com/omrX61/soc-incident-copilot.git
cd soc-incident-copilot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.ingest
streamlit run app.py
```

- Python 3.11+
- Foundry Local: `winget install Microsoft.FoundryLocal`
- First run downloads `phi-3.5-mini` (~2 GB)

UI: http://localhost:8501

For Windows GPU/NPU if needed: `pip install foundry-local-sdk-winml`

## Layout

```
soc-incident-copilot/
├── app.py                 # Streamlit UI
├── assets/                # app icon
├── docs/                  # playbooks, SOPs, PDFs
├── data/                  # MITRE JSON, sample cases, rag.db
├── src/                   # chunker, vector store, ingest, chat engine
└── tests/
```

Full walkthrough: [`SOC_Guide_EN.md`](SOC_Guide_EN.md)

## License

MIT. Parts of the RAG design are adapted from [leestott/local-rag](https://github.com/leestott/local-rag) (MIT).
