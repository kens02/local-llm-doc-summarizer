from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    language: str


class SummaryResponse(BaseModel):
    content: str


class ChatRoomResponse(BaseModel):
    id: str
    document_id: str
    title: str


class ChatMessageResponse(BaseModel):
    role: str
    content: str


class NotesResponse(BaseModel):
    content: str
