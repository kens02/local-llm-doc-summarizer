# 技術スタック制約
使用言語：バックエンド -> Python3、フロントエンド -> TypeScript
フレームワーク：FastAPI
DB：SQLite（開発・単独ユーザー想定）
インフラ：ローカル実行（GPU任意、CPUでも可）

# 推奨環境（修正版）
OS：macOS / Linux / Windows (WSL2)
Python：3.11 以上
Node.js：20 LTS
パッケージ管理：uv または poetry、フロントは npm
モデル実行：Local LLM 実行基盤（例: Ollama / llama.cpp）
ストレージ：ローカルファイル + SQLite

# 効率面での代替案（選択肢）
- SQLite が重いワークロードや並列アクセスに弱い場合: PostgreSQL
- ローカル環境のみでは運用が難しい場合: Docker Compose で一式をローカル再現
- 文書量が増え、検索が重くなる場合: ベクトルDB（FAISS / Qdrant）
- LLM 推論が遅い場合: GPU 対応モデルまたは軽量モデルへ切替

# コーディング規約
Lintルール：
- Python: ruff（`E`, `F`, `I`, `UP`, `B`, `SIM`）、formatter は black 相当（ruff format）
- TypeScript: eslint（`@typescript-eslint` + `import`）、formatter は prettier
- 追加: `no-unused-vars` は警告、`no-explicit-any` は許可（暫定）

命名規則：
- Python: `snake_case`（関数・変数）、`PascalCase`（クラス）、定数は `UPPER_SNAKE`
- TypeScript: `camelCase`（変数・関数）、`PascalCase`（クラス/型）、定数は `UPPER_SNAKE`
- ファイル/ディレクトリ: `kebab-case`（TS/フロント）、`snake_case`（Python）
- API: `snake_case` の JSON キーを基本、フロントで `camelCase` 変換

コメント規則：
- 公開関数・重要ロジックは「意図」を短く記述（何をするかではなく、なぜ/前提）
- 自明な処理へのコメントは避ける

# 非機能要件
性能：
- 要約生成: 10ページ相当で30秒以内を目標（ローカルCPU環境）
- チャット応答: 通常質問は3秒以内を目標
- 取り込み: 10MB以内のPDF/Docxは即時パース開始

可用性：
- ローカル単体実行を前提とし、再起動後も履歴/データが保持されること
- エラー時はユーザーに原因と復旧手順を提示

セキュリティレベル：
- データはローカル保存、外部送信しない
- チャット履歴/要約は暗号化オプション検討
- ログに原文全文を残さない（必要最小限のメタ情報）

# 出力優先度
品質重視 / 可読性重視 / 速度重視
