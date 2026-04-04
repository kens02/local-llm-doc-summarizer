import io
from typing import Tuple
from pypdf import PdfReader
from docx import Document as DocxDocument


class FileParserError(RuntimeError):
    pass


def parse_text_file(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="ignore")


def parse_pdf_file(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
    except Exception as exc:  # noqa: BLE001
        raise FileParserError("PDFの解析に失敗しました") from exc


def parse_docx_file(data: bytes) -> str:
    try:
        doc = DocxDocument(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs]
        return "\n".join(paragraphs).strip()
    except Exception as exc:  # noqa: BLE001
        raise FileParserError("DOCXの解析に失敗しました") from exc


def parse_file(filename: str, data: bytes) -> Tuple[str, str]:
    lower = filename.lower()
    if lower.endswith(".txt") or lower.endswith(".md"):
        return parse_text_file(data), "text"
    if lower.endswith(".pdf"):
        return parse_pdf_file(data), "pdf"
    if lower.endswith(".docx"):
        return parse_docx_file(data), "docx"
    raise FileParserError("対応していないファイル形式です")
