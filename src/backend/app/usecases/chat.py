from app.infra.llm_client import LLMClient
from app.infra.repository import SqliteRepository
from app.usecases.chunking import score_chunks


def create_room(repo: SqliteRepository, document_id: str, title: str) -> str:
    room = repo.create_chat_room(document_id, title)
    return room.id


def send_message(
    repo: SqliteRepository,
    llm: LLMClient,
    room_id: str,
    message: str,
    language: str,
) -> str:
    messages = repo.list_chat_messages(room_id)
    if not messages:
        room = None
        rooms = repo.list_chat_rooms()
        for r in rooms:
            if r.id == room_id:
                room = r
                break
        if not room:
            raise ValueError("チャットルームが見つかりません")
        document = repo.get_document(room.document_id)
        if not document:
            raise ValueError("ドキュメントが見つかりません")
    else:
        room = None
        document = None
        for r in repo.list_chat_rooms():
            if r.id == room_id:
                room = r
                document = repo.get_document(r.document_id)
                break
        if not room or not document:
            raise ValueError("チャットルームが見つかりません")

    summaries = repo.list_summaries(document.id)
    summary_text = summaries[0].content if summaries else ""
    chunks = repo.list_chunks(document.id)
    top_chunks = score_chunks(message, [c.content for c in chunks], top_k=3)

    system_prompt = (
        "あなたはドキュメントQAアシスタントです。\n"
        "ユーザーの質問に対して、与えられたドキュメント内容に基づいて回答してください。\n"
        "不明な場合は推測せず、分からないと伝えてください。\n"
        f"回答言語: {language}\n"
    )

    context_prompt = (
        "[要約]\n"
        f"{summary_text}\n\n"
        "[関連セクション]\n"
        + "\n---\n".join(top_chunks)
        + "\n"
    )

    history_messages = []
    for msg in messages:
        role = "assistant" if msg.role == "assistant" else "user"
        history_messages.append({"role": role, "content": msg.content})

    request_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": context_prompt},
        *history_messages,
        {"role": "user", "content": message},
    ]

    reply = llm.generate_with_context(request_messages)
    repo.create_chat_message(room_id, "user", message)
    repo.create_chat_message(room_id, "assistant", reply.content)
    return reply.content
