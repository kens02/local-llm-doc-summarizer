from app.usecases.chunking import score_chunks, split_into_chunks


def test_split_into_chunks_basic():
    text = "A\nB\nC\n" * 10
    chunks = split_into_chunks(text, max_chars=20, overlap=5)
    assert chunks
    assert all(chunks)


def test_score_chunks():
    chunks = ["alpha beta", "gamma delta", "alpha gamma"]
    top = score_chunks("alpha", chunks, top_k=2)
    assert "alpha beta" in top
    assert len(top) == 2
