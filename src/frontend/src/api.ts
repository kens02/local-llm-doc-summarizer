import { ChatMessage, ChatRoom, DocumentItem } from "./types";

const baseUrl = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function listDocuments(): Promise<DocumentItem[]> {
  const res = await fetch(`${baseUrl}/api/documents`);
  if (!res.ok) throw new Error("ドキュメント取得に失敗しました");
  return res.json();
}

export async function importDocument(file: File, language: string): Promise<DocumentItem> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${baseUrl}/api/documents/import?language=${language}`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error("アップロードに失敗しました");
  return res.json();
}

export async function createSummary(documentId: string, style: string, language: string) {
  const res = await fetch(`${baseUrl}/api/summaries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId, style, language, reading_time_sec: 60 }),
  });
  if (!res.ok) throw new Error("要約生成に失敗しました");
  return res.json();
}

export async function createNotes(documentId: string, language: string) {
  const res = await fetch(`${baseUrl}/api/notes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId, language }),
  });
  if (!res.ok) throw new Error("ノート生成に失敗しました");
  return res.json();
}

export async function createChatRoom(documentId: string, title: string): Promise<ChatRoom> {
  const res = await fetch(`${baseUrl}/api/chat/rooms`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId, title }),
  });
  if (!res.ok) throw new Error("チャットルーム作成に失敗しました");
  return res.json();
}

export async function listChatMessages(roomId: string): Promise<ChatMessage[]> {
  const res = await fetch(`${baseUrl}/api/chat/rooms/${roomId}/messages`);
  if (!res.ok) throw new Error("メッセージ取得に失敗しました");
  return res.json();
}

export async function postChatMessage(roomId: string, message: string, language: string) {
  const res = await fetch(`${baseUrl}/api/chat/rooms/${roomId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, language }),
  });
  if (!res.ok) throw new Error("チャット送信に失敗しました");
  return res.json();
}
