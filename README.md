# ドキュメント要約AIサービス

ローカルLLMでドキュメントを要約し、Notebook風ノートとチャット対話を提供するサービスです。

## 機能
- TXT/MD/PDF/DOCX 取り込み
- 1分程度で読める要約（箇条書き/文章）
- Notebook風ノート生成
- チャット履歴保存と再開
- 日本語/英語/中国語対応

## セットアップ
```
./setup.sh
```

## バックエンド起動
```
. .venv/bin/activate
uvicorn app.main:app --reload --app-dir src/backend
```

## フロントエンド起動
```
cd src/frontend
npm run dev
```

## LLM準備（Ollama例）
```
ollama pull llama3.1:8b
ollama serve
```

## 設定
- `.env.example` を参考に環境変数を設定

## テスト
```
. .venv/bin/activate
pytest
```
