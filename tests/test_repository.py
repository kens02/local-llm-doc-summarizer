import importlib
import os
from pathlib import Path


def _reload_repo(tmp_path: Path):
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path}/test.db"
    import app.core.config as config

    importlib.reload(config)
    import app.infra.repository as repository

    importlib.reload(repository)
    return repository.SqliteRepository()


def test_create_and_list_document(tmp_path):
    repo = _reload_repo(tmp_path)
    doc = repo.create_document("a.txt", "hello", "ja")
    docs = repo.list_documents()
    assert len(docs) == 1
    assert docs[0].id == doc.id


def test_chat_room_and_messages(tmp_path):
    repo = _reload_repo(tmp_path)
    doc = repo.create_document("a.txt", "hello", "ja")
    room = repo.create_chat_room(doc.id, "room")
    repo.create_chat_message(room.id, "user", "hi")
    repo.create_chat_message(room.id, "assistant", "hello")
    msgs = repo.list_chat_messages(room.id)
    assert len(msgs) == 2
