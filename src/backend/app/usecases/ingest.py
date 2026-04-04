from app.infra.parsers import parse_file
from app.infra.repository import SqliteRepository
from app.usecases.chunking import split_into_chunks


def ingest_document(repo: SqliteRepository, filename: str, data: bytes, language: str) -> str:
    content, _ = parse_file(filename, data)
    if not content.strip():
        raise ValueError("ファイル内容が空です")
    document = repo.create_document(filename=filename, content=content, language=language)
    chunks = split_into_chunks(content)
    repo.replace_chunks(document.id, chunks)
    return document.id
