from app.infra.llm_client import LLMClient
from app.infra.repository import SqliteRepository


def _target_length_hint(language: str, reading_time_sec: int) -> str:
    if language in {"ja", "zh"}:
        chars = int(reading_time_sec * 6)  # 1秒あたり6文字程度
        return f"{chars}文字前後"
    words = int(reading_time_sec * 3.3)  # 1分あたり200語
    return f"{words} words"


def summarize_document(
    repo: SqliteRepository,
    llm: LLMClient,
    document_id: str,
    style: str,
    language: str,
    reading_time_sec: int,
) -> str:
    document = repo.get_document(document_id)
    if not document:
        raise ValueError("ドキュメントが見つかりません")

    length_hint = _target_length_hint(language, reading_time_sec)
    style_label = "箇条書き" if style == "bullet" else "文章"

    prompt = (
        "あなたは要約アシスタントです。以下のドキュメントを要約してください。\n"
        f"- 出力言語: {language}\n"
        f"- 出力スタイル: {style_label}\n"
        f"- 目安の長さ: {length_hint}\n"
        "- 読み手が1分程度で把握できること\n"
        "- 重要な固有名詞・数値は可能な限り残す\n\n"
        "[ドキュメント]\n"
        f"{document.content}\n"
    )

    result = llm.generate(prompt)
    summary = repo.create_summary(document_id, style, language, result.content)
    return summary.content
