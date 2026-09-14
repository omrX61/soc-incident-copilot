from src.vector_store import VectorStore


def test_insert_and_search(tmp_path):
    store = VectorStore(tmp_path / "rag.db")
    store.insert("doc-a", "Phishing Playbook", "Playbook", 0, "Revoke tokens after AiTM phishing click")
    store.insert("doc-b", "Ransomware Playbook", "Playbook", 0, "Isolate hosts during ransomware encryption")
    hits = store.search("phishing token revoke", top_k=2)
    assert hits
    assert hits[0].doc_id == "doc-a"
    assert store.count() == 2
    docs = store.list_docs()
    assert {d["doc_id"] for d in docs} == {"doc-a", "doc-b"}
    store.remove_by_doc_id("doc-a")
    assert store.count() == 1
    store.close()
