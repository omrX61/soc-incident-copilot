import pytest

from src.chunker import chunk_text, cosine_similarity, parse_front_matter, term_frequency


def test_parse_front_matter():
    raw = "---\ntitle: Demo\ncategory: Test\nid: X-1\n---\n\n# Body\nHello"
    meta, body = parse_front_matter(raw)
    assert meta["title"] == "Demo"
    assert meta["id"] == "X-1"
    assert "Hello" in body


def test_chunk_overlap():
    words = " ".join(f"w{i}" for i in range(50))
    chunks = chunk_text(words, max_tokens=20, overlap_tokens=5)
    assert len(chunks) > 1
    first_tail = chunks[0].split()[-5:]
    second_head = chunks[1].split()[:5]
    assert first_tail == second_head


def test_cosine_similarity_identical():
    tf = term_frequency("phishing credential harvest inbox rule")
    assert cosine_similarity(tf, tf) == pytest.approx(1.0)


def test_cosine_similarity_disjoint():
    a = term_frequency("alpha beta")
    b = term_frequency("gamma delta")
    assert cosine_similarity(a, b) == 0.0
