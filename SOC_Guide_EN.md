# SOC Incident Copilot — A Complete Guide

A local, offline **SOC Incident Copilot**. It generates a draft triage for a Security Operations Center (SOC) analyst from playbooks, SOPs, and MITRE notes. Case data never leaves your machine; the model runs on your own computer.

This document is written for both a reader who has **never seen a SOC** and an analyst who **reviews alerts and opens cases** for a living.

**Important boundary:** the Copilot is not a decision-maker. It does not send commands to an EDR, does not lock accounts, and does not produce exploit or attack instructions. The English text it produces is a draft — approval, isolation, and legal steps are yours to take.

---

## 1. What is this project?

When an alert lands in a SOC, the analyst wants to know: *What is this? How urgent is it? What should I do right now? What evidence should I preserve?*

SOC Incident Copilot answers these questions in short English responses, drawing on **the documents you upload** (RAG) and a locally running **Phi-3.5 Mini** model.

| Does | Does not |
|---|---|
| Finds relevant playbook / PDF / MITRE snippets | Scan a real network |
| Reflects the incident card into JSON | Send commands to EDR, firewall, or AD |
| Triages the card after approval | Produce malware / exploits / payloads |
| Exports the case as JSON | Claim a "definitive CVE / legal ruling" |
| Gives short or sectioned drafts in chat | Send case data to the cloud |

The interface language can be Turkish or English. **The model always writes in English.** This is the language of Phi-3.5 Mini and the knowledge base; it is a deliberate design choice.

---

## 2. Why local?

- **Privacy:** the case title, IOCs, and host names never leave Foundry Local (your own machine).
- **Demo / training:** it can be shown without internet access or on a restricted network.
- **Auditability:** a **Sources** panel next to each answer shows which document snippet was used and its similarity score.

---

## 3. Glossary

| Term | Plain language |
|---|---|
| **SOC** | The company's security monitoring team. An alert comes in, someone looks at it. |
| **Incident / case** | A "something may have gone wrong" record: phishing, ransomware, a stolen account. |
| **Triage** | The first look: what is this, how urgent is it, what do we do now. |
| **Severity** | Urgency level: Informational → Low → Medium → High → Critical. |
| **MITRE ATT&CK** | A catalog of attacker behaviors. `T1566` is phishing, `T1486` is ransomware encryption. |
| **IOC** | An indicator: a malicious domain, hash, IP, or filename. |
| **Playbook** | Instructions of the form "when this alert fires, follow these steps." |
| **Containment** | Stopping the spread: isolation, session revocation, blocking a URL. |
| **RAG** | Pulling the answer from your own documents instead of the model's memorized knowledge. |
| **Phi-3.5 Mini** | Microsoft's small language model; it runs offline here. |
| **Foundry Local** | The Microsoft runtime layer that loads the model locally. |
| **Sources** | The document snippets an answer is based on, with a 0–1 similarity score. |
| **Ingest** | Reading `docs/` and the MITRE JSON and writing them into the `data/rag.db` index. |
| **TF / cosine** | The search method used in this project: a term-frequency vector plus cosine similarity (no embedding-vector API is used). |

---

## 4. Architecture (a brief overview)

```
docs/  +  data/mitre_techniques.json
        ↓  (ingest)
   chunking (~200 words, with overlap)
        ↓
   TF vector + inverted index  →  data/rag.db
        ↓
 analyst's question / approved card
        ↓
 similar chunks (top-k)
        ↓
 system prompt + chunks + question
        ↓
 Foundry Local → Phi-3.5 Mini  →  English answer
        ↓
 Sources panel + chat history
```

1. Markdown, PDF, and MITRE JSON files are read (`src/loaders.py`). PDF text is extracted with **pypdf**.
2. Text is split into overlapping chunks of about 200 units (`src/chunker.py`).
3. Each chunk is written to SQLite (`src/vector_store.py`).
4. The question is vectorized; candidates are narrowed down and ranked by cosine similarity.
5. The best chunks are added to the prompt; `src/chat_engine.py` calls the model.
6. `app.py` renders the Streamlit interface.

