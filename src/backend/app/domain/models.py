from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Document:
    id: str
    filename: str
    content: str
    language: str
    created_at: datetime


@dataclass(frozen=True)
class Summary:
    id: str
    document_id: str
    style: str
    language: str
    content: str
    created_at: datetime


@dataclass(frozen=True)
class ChatRoom:
    id: str
    document_id: str
    title: str
    created_at: datetime


@dataclass(frozen=True)
class ChatMessage:
    id: str
    room_id: str
    role: str
    content: str
    created_at: datetime


@dataclass(frozen=True)
class Note:
    id: str
    document_id: str
    content: str
    created_at: datetime


@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    chunk_index: int
    content: str


@dataclass(frozen=True)
class ChatReply:
    answer: str
    citations: Optional[list[str]] = None
