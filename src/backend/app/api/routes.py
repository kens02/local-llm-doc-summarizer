import logging
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.infra.llm_client import LLMClient, LLMError
from app.infra.parsers import FileParserError
from app.infra.repository import SqliteRepository
from app.schemas.requests import ChatMessageRequest, ChatRoomRequest, NotesRequest, SummaryRequest
from app.schemas.responses import (
    ChatMessageResponse,
    ChatRoomResponse,
    DocumentResponse,
    NotesResponse,
    SummaryResponse,
)
from app.usecases.chat import create_room, send_message
from app.usecases.ingest import ingest_document
from app.usecases.notes import generate_notes
from app.usecases.summarize import summarize_document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


def _repo() -> SqliteRepository:
    return SqliteRepository()


def _llm() -> LLMClient:
    return LLMClient()


@router.post("/documents/import", response_model=DocumentResponse)
async def import_document(file: UploadFile = File(...), language: str = settings.default_language):
    if not file.filename:
        raise HTTPException(status_code=400, detail="ファイル名が不正です")

    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail="ファイルサイズが大きすぎます")

    try:
        document_id = ingest_document(_repo(), file.filename, data, language)
    except FileParserError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return DocumentResponse(id=document_id, filename=file.filename, language=language)


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents():
    repo = _repo()
    docs = repo.list_documents()
    return [DocumentResponse(id=d.id, filename=d.filename, language=d.language) for d in docs]


@router.post("/summaries", response_model=SummaryResponse)
async def create_summary(request: SummaryRequest):
    try:
        content = summarize_document(
            _repo(),
            _llm(),
            request.document_id,
            request.style,
            request.language,
            request.reading_time_sec,
        )
    except LLMError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return SummaryResponse(content=content)


@router.get("/summaries", response_model=list[SummaryResponse])
async def list_summaries(document_id: str):
    repo = _repo()
    summaries = repo.list_summaries(document_id)
    return [SummaryResponse(content=s.content) for s in summaries]


@router.post("/chat/rooms", response_model=ChatRoomResponse)
async def create_chat_room(request: ChatRoomRequest):
    try:
        room_id = create_room(_repo(), request.document_id, request.title)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ChatRoomResponse(id=room_id, document_id=request.document_id, title=request.title)


@router.get("/chat/rooms", response_model=list[ChatRoomResponse])
async def list_chat_rooms(document_id: str | None = None):
    rooms = _repo().list_chat_rooms(document_id)
    return [ChatRoomResponse(id=r.id, document_id=r.document_id, title=r.title) for r in rooms]


@router.post("/chat/rooms/{room_id}/messages", response_model=ChatMessageResponse)
async def post_message(room_id: str, request: ChatMessageRequest):
    try:
        answer = send_message(_repo(), _llm(), room_id, request.message, request.language)
    except LLMError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ChatMessageResponse(role="assistant", content=answer)


@router.get("/chat/rooms/{room_id}/messages", response_model=list[ChatMessageResponse])
async def list_messages(room_id: str):
    messages = _repo().list_chat_messages(room_id)
    return [ChatMessageResponse(role=m.role, content=m.content) for m in messages]


@router.post("/notes", response_model=NotesResponse)
async def create_notes(request: NotesRequest):
    try:
        content = generate_notes(_repo(), _llm(), request.document_id, request.language)
    except LLMError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return NotesResponse(content=content)


@router.get("/notes/{document_id}", response_model=NotesResponse)
async def get_notes(document_id: str):
    note = _repo().get_latest_note(document_id)
    if not note:
        raise HTTPException(status_code=404, detail="ノートがありません")
    return NotesResponse(content=note.content)
