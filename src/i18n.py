"""Turkish / English UI strings and quick-incident pools."""

from __future__ import annotations

UI = {
    "tr": {
        "caption": "Yerel RAG · Phi-3.5 Mini · SQLite",
        "language": "Arayüz dili",
        "incident_card": "Incident card",
        "sample_case": "Örnek vaka",
        "empty": "(boş)",
        "alert_title": "Alert / vaka başlığı",
        "severity": "Severity",
        "mitre": "MITRE (ör. T1566.001, TA0001)",
        "assets": "Etkilenen varlıklar",
        "iocs": "IOC / observable listesi",
        "notes": "Analist notu",
        "export_json": "Vakayı JSON olarak dışa aktar",
        "knowledge_base": "Knowledge base",
        "upload": "Playbook yükle",
        "index": "İndeksle",
        "reindex": "Tüm docs/ klasörünü yeniden indeksle",
        "indexed": "{n} belge indekslendi",
        "added": "{title} eklendi ({chunks} chunk)",
        "reindexed": "{documents} belge, {chunks} chunk",
        "mitre_catalog": "MITRE katalog",
        "workspace": "Incident workspace",
        "workspace_blurb": (
            "Phi-3.5 Mini yanıtları yerel playbook, PDF ve MITRE kayıtlarından çekilen "
            "parçalara dayandırılır. Model yoksa sohbet başlatılamaz."
        ),
        "chat_placeholder": "Analist sorusu veya vaka özeti yazın",
        "loading_model": "Foundry Local ve Phi-3.5 yükleniyor (ilk seferde birkaç dakika sürebilir)...",
        "indexing": "Bilgi bankası indeksleniyor...",
        "reindexing": "Yeniden indeksleniyor...",
        "sources": "Kaynaklar",
        "no_sources": "Bu sorgu için eşleşen kaynak bulunamadı.",
        "active_case": "Aktif vaka",
        "upload_types": "Yalnızca .md, .txt ve .pdf kabul edilir",
        "bad_filename": "Geçersiz dosya adı",
        "answering": "Cevap yükleniyor",
        "approve_case": "Vakayı onayla ve analiz et",
        "approve_hint": "Tüm Incident card alanlarını doldurunca onay butonu çıkar. Onay, bu vakayı sohbete gönderir.",
        "approve_ready": "Kart tamam. Onaylarsan copilot bu vakayı İngilizce triage eder.",
        "help_title": "Nasıl kullanılır?",
        "help_body": """
1. **Arayüz dili** yalnızca etiketleri değiştirir. Chatbot her zaman İngilizce yazar.
2. Solda **Incident card** doldur → sağda **Active case** aynı kaydı gösterir.
3. Tüm alanlar dolunca **Vakayı onayla ve analiz et** çıkar; onay kısa triage üretir.
4. Ortadaki sohbete serbest soru yaz. Kısa cevap varsayılandır.
5. **Kaynaklar** copilotun hangi playbook parçalarını kullandığını gösterir.
6. **JSON dışa aktar** vaka kartını, sohbeti ve kaynakları indirir.
7. Tam metin: `SOC_Kılavuzu` / `SOC_Guide_EN`
""",

    },
    "en": {
        "caption": "Local RAG · Phi-3.5 Mini · SQLite",
        "language": "UI language",
        "incident_card": "Incident card",
        "sample_case": "Sample case",
        "empty": "(empty)",
        "alert_title": "Alert / case title",
        "severity": "Severity",
        "mitre": "MITRE (e.g. T1566.001, TA0001)",
        "assets": "Affected assets",
        "iocs": "IOC / observable list",
        "notes": "Analyst notes",
        "export_json": "Export case as JSON",
        "knowledge_base": "Knowledge base",
        "upload": "Upload playbook",
        "index": "Index",
        "reindex": "Re-index entire docs/ folder",
        "indexed": "{n} documents indexed",
        "added": "Added {title} ({chunks} chunks)",
        "reindexed": "{documents} documents, {chunks} chunks",
        "mitre_catalog": "MITRE catalog",
        "workspace": "Incident workspace",
        "workspace_blurb": (
            "Phi-3.5 Mini answers are grounded in retrieved playbook, PDF, and MITRE chunks. "
            "Chat cannot start if the local model is unavailable."
        ),
        "chat_placeholder": "Ask an analyst question or paste a case summary",
        "loading_model": "Loading Foundry Local and Phi-3.5 (first run may take several minutes)...",
        "indexing": "Indexing knowledge base...",
        "reindexing": "Re-indexing...",
        "sources": "Sources",
        "no_sources": "No matching sources for this query.",
        "active_case": "Active case",
        "upload_types": "Only .md, .txt and .pdf files are accepted",
        "bad_filename": "Invalid filename",
        "answering": "Generating answer",
        "approve_case": "Approve case and analyze",
        "approve_hint": "Fill every Incident card field to reveal the approve button. Approval sends this case to the copilot.",
        "approve_ready": "Card complete. Approval asks the copilot for an English triage of this case.",
        "help_title": "How to use",
        "help_body": """
1. **UI language** only changes labels. The chatbot always answers in English.
2. Fill **Incident card** on the left → **Active case** on the right mirrors it.
3. When every field is filled, **Approve case and analyze** runs a short triage.
4. Type a free question in chat. Short answers are the default.
5. **Sources** shows which playbook chunks were used.
6. **Export JSON** downloads the card, chat, and sources.
7. Full guide: `SOC_Kılavuzu` / `SOC_Guide_EN`
""",

    },
}

