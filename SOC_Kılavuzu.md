# SOC Incident Copilot — A’dan Z’ye Kılavuz

Yerel, çevrimdışı bir **SOC Incident Copilot**. Siber güvenlik operasyon merkezi (SOC) analistine playbook, SOP ve MITRE notlarından taslak triage üretir. Vaka verisi buluta gitmez; model bilgisayarınızda çalışır.

Bu belge hem **hiç SOC görmemiş** bir okuyucu hem de **alarm inceleyip vaka açan** bir analist içindir.

**Önemli sınır:** Copilot karar verici değildir. EDR’ye komut göndermez, hesabı kilitlemez, exploit veya saldırı tarifi üretmez. Ürettiği İngilizce metin taslaktır; onay, izolasyon ve hukuki adım size aittir.

---

## 1. Bu proje nedir?

SOC’ye bir alarm düştüğünde analist şunları ister: *Bu ne? Ne kadar acil? Şimdi ne yapmalıyım? Hangi kanıtı saklamalıyım?*

SOC Incident Copilot bu sorulara **sizin yüklediğiniz belgelerden** (RAG) ve yerelde çalışan **Phi-3.5 Mini** ile kısa İngilizce cevap verir.

| Yapar | Yapmaz |
|---|---|
| Playbook / PDF / MITRE parçalarını bulur | Gerçek ağı tarama |
| Incident card’ı JSON’a yansıtır | EDR, firewall, AD’ye komut |
| Onaydan sonra kartı triage eder | Malware / exploit / payload üretme |
| Vakayı JSON olarak indirir | “Kesin CVE / hukuki hüküm” iddiası |
| Sohbette kısa veya bölümlü taslak verir | Buluta vaka gönderme |

Arayüz dili Türkçe veya İngilizce olabilir. **Model her zaman İngilizce yazar.** Bu, Phi-3.5 Mini’nin ve bilgi bankasının dilidir; tasarım kararıdır.

---

## 2. Neden yerel?

- **Gizlilik:** Vaka başlığı, IOC, host adı Foundry Local dışına çıkmaz (sizin makineniz).
- **Demo / eğitim:** İnternetsiz veya kısıtlı ağda gösterilebilir.
- **Denetlenebilirlik:** Cevabın yanında **Kaynaklar** paneli, hangi belge parçasının kullanıldığını ve benzerlik skorunu gösterir.

---

## 3. Sözlük

| Terim | Düz dil |
|---|---|
| **SOC** | Şirketin güvenlik izleme ekibi. Alarm gelir, biri bakar. |
| **Incident / vaka** | “Bir şey ters gitmiş olabilir” kaydı: phishing, ransomware, çalıntı hesap. |
| **Triage** | İlk bakış: ne bu, ne kadar acil, şimdi ne yapalım. |
| **Severity** | Aciliyet: Informational → Low → Medium → High → Critical. |
| **MITRE ATT&CK** | Saldırgan davranış kataloğu. `T1566` phishing, `T1486` fidye şifreleme. |
| **IOC** | İz: kötü domain, hash, IP, dosya adı. |
| **Playbook** | “Bu alarm gelince şu adımları izle” talimatı. |
| **Containment** | Yayılmayı durdurmak: izolasyon, oturum düşürme, URL kesme. |
| **RAG** | Cevabı modelin ezberinden değil, sizin belgelerinizden çekme. |
| **Phi-3.5 Mini** | Microsoft’un küçük dil modeli; burada çevrimdışı çalışır. |
| **Foundry Local** | Modeli yerelde yükleyen Microsoft çalışma katmanı. |
| **Kaynaklar** | Cevabın dayandığı belge parçaları ve 0–1 benzerlik skoru. |
| **Ingest** | `docs/` ve MITRE JSON’unu okuyup `data/rag.db` indeksine yazmak. |
| **TF / kosinüs** | Bu projedeki arama: terim frekansı vektörü + kosinüs benzerliği (gömülü vektör API’si yok). |

---

## 4. Mimari (kısaca nasıl çalışır)

