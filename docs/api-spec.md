# API仕様

## エンドポイント一覧
- POST /api/documents/import
- GET /api/documents
- POST /api/summaries
- GET /api/summaries?document_id=
- POST /api/notes
- GET /api/notes/{document_id}
- POST /api/chat/rooms
- GET /api/chat/rooms?document_id=
- POST /api/chat/rooms/{room_id}/messages
- GET /api/chat/rooms/{room_id}/messages

## リクエスト例
### POST /api/summaries
```
{"document_id":"...","style":"bullet","language":"ja","reading_time_sec":60}
```

### POST /api/chat/rooms/{room_id}/messages
```
{"message":"要点を教えて","language":"ja"}
```

## レスポンス例
### POST /api/summaries
```
{"content":"..."}
```

## ステータスコード
- 200: 成功
- 400: 入力エラー
- 404: 対象なし
- 500: LLMエラー

## 認証方式
- なし（ローカル利用を前提）
