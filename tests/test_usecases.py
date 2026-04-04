import importlib
import os
from pathlib import Path

from app.usecases.summarize import summarize_document
from app.usecases.notes import generate_notes


class FakeLLM:
    def __init__(self, content: str):
        self._content = content

    def generate(self, prompt: str):
        class Resp:
            def __init__(self, content: str):
                self.content = content

        return Resp(self._content)


class FakeLLMChat(FakeLLM):
    def generate_with_context(self, messages):
        return self.generate("")


def _reload_repo(tmp_path: Path):
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path}/test.db"
    import app.core.config as config

    importlib.reload(config)
    import app.infra.repository as repository

    importlib.reload(repository)
    return repository.SqliteRepository()


def test_summarize_document(tmp_path):
    repo = _reload_repo(tmp_path)
    doc = repo.create_document("a.txt", "hello world", "ja")
    summary = summarize_document(repo, FakeLLM("summary"), doc.id, "bullet", "ja", 60)
    assert "summary" in summary


def test_generate_notes(tmp_path):
    repo = _reload_repo(tmp_path)
    doc = repo.create_document("a.txt", "hello world", "ja")
    notes = generate_notes(repo, FakeLLM("notes"), doc.id, "ja")
    assert "notes" in notes
