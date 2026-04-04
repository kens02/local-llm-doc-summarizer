import { useEffect, useState } from "react";
import {
  createChatRoom,
  createNotes,
  createSummary,
  importDocument,
  listChatMessages,
  listDocuments,
  postChatMessage,
} from "./api";
import { ChatMessage, ChatRoom, DocumentItem } from "./types";

const languageOptions = [
  { value: "ja", label: "日本語" },
  { value: "en", label: "English" },
  { value: "zh", label: "中文" },
];

export default function App() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);
  const [summary, setSummary] = useState<string>("");
  const [notes, setNotes] = useState<string>("");
  const [style, setStyle] = useState("bullet");
  const [language, setLanguage] = useState("ja");
  const [loading, setLoading] = useState(false);
  const [room, setRoom] = useState<ChatRoom | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listDocuments()
      .then(setDocuments)
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!room) return;
    listChatMessages(room.id)
      .then(setMessages)
      .catch((err) => setError(err.message));
  }, [room]);

  const onUpload = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const doc = await importDocument(file, language);
      setDocuments((prev) => [doc, ...prev]);
      setSelectedDoc(doc);
      setSummary("");
      setNotes("");
      setRoom(null);
      setMessages([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "アップロードに失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const onSummarize = async () => {
    if (!selectedDoc) return;
    setLoading(true);
    setError(null);
    try {
      const res = await createSummary(selectedDoc.id, style, language);
      setSummary(res.content);
    } catch (err) {
      setError(err instanceof Error ? err.message : "要約に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const onNotes = async () => {
    if (!selectedDoc) return;
    setLoading(true);
    setError(null);
    try {
      const res = await createNotes(selectedDoc.id, language);
      setNotes(res.content);
    } catch (err) {
      setError(err instanceof Error ? err.message : "ノート生成に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const onCreateRoom = async () => {
    if (!selectedDoc) return;
    setLoading(true);
    setError(null);
    try {
      const res = await createChatRoom(selectedDoc.id, `${selectedDoc.filename} chat`);
      setRoom(res);
      setMessages([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "チャットルーム作成に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const onSendMessage = async () => {
    if (!room || !inputMessage.trim()) return;
    const userMessage: ChatMessage = { role: "user", content: inputMessage };
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    try {
      const res = await postChatMessage(room.id, userMessage.content, language);
      setMessages((prev) => [...prev, res]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "チャット送信に失敗しました");
    }
  };

  const selectedLabel = selectedDoc ? selectedDoc.filename : "未選択";

  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">Local LLM Document Summarizer</p>
          <h1>1分で理解し、対話で深掘りする</h1>
          <p className="lead">
            TXT / MD / PDF / DOCX をローカルLLMで要約し、Notebook風に整理。保存されたチャットで続きを再開できます。
          </p>
        </div>
        <div className="hero-card">
          <h2>ファイル取り込み</h2>
          <input
            type="file"
            accept=".txt,.md,.pdf,.docx"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) onUpload(file);
            }}
          />
          <div className="field">
            <label>言語</label>
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              {languageOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div className="status">現在のドキュメント: {selectedLabel}</div>
          <div className="doc-list">
            {documents.length === 0 ? (
              <div className="status">まだドキュメントがありません</div>
            ) : (
              documents.map((doc) => (
                <button
                  key={doc.id}
                  className={`doc-item ${selectedDoc?.id === doc.id ? "active" : ""}`}
                  onClick={() => setSelectedDoc(doc)}
                >
                  {doc.filename}
                </button>
              ))
            )}
          </div>
          {loading && <div className="status">処理中...</div>}
          {error && <div className="error">{error}</div>}
        </div>
      </header>

      <section className="grid">
        <div className="card">
          <h2>要約生成</h2>
          <div className="field">
            <label>スタイル</label>
            <select value={style} onChange={(e) => setStyle(e.target.value)}>
              <option value="bullet">箇条書き</option>
              <option value="text">文章</option>
            </select>
          </div>
          <button className="primary" onClick={onSummarize} disabled={!selectedDoc || loading}>
            要約する
          </button>
          <pre className="output">{summary || "まだ要約はありません"}</pre>
        </div>

        <div className="card">
          <h2>Notebook風ノート</h2>
          <button className="primary" onClick={onNotes} disabled={!selectedDoc || loading}>
            ノートを作成
          </button>
          <pre className="output">{notes || "まだノートはありません"}</pre>
        </div>
      </section>

      <section className="card chat">
        <div className="chat-header">
          <h2>チャット</h2>
          <button className="ghost" onClick={onCreateRoom} disabled={!selectedDoc || loading}>
            ルーム作成
          </button>
        </div>
        <div className="messages">
          {messages.length === 0 ? (
            <div className="empty">まだ会話がありません</div>
          ) : (
            messages.map((m, idx) => (
              <div key={idx} className={`bubble ${m.role}`}>
                <span className="role">{m.role}</span>
                <span>{m.content}</span>
              </div>
            ))
          )}
        </div>
        <div className="composer">
          <input
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="質問を入力してください"
            disabled={!room}
          />
          <button className="primary" onClick={onSendMessage} disabled={!room || loading}>
            送信
          </button>
        </div>
      </section>
    </div>
  );
}
