[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=fff)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=fff)](https://streamlit.io)
[![Foundry Local](https://img.shields.io/badge/Foundry%20Local-On--Device%20AI-0078D4?logo=microsoft&logoColor=fff)](https://foundrylocal.ai)
[![Phi-3.5 Mini](https://img.shields.io/badge/Model-Phi--3.5%20Mini-6B21A8)](https://azure.microsoft.com/products/phi-3)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Offline](https://img.shields.io/badge/Connectivity-Offline-brightgreen)]()

**[Readme_english](README_EN.md)**

# SOC Incident Copilot

Yerel, çevrimdışı bir **SOC Incident Copilot**. Playbook, SOP ve MITRE notlarından taslak triage üretir. Vaka metni buluta gitmez; model **[Foundry Local](https://foundrylocal.ai)** üzerinde **Phi-3.5 Mini** ile çalışır. Arayüz **Streamlit**.

Mimari, [leestott/local-rag](https://github.com/leestott/local-rag) örneğindeki çevrimdışı RAG deseninin Python karşılığıdır: belgeler parçalanır, terim frekansı vektörleri SQLite’da tutulur, sorgu kosinüs benzerliği ile geri getirilir.

## Yapar / yapmaz

| Yapar | Yapmaz |
|---|---|
| Playbook, PDF ve MITRE parçalarını yerelde arar | Gerçek ağı tarama |
| Incident card’ı JSON’a yansıtır; onay sonrası kısa triage üretir | EDR, firewall veya AD’ye komut |
| Kaynak parçalarını ve benzerlik skorunu gösterir | Exploit, malware veya payload üretme |
| Vakayı JSON olarak indirir | Kesin CVE veya hukuki hüküm iddiası |
| `.md` / `.txt` / `.pdf` yükleyip indeksler | OCR’siz taranmış PDF okuma |
| Arayüzü TR/EN gösterir; model İngilizce yazar | Çok kullanıcılı giriş veya vaka verisini buluta gönderme |

Copilot karar verici değildir. İzolasyon, hesap kilidi ve hukuki adım analiste aittir.

## Mimari

1. `docs/` altındaki Markdown, PDF ve `data/mitre_techniques.json` okunur.
2. Metin ~200 birimlik örtüşmeli parçalara bölünür.
3. Her parça için TF hesaplanır ve `data/rag.db` içine yazılır.
4. Analist sorusu vektörlenir; inverted index adayları daraltır, kosinüs sıralar.
5. En iyi parçalar prompta eklenir; Phi-3.5 Mini yanıtı yerelde üretir.

## Kurulum

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
- İlk çalıştırmada `phi-3.5-mini` indirilir (~2 GB)

Arayüz: http://localhost:8501

Windows GPU/NPU için gerekirse: `pip install foundry-local-sdk-winml`

## Dizinler

```
soc-incident-copilot/
├── app.py                 # Streamlit arayüzü
├── assets/                # uygulama ikonu
├── docs/                  # playbook, SOP, PDF
├── data/                  # MITRE JSON, örnek vakalar, rag.db
├── src/                   # chunker, vector store, ingest, chat engine
└── tests/
```

Kullanım (kurulumdan analist akışına): [`SOC_Kılavuzu.md`](SOC_Kılavuzu.md)

## Lisans

MIT. RAG tasarımının bir kısmı [leestott/local-rag](https://github.com/leestott/local-rag) (MIT) örnek alınarak uyarlanmıştır.