For short exchanges like greetings or thanks, RAG is **turned off** (so an unnecessary playbook isn't pulled in).

---

## 5. Requirements

- **Windows 10/11** (development and the demo were done in this environment)
- **Python 3.11+** ([python.org](https://www.python.org/downloads/) — check "Add Python to PATH" during install)
- **[Foundry Local](https://foundrylocal.ai)**
  `winget install Microsoft.FoundryLocal`
- **phi-3.5-mini** is downloaded on first run (roughly **~2 GB**). The CUDA variant is used if a GPU is present, otherwise the CPU variant.
- Browser: Edge / Chrome. Interface: `http://localhost:8501`
- Optional: an NVIDIA GPU + Foundry's CUDA execution provider (for faster generation)

On macOS / Linux, Foundry Local and package names may differ; this guide is Windows-focused.

---

## 6. Installation (step by step)

Open PowerShell. If the execution policy blocks the virtual environment for the first time:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Go to the project folder (use your own path):

```powershell
cd C:\Users\<username>\soc-incident-copilot
```

Virtual environment and dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` summary:

| Package | Purpose |
|---|---|
| `streamlit` | Web interface |
| `pypdf` | Reading and indexing playbook PDFs |
| `openai` | Foundry's OpenAI-compatible client path |
| `foundry-local-sdk` | Local model manager and chat |
| `pytest` | Unit tests |

If needed, for Windows GPU/NPU (see Foundry's documentation):

```powershell
pip install foundry-local-sdk-winml
```

Index the knowledge base for the first time:

```powershell
python -m src.ingest
```

The chunk count for each document is printed to the terminal. When it finishes, `data/rag.db` is created.

Start the app:

```powershell
streamlit run app.py
```

If the browser doesn't open `http://localhost:8501` automatically, type the address in manually. To stop it, press `Ctrl+C` in the terminal.

### 6.1 Optional environment variables

You can copy `.env.example` to `.env` (`.env` is not tracked by git). Defaults live in `src/config.py`:

| Variable | Meaning |
|---|---|
| `FOUNDRY_MODEL` | Default `phi-3.5-mini` |
| `FOUNDRY_APP_NAME` | Foundry application name |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | Chunk size |
| `TOP_K` | Default number of chunks to retrieve (the policy may set this to 3 or 5 depending on the question) |

---

## 7. What do you see on first launch?

1. A dark theme, a sidebar on the left, chat in the center, and sources on the right.
2. On the first message, loading the model can take **a few minutes**. An orange dot with "Generating answer" is shown.
3. There's an arrow at the top left to collapse the sidebar.
4. There's an **Extra** menu at the top right.

The **How to use** section in the sidebar is a short reminder. This document is the full text; the repo's `KULLANIM_KILAVUZU.md` is the in-app summary guide.

---

## 8. The three columns of the screen

### 8.1 Left — Incident card

The analyst's official form. As it's filled in, the **Active case** JSON on the right updates simultaneously.

| Field | What to write | Example |
|---|---|---|
| Sample case | A ready-made scenario | VIP mailbox AiTM phishing |
| Alert / case title | A short name | Finance share encryption |
| Severity | Urgency | High / Critical |
| MITRE | Technique code(s) | T1486, T1021.001 |
| Affected assets | Host / user | FILESRV01, j.hale |
| IOC list | One indicator per line | `ransom note.txt` |
| Analyst notes | What you observed | VSS deleted, backup job failed |

**Approval:** once the title, severity, MITRE, asset, at least one IOC, and notes are **all** filled in, the **Approve case and analyze** button appears on the right. There's no approval for a half-filled card, and no automatic analysis without approval.

Approval sends an English prompt to the chat that's roughly: *analyze* the card, covering the headings *incident type, severity, containment, evidence, gaps*.

**Export as JSON:** the card + chat + sources. For attaching to a ticket or for backup. There is no PDF export.

**Knowledge base:** upload `.md` / `.txt` / `.pdf` to index a single document. **Reindex the entire docs/ folder** reprocesses everything from scratch (`ingest(clear=True)`).

**MITRE catalog:** sample technique cards. Clicking one does not start a chat; it's a reference.

### 8.2 Center — Incident workspace

- Four **quick incident** buttons: ready-made English/Turkish questions. They change randomly when the **page is refreshed (F5)**; Extra → Rerun re-runs the script without clearing the chat, and generally does **not** change these four buttons.
- Bottom box: free-form question.
- The answer is in English.

### 8.3 Right — Sources and Active case

- **Sources:** the chunks pulled in for this answer. Scores are 0–1; higher means more relevant.
- "No matching source": either it's a greeting (RAG is off) or no words matched.
- **Active case:** the JSON form of the card on the left.

### 8.4 Extra menu (top right)

This is Streamlit's own menu, not a Copilot command.

| Item | What it does |
|---|---|
| **Rerun** | Re-runs `app.py` from scratch. The chat, card, and loaded model are generally **preserved**. |
| **Auto rerun** | Automatically re-runs the script when a source file changes. |
| **Clear cache** | Clears Streamlit's `@st.cache_resource` caches. Since the engine is also kept in the session in this app, **Foundry usually isn't reloaded**. The chat is not cleared. `rag.db` remains on disk. |
| **Print / Record screen** | Browser printing or screen recording. |

---

## 9. I know nothing about SOC — a 10-minute trial

1. Leave the interface in **Turkish**. The answer will still be in English.
2. Pick a **Sample case** on the left (e.g., VIP mailbox phishing).
3. Fill in the empty fields with the sample values (the training IOCs are enough).
4. Watch the JSON on the right fill in.
5. **Approve the case and analyze it.**
6. Look at the English triage in the center, and check on the right which PDF/playbook snippet was used.
7. If you'd like, **export it as JSON.**

This does not mean "I carried out an attack." It's a synthetic scenario.

Try this in the chat:

```text
Password spray followed by a successful service-account logon. How should I proceed?
```
---

## 10. Recommended workflow for an analyst

1. Enter the alert into the card (title, severity, MITRE, host, IOC, notes).
2. Visually review the Active case JSON.
3. Approve it → triage + sources.
4. Narrow it down in chat if needed: *containment only*, *evidence to collect for T1003.001*.
5. Attach the JSON to the ticket.
6. You make the isolation / account lockout decision.

---

## 11. Effective questions (no hidden slash commands)

The length depends on **the text**, not on whether the card is filled in:

| What you write | What to expect |
|---|---|
| `How should I proceed?` + a sentence about the case | Short bullet points |
| Only the `Analyze:` prefix | **Not** a magic template; usually still bullet points |
| `Triage … Cover incident type, severity, immediate containment, evidence, remaining gaps.` | A sectioned triage close to what the approval button produces |
| `Playbook detail for T1486 ransomware on a file server.` | A sectioned playbook draft |
| A MITRE code (`T1048`, `T1486`) | Improves the RAG hit rate |
| Card + **Approval** | The cover list is sent on your behalf |

---

## 12. Repository map — folders and files

```
soc-incident-copilot/
├── app.py                 # Streamlit interface (single entry point)
├── requirements.txt       # Python packages
├── pytest.ini             # test path
├── LICENSE                # MIT
├── README.md              # short setup guide
├── KULLANIM_KILAVUZU.md   # in-app summary guide
├── .env.example           # optional settings template
├── .gitignore
├── .streamlit/config.toml # port 8501, dark theme
├── assets/                # tab / brand icon
├── docs/                  # knowledge base (md + pdf)
├── data/                  # MITRE JSON, sample cards, rag.db
├── src/                   # engine
└── tests/                 # unit tests
```

**Not tracked** by git: `.venv/`, `.env`, `data/*.db` (generate the index on each machine with `python -m src.ingest`), `__pycache__/`.

### 12.1 Root files

| File | Purpose |
|---|---|
| `app.py` | Three-column UI, card, chat, approval, ingest buttons, theme, Extra/Deploy CSS |
| `requirements.txt` | pip dependencies |
| `LICENSE` | MIT; notes the local-rag adaptation |
| `README.md` | GitHub showcase: architecture + commands |
| `KULLANIM_KILAVUZU.md` | Short in-app guide |
| `.env.example` | Model name, chunk, port template |
| `pytest.ini` | `pythonpath = .`, tests live in `tests/` |

### 12.2 `src/` — the engine

| File | Purpose |
|---|---|
| `config.py` | Root path, model name, `docs/`, `data/rag.db`, chunk / top_k |
| `loaders.py` | md/txt/pdf/MITRE JSON → plain-text documents |
| `chunker.py` | Chunking, front matter, TF, cosine |
| `vector_store.py` | SQLite index and search |
| `ingest.py` | Bulk indexing. Run: `python -m src.ingest` |
| `chat_engine.py` | Foundry startup, retrieval, streaming |
| `query_policy.py` | Whether it's a greeting or short; token and top_k |
| `prompts.py` | System prompt (always in English) |
| `answer_cleanup.py` | Prevents the same heading from being printed twice |
| `i18n.py` | TR/EN labels, the quick-incident pool |

### 12.3 `docs/` — knowledge base

Sample markdown playbooks / SOPs:

| File | Topic |
|---|---|
| `soc-incident-handling-sop.md` | SOC incident-handling SOP |
| `ransomware-containment-playbook.md` | Ransomware containment |
| `phishing-bec-playbook.md` | Phishing / BEC |
| `lateral-movement-playbook.md` | Lateral movement |
| `identity-threat-runbook.md` | Identity threats |
| `c2-hunt-notes.md` | C2 hunting notes |
| `evidence-chain-of-custody.md` | Chain of custody |
| `log-source-coverage.md` | Log source coverage |
| `severity-escalation-matrix.md` | Severity / escalation |

PDFs (converted to text via ingest): public IR / NIST / IC3 / ransomware / phishing guides. To add a new PDF: drop the file into `docs/` → **reindex**.

### 12.4 `data/`

| File | Purpose |
|---|---|
| `mitre_techniques.json` | Sample ATT&CK techniques (not the full MITRE catalog) |
| `sample_incidents.json` | The "Sample case" list on the left |
| `rag.db` | Search index (generated locally, usually not in git) |
| `.gitkeep` | Keeps the empty `data/` folder present in git |

### 12.5 `tests/`

`test_chunker.py`, `test_vector_store.py`, `test_query_policy.py`, `test_answer_cleanup.py`. While in the virtual environment:

```powershell
python -m pytest tests -q
```

(the `pytest` package must be installed.)

### 12.6 `assets/` and `.streamlit/`

- `assets/soc_incident_copilot_icon.png` — the tab icon.
- `.streamlit/config.toml` — `headless`, port **8501**, dark color palette.

---

## 13. Common situations

| What you see | What it means | What to do |
|---|---|---|
| "Generating answer" + orange dot | The model is generating | Wait; the first load can be slow |
| Foundry singleton / already initialized | The model is already open in this process | Refresh the page; restart Streamlit if needed |
| Port 8501 in use | Another Streamlit instance is open | Ctrl+C in the old terminal, or use a different port |
| No source | RAG is off, or the match was weak | Use a MITRE code, "ransomware", or a host name |
| Asked in Turkish, got an English answer | By design | The interface language is menu-only |
| Clear cache didn't unload the model | The engine lives in the session | Close the Streamlit process |
| PDF "no selectable text" | It's a scanned image PDF | Use OCR'd text or a Markdown playbook |
| Activate.ps1 blocked | Execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |

---

## 14. Security and sharing (GitHub / LinkedIn)

- The sample IOCs are **for training purposes** (`corp.example`, `hxxps://…`).
- Do not put a real case, a real user, an internal IP, or a hash on screen, in JSON, or in a screenshot.
- If you use Extra → Record screen for a LinkedIn video, accept the browser permission; leave the left-hand card empty or filled with synthetic data during the recording.
- When pushing the repo to GitHub: **do not upload** `.env`, `.venv`, `rag.db`, or a company playbook. Comply with the licenses of public PDFs.
- License: **MIT**. Third-party PDFs have their own license / TLP markings; credit the source when republishing.

---

## 15. Sharing on GitHub

The `README.md` in the repo root already contains a short setup guide. You can link this document (`SOC_Kılavuzu.md`) from the README.

Suggested README items: what it is, local / offline, a screenshot, install commands, a "does not" list, license.

```text
git clone https://github.com/<org>/soc-incident-copilot.git
cd soc-incident-copilot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.ingest
streamlit run app.py
```

---

## 16. Developer notes

- The last few turns of chat history are sent to the model.
- `@st.cache_resource` holds the Foundry instance; a new cache key is used when ENGINE_REVISION changes.
- Temperature is low (~0.2); the same question produces similar output, though not necessarily identical.
- Tests don't call the model; `pytest` can pass without Foundry.

---

## 17. Sources and acknowledgments

- [Foundry Local](https://foundrylocal.ai)
- [Phi-3.5 Mini](https://azure.microsoft.com/en-us/products/phi-3)
- MITRE ATT&CK® — technique IDs are sampled for training purposes
- Public IR / NIST / IC3 PDFs are in `docs/`, under the terms of their respective publishing organizations

---

*SOC Incident Copilot — a local triage assistant. You are the decision-maker.*
