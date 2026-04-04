# アーキテクチャ

## 全体像
- フロントエンド: Vite + React(TypeScript)
- バックエンド: FastAPI(Python)
- LLM: ローカル実行基盤(Ollama)をHTTPで呼び出し
- データ永続化: SQLite

## 構成図（テキスト）
[Browser]
  |  HTTP
  v
[FastAPI]
  |  documents/summaries/chat/notes
  v
[SQLite]  [Local LLM]

## 層構造
- API層: FastAPI Router
- ユースケース層: 要約生成・ノート生成・チャット
- ドメイン層: Document/Summary/ChatRoom/ChatMessage
- インフラ層: SQLite, ファイルパーサ, LLMクライアント

## 主要データフロー
1. ファイルアップロード
2. パース → 文書保存 → チャンク生成
3. 要約生成/ノート生成 (LLM)
4. チャット応答 (要約 + 関連チャンクを文脈としてLLMへ)

## セキュリティ/運用
- データはローカル保存
- 外部送信は無し（LLMはローカルのみ）