```
docs/  +  data/mitre_techniques.json
        ↓  (ingest)
   parçalama (~200 kelime, örtüşme)
        ↓
   TF vektörü + inverted index  →  data/rag.db
        ↓
 analist sorusu / onaylanan kart
        ↓
 benzer parçalar (top-k)
        ↓
 sistem promptu + parçalar + soru
        ↓
 Foundry Local → Phi-3.5 Mini  →  İngilizce cevap
        ↓
 Kaynaklar paneli + sohbet geçmişi
```

1. Markdown, PDF ve MITRE JSON okunur (`src/loaders.py`). PDF metni **pypdf** ile çıkarılır.
2. Metin ~200 birimlik örtüşmeli parçalara bölünür (`src/chunker.py`).
3. Her parça SQLite’a yazılır (`src/vector_store.py`).
4. Soru vektörlenir; adaylar daraltılır, kosinüs ile sıralanır.
5. En iyi parçalar prompta eklenir; `src/chat_engine.py` modeli çağırır.
6. `app.py` Streamlit arayüzünü çizer.

Selam / teşekkür gibi kısa sohbetlerde RAG **kapanır** (gereksiz playbook çekilmesin amaçlı).

---

## 5. Gereksinimler

- **Windows 10/11** (geliştirme ve demo bu ortamda yapıldı)
- **Python 3.11+** ([python.org](https://www.python.org/downloads/) — kurulumda “Add Python to PATH”)
- **[Foundry Local](https://foundrylocal.ai)**  
  `winget install Microsoft.FoundryLocal`
- İlk çalıştırmada **phi-3.5-mini** indirilir (kabaca **~2 GB**). GPU varsa CUDA varyantı, yoksa CPU.
- Tarayıcı: Edge / Chrome. Arayüz: `http://localhost:8501`
- İsteğe bağlı: NVIDIA GPU + Foundry’nin CUDA execution provider’ı (daha hızlı üretim)

macOS / Linux’ta Foundry Local ve paket adları değişebilir; bu kılavuz Windows odaklıdır.

---

## 6. Kurulum (adım adım)

PowerShell’i açın. Execution policy ilk kez sanal ortamı engellerse:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Proje klasörüne gidin (kendi yolunuz):

```powershell
cd C:\Users\<kullanici>\soc-incident-copilot
```

Sanal ortam ve bağımlılıklar:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` özeti:

| Paket | Ne işe yarar |
|---|---|
| `streamlit` | Web arayüzü |
| `pypdf` | Playbook PDF’lerini okuyup indekse almak |
| `openai` | Foundry’nin OpenAI uyumlu istemci yolu |
| `foundry-local-sdk` | Yerel model yöneticisi ve sohbet |
| `pytest` | Birim testleri |

Windows GPU/NPU için gerekirse (Foundry belgelerine bakın):

```powershell
pip install foundry-local-sdk-winml
```

Bilgi bankasını ilk kez indeksleyin:

```powershell
python -m src.ingest
```

Terminalde her belge için chunk sayısı basılır. Bittiğinde `data/rag.db` oluşur.

Uygulamayı başlatın:

```powershell
streamlit run app.py
```

Tarayıcı `http://localhost:8501` açılmazsa adresi elle yazın. Durdurmak için terminalde `Ctrl+C`.

### 6.1 İsteğe bağlı ortam değişkenleri

`.env.example` dosyasını kopyalayıp `.env` yapabilirsiniz (`.env` git’e girmez). Varsayılanlar `src/config.py` içindedir:

| Değişken | Anlamı |
|---|---|
| `FOUNDRY_MODEL` | Varsayılan `phi-3.5-mini` |
| `FOUNDRY_APP_NAME` | Foundry uygulama adı |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | Parça boyutu |
| `TOP_K` | Varsayılan kaç parça çekileceği (politika bunu soruya göre 3 veya 5 yapabilir) |

---

## 7. İlk açılışta ne görürsünüz?

1. Koyu tema, sol kenar çubuğu, ortada sohbet, sağda kaynaklar.
2. İlk mesajda model yüklemesi **birkaç dakika** sürebilir. Turuncu nokta + “Cevap yükleniyor”.
3. Sol üstte kenar çubuğunu kapatma oku.
4. Sağ üstte **Extra** menüsü vardır.

Kenar çubuğundaki **Nasıl kullanılır?** kısa hatırlatmadır. Tam metin bu belgedir; depodaki `KULLANIM_KILAVUZU.md` ise uygulama içi özet kılavuzdur.

---

## 8. Ekranın üç sütunu

### 8.1 Sol — Incident card

Analistin resmi formu. Doldukça sağdaki **Aktif vaka** JSON’u aynı anda güncellenir.

| Alan | Ne yazılır | Örnek |
|---|---|---|
| Örnek vaka | Hazır senaryo | VIP mailbox AiTM phishing |
| Alert / vaka başlığı | Kısa isim | Finance share encryption |
| Severity | Aciliyet | High / Critical |
| MITRE | Teknik kod(lar) | T1486, T1021.001 |
| Etkilenen varlıklar | Host / kullanıcı | FILESRV01, j.hale |
| IOC listesi | Satır satır iz | `ransom note.txt` |
| Analist notu | Gördüğünüz şey | VSS silindi, yedek job fail |

**Onay:** Başlık, severity, MITRE, varlık, en az bir IOC ve not **hepsi** dolunca sağda **Vakayı onayla ve analiz et** çıkar. Yarım kartla onay yok; onaysız otomatik analiz yok.

Onay, sohbete şuna benzer bir İngilizce prompt basar: kartı *analyze* et, *incident type, severity, containment, evidence, gaps* başlıklarını ört.

**JSON dışa aktar:** Kart + sohbet + kaynaklar. Ticket eki veya yedek için. PDF export yoktur.

**Knowledge base:** `.md` / `.txt` / `.pdf` yükler, tek belgeyi indeksler. **Tüm docs/ klasörünü yeniden indeksle** her şeyi baştan işler (`ingest(clear=True)`).

**MITRE katalog:** Örnek teknik kartları. Tıklamak sohbet başlatmaz; referanstır.

### 8.2 Orta — Incident workspace

- Dört **quick incident** düğmesi: hazır İngilizce/Türkçe sorular. **Sayfa yenilenince (F5)** rastgele değişir; Extra → Rerun sohbeti silmeden script’i yeniden çalıştırır, bu dört düğmeyi genelde **değiştirmez**.
- Alt kutu: serbest soru.
- Cevap İngilizce.

### 8.3 Sağ — Kaynaklar ve Aktif vaka

- **Kaynaklar:** Bu cevaba çekilen parçalar. Skor 0–1; yüksek olan daha ilgili.
- “Eşleşen kaynak yok”: selamlaşma (RAG kapalı) veya kelime eşleşmedi.
- **Aktif vaka:** Soldaki kartın JSON hali.

### 8.4 Extra menüsü (sağ üst)

Streamlit’in kendi menüsü; copilot komutu değildir.

| Öğe | Ne yapar |
|---|---|
| **Rerun** | `app.py`’yi baştan çalıştırır. Sohbet, kart, yüklü model genelde **kalır**. |
| **Auto rerun** | Kaynak dosya değişince script’i otomatik yeniler. |
| **Clear cache** | Streamlit `@st.cache_resource` belleklerini boşaltır. Bu uygulamada motor ayrıca session’da tutulduğu için **Foundry çoğu zaman yeniden yüklenmez**. Sohbet silinmez. `rag.db` diskte kalır. |
| **Print / Record screen** | Tarayıcı yazdırma veya ekran kaydı. |

---

## 9. Hiç SOC bilgim yok — 10 dakikalık deneme

1. Arayüzü **Türkçe** bırakın. Cevap yine İngilizce olacak.
2. Solda **Örnek vaka** seçin (ör. VIP mailbox phishing).
3. Boş kalan alanları örnek değerlerle doldurun (eğitim IOC’leri yeter).
4. Sağda JSON’un dolduğunu görün.
5. **Vakayı onayla ve analiz et.**
6. Ortada İngilizce triage, sağda hangi PDF/playbook parçasının geldiğine bakın.
7. İsterseniz **JSON olarak dışa aktar.**

Bu, “saldırı yaptım” anlamına gelmez. Sentetik senaryodur.

Sohbette deneyin:

```text
Password spray followed by a successful service-account logon. How should I proceed?
```
---

## 10. Analist için önerilen akış

1. Alarmı karta dökün (başlık, severity, MITRE, host, IOC, not).
2. Aktif vaka JSON’unu gözle kontrol edin.
3. Onaylayın → triage + kaynaklar.
4. Gerekirse sohbette daraltın: *containment only*, *evidence to collect for T1003.001*.
5. JSON’u ticket’a ekleyin.
6. İzolasyon / hesap kilidi kararını siz verin.

---

## 11. Etkili sorular (gizli slash komut yok)

Uzunluk **kartın dolu olup olmamasına** değil, metne bağlıdır:

| Ne yazarsınız | Ne beklenir |
|---|---|
| `How should I proceed?` + vaka cümlesi | Kısa maddeler |
| Yalnızca `Analyze:` öneki | Sihirli şablon **değil**; çoğu zaman yine madde |
| `Triage … Cover incident type, severity, immediate containment, evidence, remaining gaps.` | Onay butonuna yakın bölümlü triage |
| `Playbook detail for T1486 ransomware on a file server.` | Bölümlü playbook taslağı |
| MITRE kodu (`T1048`, `T1486`) | RAG isabeti artar |
| Kart + **Onay** | Cover listesi sizin yerinize gönderilir |

---

## 12. Depo haritası — klasör ve dosya

```
soc-incident-copilot/
├── app.py                 # Streamlit arayüzü (tek giriş noktası)
├── requirements.txt       # Python paketleri
├── pytest.ini             # test yolu
├── LICENSE                # MIT
├── README.md              # kısa kurulum
├── KULLANIM_KILAVUZU.md   # uygulama içi özet kılavuz
├── .env.example           # isteğe bağlı ayar şablonu
├── .gitignore
├── .streamlit/config.toml # port 8501, koyu tema
├── assets/                # sekme / marka ikonu
├── docs/                  # bilgi bankası (md + pdf)
├── data/                  # MITRE JSON, örnek kartlar, rag.db
├── src/                   # motor
└── tests/                 # birim testleri
```

Git’e **alınmaz:** `.venv/`, `.env`, `data/*.db` (indeksi her makinede `python -m src.ingest` ile üretin), `__pycache__/`.

### 12.1 Kök dosyalar

| Dosya | Ne işe yarar |
|---|---|
| `app.py` | Üç sütunlu UI, kart, sohbet, onay, ingest butonları, tema, Extra/Deploy CSS |
| `requirements.txt` | pip bağımlılıkları |
| `LICENSE` | MIT; local-rag uyarlaması belirtilir |
| `README.md` | GitHub vitrini: mimari + komutlar |
| `KULLANIM_KILAVUZU.md` | Uygulama içi kısa kılavuz |
| `.env.example` | Model adı, chunk, port şablonu |
| `pytest.ini` | `pythonpath = .`, testler `tests/` |

### 12.2 `src/` — motor

| Dosya | Ne işe yarar |
|---|---|
| `config.py` | Kök yol, model adı, `docs/`, `data/rag.db`, chunk / top_k |
| `loaders.py` | md/txt/pdf/MITRE JSON → düz metin belge |
| `chunker.py` | Parçalama, front matter, TF, kosinüs |
| `vector_store.py` | SQLite indeks ve arama |
| `ingest.py` | Toplu indeks. Çalıştır: `python -m src.ingest` |
| `chat_engine.py` | Foundry başlatma, retrieve, stream |
| `query_policy.py` | Selam mı, kısa mı; token ve top_k |
| `prompts.py` | Sistem promptu (her zaman İngilizce) |
| `answer_cleanup.py` | Aynı başlığın ikinci kez basılmasını keser |
| `i18n.py` | TR/EN etiketler, quick incident havuzu |

### 12.3 `docs/` — bilgi bankası

Markdown playbook / SOP örnekleri:

| Dosya | Konu |
|---|---|
| `soc-incident-handling-sop.md` | SOC olay yönetimi SOP |
| `ransomware-containment-playbook.md` | Fidye containment |
| `phishing-bec-playbook.md` | Phishing / BEC |
| `lateral-movement-playbook.md` | Yanal hareket |
| `identity-threat-runbook.md` | Kimlik tehdidi |
| `c2-hunt-notes.md` | C2 av notları |
| `evidence-chain-of-custody.md` | Kanıt zinciri |
| `log-source-coverage.md` | Log kaynakları |
| `severity-escalation-matrix.md` | Severity / eskalasyon |

PDF’ler (ingest ile metne çevrilir): kamu IR / NIST / IC3 / ransomware / phishing rehberleri. Yeni PDF: dosyayı `docs/` içine koyun → **yeniden indeksle**.

### 12.4 `data/`

| Dosya | Ne işe yarar |
|---|---|
| `mitre_techniques.json` | Örnek ATT&CK teknikleri (tam MITRE kataloğu değil) |
| `sample_incidents.json` | Sol “Örnek vaka” listesi |
| `rag.db` | Arama indeksi (yerelde üretilir, genelde git’te yok) |
| `.gitkeep` | Boş `data/` klasörünün git’te durması |

### 12.5 `tests/`

`test_chunker.py`, `test_vector_store.py`, `test_query_policy.py`, `test_answer_cleanup.py`. Sanal ortamdayken:

```powershell
python -m pytest tests -q
```

(`pytest` paketinin yüklü olması gerekir.)

### 12.6 `assets/` ve `.streamlit/`

- `assets/soc_incident_copilot_icon.png` — sekme ikonu.
- `.streamlit/config.toml` — `headless`, port **8501**, koyu renk paleti.

---

## 13. Sık görülen durumlar

| Ne gördünüz | Ne demek | Ne yapın |
|---|---|---|
| Cevap yükleniyor + turuncu nokta | Model üretiyor | Bekleyin; ilk yükleme uzun olabilir |
| Foundry singleton / already initialized | Model bu süreçte zaten açık | Sayfayı yenileyin; gerekirse Streamlit’i kapatıp açın |
| Port 8501 in use | Başka bir Streamlit açık | Eski terminalde Ctrl+C veya başka port |
| Kaynak yok | RAG kapalı veya eşleşme zayıf | MITRE kodu, `ransomware`, host adı kullanın |
| Türkçe sordum, İngilizce cevap | Tasarım | Arayüz dili yalnızca menü |
| Clear cache modeli düşürmedi | Motor session’da | Streamlit sürecini kapatın |
| PDF “no selectable text” | Taranmış görüntü PDF | OCR’lı metin veya Markdown playbook kullanın |
| Activate.ps1 yasak | Execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |

---

## 14. Güvenlik ve paylaşım (GitHub / LinkedIn)

- Örnek IOC’ler **eğitim içindir** (`corp.example`, `hxxps://…`).
- Gerçek vaka, gerçek kullanıcı, dahili IP ve hash’i ekrana / JSON’a / ekran görüntüsüne koymayın.
- LinkedIn videosunda Extra → Record screen kullanırsanız tarayıcı iznini onaylayın; kayıtta sol kartı boş bırakın veya sentetik doldurun.
- Depoyu GitHub’a atarken: `.env`, `.venv`, `rag.db`, şirket playbook’u **yüklemeyin**. Kamu PDF lisanslarına uyun.
- Lisans: **MIT**. Üçüncü parti PDF’lerin kendi lisans / TLP işaretleri vardır; yeniden yayınlarken kaynağı belirtin.

---

## 15. GitHub’da paylaşırken

Depo kökünde `README.md` zaten kısa kurulumu içerir. Bu kılavuzu (`SOC_Kılavuzu.md`) README’den bağlayabilirsiniz.

Önerilen README maddeleri: ne olduğu, yerel / çevrimdışı, ekran görüntüsü, kurulum komutları, “yapmaz” listesi, lisans.

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

## 16. Geliştirici notları

- Sohbet geçmişi son birkaç turu modele gider.
- `@st.cache_resource` Foundry örneğini tutar; ENGINE_REVISION değişince yeni önbellek anahtarı kullanılır.
- Sıcaklık (`temperature`) düşüktür (~0.2); aynı soru benzer çıkar, birebir aynı olmak zorunda değildir.
- Testler modeli çağırmaz; Foundry olmadan `pytest` geçebilir.

---

## 17. Kaynaklar ve teşekkür

- [Foundry Local](https://foundrylocal.ai)
- [Phi-3.5 Mini](https://azure.microsoft.com/en-us/products/phi-3)
- MITRE ATT&CK® — teknik kimlikleri eğitim amaçlı örneklenmiştir
- Kamu IR / NIST / IC3 PDF’leri `docs/` içinde, kendi yayımlayan kurumlarının koşullarıyla

---

*SOC Incident Copilot — yerel triage asistanı. Siz karar vericisiniz.*