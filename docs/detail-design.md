# 詳細設計

## クラス設計
- SqliteRepository: 永続化・取得
- LLMClient: LLM呼び出し
- Usecases: ingest/summarize/chat/notes

## モジュール設計
- app/api: FastAPIルーティング
- app/usecases: 業務ロジック
- app/infra: 外部依存
- app/domain: エンティティ

## インターフェース仕様
- LLMClient.generate(prompt)
- LLMClient.generate_with_context(messages)
- Repository CRUD

## 処理フロー
- 取り込み → パース → DB保存 → チャンク化
- 要約 → LLM呼び出し → DB保存
- チャット → 直近要約 + 関連チャンク → LLM

## 状態遷移
- Document: 取り込み済み
- Summary: 生成済み
- ChatRoom: 作成済み → メッセージ蓄積

## エラー設計
- パース失敗: 400
- LLM失敗: 500
- 存在しないID: 400/404

## ログ仕様
- LLM呼び出し失敗時にエラー出力

## バリデーション仕様
- 読み時間: 10〜600秒
- ファイルサイズ: MAX_UPLOAD_MB
- スタイル: bullet/text