QUICK_INCIDENTS = {
    "tr": [
        "Phishing e-postasında credential harvest şüphesi var. İlk 30 dakikalık triage nedir?",
        "Ransomware uyarıları endpoint'te şüpheli şifreleme gösteriyor. Containment sırası ne olmalı?",
        "T1078 Valid Accounts için hangi log kaynaklarını ve kanıtları toplamalıyım?",
        "C2 beacon şüphesi (T1071) için ağ ve host tarafında hangi adımları izlerim?",
        "VIP mailbox'ta AiTM tıklaması ve yeni inbox kuralı var. Hemen ne yapmalıyım?",
        "Password spray sonrası bir servis hesabında başarılı oturum görüldü. Nasıl ilerlemeliyim?",
        "LSASS bellek erişimi (T1003.001) alarmı geldi. Kimlikleri nasıl yakmalı ve ne toplamalıyım?",
        "FILESRV01 üzerinde VSS silme ve fidye notu var. Hasta sıfır nasıl aranır?",
        "Excel makrosundan PowerShell cradle çalıştı. Kuruluş genelinde av nasıl yapılır?",
        "Herkese açık VPN/web uygulamasında exploit izi ve web shell şüphesi var. İlk adımlar neler?",
        "RDP ile yatay hareket (T1021.001) görüldü. Kaynak ve hedefte ne bakmalıyım?",
        "Büyük outbound arşiv transferi (T1048) alarmı var. Kanıt ve containment nedir?",
    ],
    "en": [
        "Suspected credential-harvest phishing. What is the first 30-minute triage?",
        "EDR shows likely ransomware encryption on an endpoint. What is the containment order?",
        "For T1078 Valid Accounts, which log sources and evidence should I collect?",
        "Suspected C2 beaconing (T1071). What host and network steps should I follow?",
        "VIP mailbox AiTM click plus a new inbox rule. What should I do immediately?",
        "Password spray followed by a successful service-account logon. How should I proceed?",
        "LSASS memory access alert (T1003.001). Which identities do I burn and what do I collect?",
        "VSS deletion and a ransom note on FILESRV01. How do I hunt patient zero?",
        "PowerShell cradle launched from an Excel macro. How do I hunt estate-wide?",
        "Public-facing VPN/web app exploit with a possible web shell. What are the first steps?",
        "RDP lateral movement (T1021.001) observed. What do I inspect on source and destination?",
        "Large outbound archive transfer (T1048). What evidence and containment apply?",
    ],
}

QUICK_COUNT = 4

_FALLBACKS = {
    "approve_case": "Approve case and analyze",
    "approve_hint": "Fill every Incident card field to reveal the approve button.",
    "approve_ready": "Card complete. Approval sends this case to the copilot.",
}


def labels(lang: str) -> dict[str, str]:
    merged = dict(_FALLBACKS)
    merged.update(UI.get("en", {}))
    merged.update(UI.get(lang, {}))
    return merged
