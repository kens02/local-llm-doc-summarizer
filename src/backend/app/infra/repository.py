import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional
from uuid import uuid4

from app.core.config import settings
from app.domain.models import ChatMessage, ChatRoom, Chunk, Document, Note, Summary


class RepositoryError(RuntimeError):
    pass


def _utcnow() -> datetime:
    return datetime.utcnow()


def _ensure_db_path(db_url: str) -> Path:
    if not db_url.startswith("sqlite:///"):
        raise RepositoryError("DATABASE_URL は sqlite:/// 形式のみ対応")
    path = Path(db_url.replace("sqlite:///", "", 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


class SqliteRepository:
    def __init__(self) -> None:
        self.db_path = _ensure_db_path(settings.database_url)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    content TEXT NOT NULL,
                    language TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(id)
                );
                CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id
                    ON document_chunks(document_id);

                CREATE TABLE IF NOT EXISTS summaries (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    style TEXT NOT NULL,
                    language TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(id)
                );
                CREATE INDEX IF NOT EXISTS idx_summaries_document_id
                    ON summaries(document_id);

                CREATE TABLE IF NOT EXISTS chat_rooms (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(id)
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(room_id) REFERENCES chat_rooms(id)
                );
                CREATE INDEX IF NOT EXISTS idx_chat_messages_room_id
                    ON chat_messages(room_id);

                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(id)
                );
                """
            )

    def create_document(self, filename: str, content: str, language: str) -> Document:
        doc_id = str(uuid4())
        created_at = _utcnow()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO documents (id, filename, content, language, created_at) VALUES (?, ?, ?, ?, ?)",
                (doc_id, filename, content, language, created_at.isoformat()),
            )
        return Document(doc_id, filename, content, language, created_at)

    def get_document(self, document_id: str) -> Optional[Document]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE id = ?", (document_id,)
            ).fetchone()
        if not row:
            return None
        return Document(
            row["id"], row["filename"], row["content"], row["language"], datetime.fromisoformat(row["created_at"])
        )

    def list_documents(self) -> list[Document]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
        return [
            Document(
                row["id"], row["filename"], row["content"], row["language"], datetime.fromisoformat(row["created_at"])
            )
            for row in rows
        ]

    def replace_chunks(self, document_id: str, chunks: Iterable[str]) -> list[Chunk]:
        with self._connect() as conn:
            conn.execute("DELETE FROM document_chunks WHERE document_id = ?", (document_id,))
            stored = []
            for idx, content in enumerate(chunks):
                chunk_id = str(uuid4())
                conn.execute(
                    "INSERT INTO document_chunks (id, document_id, chunk_index, content) VALUES (?, ?, ?, ?)",
                    (chunk_id, document_id, idx, content),
                )
                stored.append(Chunk(chunk_id, document_id, idx, content))
        return stored

    def list_chunks(self, document_id: str) -> list[Chunk]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM document_chunks WHERE document_id = ? ORDER BY chunk_index", (document_id,)
            ).fetchall()
        return [Chunk(row["id"], row["document_id"], row["chunk_index"], row["content"]) for row in rows]

    def create_summary(self, document_id: str, style: str, language: str, content: str) -> Summary:
        summary_id = str(uuid4())
        created_at = _utcnow()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO summaries (id, document_id, style, language, content, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (summary_id, document_id, style, language, content, created_at.isoformat()),
            )
        return Summary(summary_id, document_id, style, language, content, created_at)

    def list_summaries(self, document_id: str) -> list[Summary]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM summaries WHERE document_id = ? ORDER BY created_at DESC", (document_id,)
            ).fetchall()
        return [
            Summary(
                row["id"],
                row["document_id"],
                row["style"],
                row["language"],
                row["content"],
                datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def create_chat_room(self, document_id: str, title: str) -> ChatRoom:
        room_id = str(uuid4())
        created_at = _utcnow()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO chat_rooms (id, document_id, title, created_at) VALUES (?, ?, ?, ?)",
                (room_id, document_id, title, created_at.isoformat()),
            )
        return ChatRoom(room_id, document_id, title, created_at)

    def list_chat_rooms(self, document_id: Optional[str] = None) -> list[ChatRoom]:
        with self._connect() as conn:
            if document_id:
                rows = conn.execute(
                    "SELECT * FROM chat_rooms WHERE document_id = ? ORDER BY created_at DESC", (document_id,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM chat_rooms ORDER BY created_at DESC").fetchall()
        return [
            ChatRoom(
                row["id"], row["document_id"], row["title"], datetime.fromisoformat(row["created_at"])
            )
            for row in rows
        ]

    def create_chat_message(self, room_id: str, role: str, content: str) -> ChatMessage:
        msg_id = str(uuid4())
        created_at = _utcnow()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO chat_messages (id, room_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                (msg_id, room_id, role, content, created_at.isoformat()),
            )
        return ChatMessage(msg_id, room_id, role, content, created_at)

    def list_chat_messages(self, room_id: str) -> list[ChatMessage]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM chat_messages WHERE room_id = ? ORDER BY created_at", (room_id,)
            ).fetchall()
        return [
            ChatMessage(
                row["id"], row["room_id"], row["role"], row["content"], datetime.fromisoformat(row["created_at"])
            )
            for row in rows
        ]

    def create_note(self, document_id: str, content: str) -> Note:
        note_id = str(uuid4())
        created_at = _utcnow()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO notes (id, document_id, content, created_at) VALUES (?, ?, ?, ?)",
                (note_id, document_id, content, created_at.isoformat()),
            )
        return Note(note_id, document_id, content, created_at)

    def get_latest_note(self, document_id: str) -> Optional[Note]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM notes WHERE document_id = ? ORDER BY created_at DESC LIMIT 1", (document_id,)
            ).fetchone()
        if not row:
            return None
        return Note(
            row["id"], row["document_id"], row["content"], datetime.fromisoformat(row["created_at"])
        )
