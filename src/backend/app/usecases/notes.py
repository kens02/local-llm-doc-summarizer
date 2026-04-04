from app.infra.llm_client import LLMClient
from app.infra.repository import SqliteRepository


def generate_notes(repo: SqliteRepository, llm: LLMClient, document_id: str, language: str) -> str:
    document = repo.get_document(document_id)
    if not document:
        raise ValueError("ドキュメントが見つかりません")

    prompt = (
        "あなたはNotebookLM風のノート作成アシスタントです。\n"
        "以下のドキュメントから、簡易的なノートビューを作成してください。\n"
        "- 形式: 見出し構造 + 要点箇条書き + キーフレーズ\n"
        f"- 出力言語: {language}\n\n"
        "[ドキュメント]\n"
        f"{document.content}\n"
    )

    result = llm.generate(prompt)
    note = repo.create_note(document_id, result.content)
    return note.content
