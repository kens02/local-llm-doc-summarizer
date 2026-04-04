from pydantic import BaseModel, Field


class SummaryRequest(BaseModel):
    document_id: str
    style: str = Field(default="bullet", description="bullet or text")
    language: str = Field(default="ja")
    reading_time_sec: int = Field(default=60, ge=10, le=600)


class ChatRoomRequest(BaseModel):
    document_id: str
    title: str


class ChatMessageRequest(BaseModel):
    message: str
    language: str = Field(default="ja")


class NotesRequest(BaseModel):
    document_id: str
    language: str = Field(default="ja")
