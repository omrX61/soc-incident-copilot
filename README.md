# SOC Incident Copilot

Yerel, çevrim dışı bir SOC Incident Copilot.
Belgeler parçalanır, TF vektörleri SQLite içinde saklanır, sorgu anında kosinüs benzerliği ile geri getirilir.
Ve yanıt **Foundry Local** üzerindeki **Phi-3.5 Mini** ile üretilir. Arayüz **Streamlit** üzerindedir.

## Mimari

1. `docs/` altındaki Markdown, PDF ve `data/mitre_techniques.json` okunur.
2. Metin ~200 token'lık örtüşmeli parçalara bölünür.
3. Her parça için terim frekansı (TF) hesaplanır ve `data/rag.db` içine yazılır.
4. Analist sorusu aynı şekilde vektörlenir; inverted index adayları daraltır, kosinüs benzerliğiyle sıralanır.
5. En iyi parçalar sistem promptuna eklenir; Phi-3.5 Mini yanıtı yerel üretir.

## Gereksinimler

- Python 3.11+
- [Foundry Local](https://foundrylocal.ai): `winget install Microsoft.FoundryLocal`
- İlk çalıştırmada `phi-3.5-mini` modeli indirilir (~2 GB)

## Komutlar

```powershell
cd soc-incident-copilot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.ingest
streamlit run app.py
```

Windows GPU/NPU için gerekirse: `pip install foundry-local-sdk-winml`

Arayüz: http://localhost:8501

Kullanıcı kılavuzu: [`SOC_Kılavuzu.md`](SOC_Kılavuzu.md) / [`SOC_Guide_EN.md`](SOC_Guide_EN.md)

## Dizinler

```
soc-incident-copilot/
├── app.py
├── assets/				  # favicon
├── docs/                 # playbook, SOP, PDF kaynaklar
├── data/                 # MITRE JSON, örnek vakalar, rag.db
├── src/                  # chunker, vector store, ingest, chat engine
└── tests/
```
