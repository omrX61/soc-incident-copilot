[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=fff)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=fff)](https://streamlit.io)
[![Foundry Local](https://img.shields.io/badge/Foundry%20Local-On--Device%20AI-0078D4?logo=microsoft&logoColor=fff)](https://foundrylocal.ai)
[![Phi-3.5 Mini](https://img.shields.io/badge/Model-Phi--3.5%20Mini-6B21A8)](https://azure.microsoft.com/products/phi-3)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Offline](https://img.shields.io/badge/Connectivity-Offline-brightgreen)]()

**[Readme_english](README_EN.md)**

# SOC Incident Copilot

SOC analistine, **kendi makinesinde** çalışan bir triaj asistanı. Alarm düşünce “bu ne, ne kadar acil, şimdi ne yapmalıyım, hangi kanıtı saklamalıyım?” sorularına playbook, SOP ve MITRE notlarından dayanaklı **İngilizce taslak** üretir.

Vaka başlığı, IOC ve host adı buluta gitmez. Üretim **[Foundry Local](https://foundrylocal.ai)** üzerindeki **Phi-3.5 Mini** ile yapılır; arayüz **Streamlit** (`http://localhost:8501`).

Bu depo, [leestott/local-rag](https://github.com/leestott/local-rag) örneğindeki çevrimdışı RAG deseninin Python karşılığıdır: belgeler parçalanır, terim frekansı (TF) vektörleri SQLite’da tutulur, sorgu kosinüs benzerliği ile sıralanır. Eğitim, demo ve laboratuvar içindir; canlı SOC orkestrasyonu değildir.

## İçindekiler

- [Kapsam](#kapsam)
- [Yapar ve yapmaz](#yapar-ve-yapmaz)
- [Mimari](#mimari)
- [Arayüz](#arayüz)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Bilgi bankası](#bilgi-bankası)
- [Yapılandırma](#yapılandırma)
- [Proje yapısı](#proje-yapısı)
- [Test](#test)
- [Güvenlik](#güvenlik)
- [Belgelendirme](#belgelendirme)
- [Lisans](#lisans)

## Kapsam

Copilot üç şeyi bir arada tutar:

1. **Incident card** — başlık, severity, MITRE, varlık, IOC, analist notu.
2. **RAG** — `docs/` playbook’ları, PDF’ler ve örnek MITRE kartları.
3. **Yerel dil modeli** — retrieved parçalar + kart bağlamı ile kısa veya bölümlü İngilizce cevap.

Arayüz dili Türkçe veya İngilizce olabilir. **Model her zaman İngilizce yazar.** Bu, Phi-3.5 Mini ve bilgi bankasının dilidir.

## Yapar ve yapmaz

| Yapar | Yapmaz |
|---|---|
| Playbook, seçilebilir metinli PDF ve MITRE parçalarını yerelde arar | Canlı ağı tarama, EDR sorgusu, log toplama |
| Kartı sağdaki JSON’a yansıtır; kart dolunca onaylı triaj üretir | EDR, firewall, Active Directory veya mailbox’a komut |
| Cevabın dayandığı parçayı ve 0–1 benzerlik skorunu gösterir | Exploit, malware, payload veya saldırı tarifi |
| Kart + sohbet + kaynakları JSON olarak indirir | Kesin CVE, atribüsyon veya hukuki hüküm |
| Çalışırken `.md` / `.txt` / `.pdf` yükleyip indeksler | OCR’siz taranmış (görüntü) PDF |
| Selamda RAG’i kapatır; kısa soruda daha az token kullanır | Çok kullanıcılı kimlik, rol veya ticket entegrasyonu |

**Karar verici sizsiniz.** İzolasyon, hesap yakma, hukuki bildirim ve SOAR adımı copilotun dışında kalır.

## Mimari

```
docs/  +  data/mitre_techniques.json
        ↓  ingest
   örtüşmeli parçalar (~200 birim, 25 örtüşme)
        ↓
   TF vektörü + inverted index  →  data/rag.db
        ↓
 analist sorusu / onaylanan kart
        ↓
 aday parçalar → kosinüs sıralama (top-k)
        ↓
 sistem promptu + parçalar + kart + soru
        ↓
 Foundry Local → Phi-3.5 Mini  →  İngilizce cevap
        ↓
 Kaynaklar paneli + sohbet
```

1. `src/loaders.py` Markdown, metin, PDF (`pypdf`) ve MITRE JSON okur.
2. `src/chunker.py` gövdeyi kayan pencerede böler; YAML front-matter varsa başlık ve kategori olarak saklanır.
3. `src/vector_store.py` her parçanın TF vektörünü SQLite’a (WAL) yazar. Sorgu anında ortak terimli adaylar toplanır, kosinüs skoru hesaplanır.
4. `src/query_policy.py` selamı RAG’siz ve kısa tutar; olay sorularında top-k ve token bütçesini ayarlar.
5. `src/chat_engine.py` Foundry SDK (veya OpenAI uyumlu yedek yol) ile modeli çağırır; cevap akışlı gelir.
6. `app.py` üç sütunlu analist çalışma alanını çizer.

Arama **TF + kosinüs**’tür, gömülü vektör API’si yoktur. Sık geçen genel kelimeler IDF ile bastırılmaz; demo playbook’larında bu yeterlidir, çok gürültülü büyük külliyatta zayıflayabilir.

## Arayüz

| Bölge | İşlev |
|---|---|
| Sol | Dil, yardım, incident card, örnek vaka, JSON export, belge yükleme, indeks listesi, MITRE katalog |
| Orta | Hızlı soru butonları, sohbet, akışlı cevap |
| Sağ | Son sorgunun kaynakları, aktif vaka JSON’u, kart tamamsa **Vakayı onayla ve analiz et** |

Örnek vaka seçilince kart alanları doldurulur; ardından düzenlenebilir. Ortadaki dört kısa buton sohbete soru basar, kartı doldurmaz.

Sağ üst **Extra** menüsü Streamlit’indir (Rerun, cache, ekran kaydı). Uygulama kodunun bir özelliği değildir.

## Kurulum

Geliştirme ve demo **Windows 10/11** üzerinde doğrulanmıştır.

### Gereksinimler

- Python 3.11+ (`Add Python to PATH`)
- [Foundry Local](https://foundrylocal.ai): `winget install Microsoft.FoundryLocal`
- İlk çalıştırmada `phi-3.5-mini` (~2 GB). GPU varsa Foundry CUDA/NPU yolunu kullanabilir; yoksa CPU
- Tarayıcı: Edge veya Chrome

PowerShell execution policy sanal ortamı engellerse:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### İlk çalıştırma

```powershell
git clone https://github.com/omrX61/soc-incident-copilot.git
cd soc-incident-copilot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.ingest
streamlit run app.py
```

Arayüz: **http://localhost:8501**

Windows GPU/NPU için Foundry belgelerine göre gerekirse:

```powershell
pip install foundry-local-sdk-winml
```

`ingest` her belge için chunk sayısını yazar ve `data/rag.db` üretir (`rag.db` git’te yoktur). Streamlit ilk açılışta indeks yoksa ingest’i kendisi de tetikler; modeli ilk sohbet yükler ve birkaç dakika sürebilir.

## Kullanım

1. Soldan örnek vaka seçin veya kartı elle doldurun.
2. Tüm alanlar dolunca sağda onay butonu çıkar; onay, kartı İngilizce triaj promptu olarak sohbete gönderir.
3. Serbest soru yazın. Kısa cevap varsayılandır.
4. Sağdaki **Kaynaklar** hangi playbook parçasının çekildiğini gösterir.
5. **JSON dışa aktar** kartı, sohbeti ve kaynakları indirir.

Gerçek IOC, dahili host ve kullanıcı adını ekran görüntüsüne veya public forka koymayın. Depodaki örnekler (`corp.example`, `hxxps://…`) sentetiktir.

## Bilgi bankası

Repoda phishing, ransomware, kimlik, yanal hareket, C2 ve kanıt SOP’ları; kamu IR PDF’leri; 12 örnek MITRE kartı ve 12 sentetik vaka vardır.

Yeni belge:

- UI’dan `.md` / `.txt` / `.pdf` yükleyip **İndeksle**, veya
- Dosyayı `docs/` altına koyup **Tüm docs/ klasörünü yeniden indeksle** (`ingest(clear=True)`).

Markdown front-matter örneği:

```markdown
---
title: Phishing BEC Playbook
category: Playbook
id: pb-phishing-bec
---

# Gövde metni
```

## Yapılandırma

Varsayılanlar `src/config.py` içindedir. `.env.example` şablondur; uygulama `.env` dosyasını kendiliğinden okumaz. Değeri süreç ortamına vermeniz gerekir:

```powershell
$env:FOUNDRY_MODEL="phi-3.5-mini"
$env:CHUNK_SIZE="200"
$env:CHUNK_OVERLAP="25"
$env:TOP_K="5"
streamlit run app.py
```

| Değişken | Anlam |
|---|---|
| `FOUNDRY_MODEL` | Varsayılan `phi-3.5-mini` |
| `FOUNDRY_APP_NAME` | Foundry uygulama adı |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | Parça boyutu ve örtüşme |
| `TOP_K` | Politika bunu soruya göre 3 veya 5 yapabilir |

Sıcaklık düşüktür (~0.2). Sohbet geçmişinin son birkaç turu modele gider.

## Proje yapısı

```
soc-incident-copilot/
├── app.py                      # Streamlit çalışma alanı
├── assets/                     # yerel uygulama ikonu
├── docs/                       # playbook, SOP, PDF
├── data/
│   ├── mitre_techniques.json   # örnek ATT&CK kartları
│   ├── sample_incidents.json   # örnek vakalar
│   └── rag.db                  # ingest sonrası (git dışı)
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
└── README_EN.md
```

## Test

Model çağırılmaz; Foundry olmadan çalışır:

```powershell
python -m pytest tests -q
```

Kapsam: parçalama, vektör deposu, soru politikası, tekrarlayan cevap kesme.

## Güvenlik

- Prompt, exploit ve payload üretimini yasaklar; uydurma IOC/CVE istemez.
- Yüklenen dosya adı `docs/` dışına çıkamaz.
- Streamlit’i internete `0.0.0.0` ile açmayın; kimlik doğrulama yoktur.
- Şirket playbook’unu public forka koymayın. Üçüncü parti PDF’lerin kendi lisans / TLP koşulları vardır.

## Belgelendirme

| Dosya | İçerik |
|---|---|
| [`SOC_Kılavuzu.md`](SOC_Kılavuzu.md) | Kurulumdan analist akışına tam Türkçe kılavuz |
| [`SOC_Guide_EN.md`](SOC_Guide_EN.md) | Aynı metnin İngilizcesi |
| [`README_EN.md`](README_EN.md) | Bu dosyanın İngilizcesi |

## Lisans

MIT. RAG tasarımının bir kısmı [leestott/local-rag](https://github.com/leestott/local-rag) (MIT) örnek alınarak uyarlanmıştır.
