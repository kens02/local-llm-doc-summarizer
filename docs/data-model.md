# データ設計

## ER図（テキスト）
Document 1 --- n Summary
Document 1 --- n Chunk
Document 1 --- n ChatRoom
ChatRoom 1 --- n ChatMessage
Document 1 --- n Note

## テーブル定義
- documents(id, filename, content, language, created_at)
- document_chunks(id, document_id, chunk_index, content)
- summaries(id, document_id, style, language, content, created_at)
- chat_rooms(id, document_id, title, created_at)
- chat_messages(id, room_id, role, content, created_at)
- notes(id, document_id, content, created_at)

## インデックス戦略
- document_chunks.document_id
- summaries.document_id
- chat_messages.room_id

## 正規化方針
- 3NFを維持

## トランザクション方針
- 1ユースケース内で必要最小限のトランザクション
- 取り込み時は document + chunks を同一操作で作成
