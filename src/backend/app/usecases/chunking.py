import re
from typing import Iterable


def split_into_chunks(text: str, max_chars: int = 1200, overlap: int = 200) -> list[str]:
    cleaned = text.replace("\r\n", "\n").strip()
    if not cleaned:
        return []

    paragraphs = [p.strip() for p in cleaned.split("\n") if p.strip()]
    chunks: list[str] = []
    buffer = ""

    for para in paragraphs:
        if len(buffer) + len(para) + 1 <= max_chars:
            buffer = f"{buffer}\n{para}".strip()
        else:
            if buffer:
                chunks.append(buffer)
            buffer = para
    if buffer:
        chunks.append(buffer)

    if overlap <= 0 or len(chunks) <= 1:
        return chunks

    overlapped: list[str] = []
    for idx, chunk in enumerate(chunks):
        if idx == 0:
            overlapped.append(chunk)
            continue
        prefix = chunks[idx - 1][-overlap:]
        overlapped.append(f"{prefix}\n{chunk}")
    return overlapped


_word_re = re.compile(r"[A-Za-z0-9_\-]+")


def score_chunks(query: str, chunks: Iterable[str], top_k: int = 3) -> list[str]:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return list(chunks)[:top_k]

    scored = []
    for chunk in chunks:
        tokens = _tokenize(chunk)
        score = sum(tokens.get(t, 0) for t in query_tokens)
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for score, c in scored[:top_k] if score > 0] or [c for _, c in scored[:top_k]]


def _tokenize(text: str) -> dict[str, int]:
    tokens: dict[str, int] = {}
    for word in _word_re.findall(text.lower()):
        tokens[word] = tokens.get(word, 0) + 1
    if tokens:
        return tokens

    for ch in text:
        if ch.strip():
            tokens[ch] = tokens.get(ch, 0) + 1
    return tokens
