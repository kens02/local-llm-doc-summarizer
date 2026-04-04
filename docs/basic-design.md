# 基本設計

## システム概要
ローカル環境でドキュメントを要約し、チャットで対話できるサービス。

## 目的
- 1分程度で読める要約提供
- 内容の対話的な確認
- NotebookLM風の簡易ノート化

## スコープ
- 対象: txt / md / pdf / docx
- 言語: 日本語 / 英語 / 中国語
- 実行: ローカル

## 用語定義
- ドキュメント: 取り込んだファイルの本文
- ノート: NotebookLM風の見出し + 要点

## 機能一覧
- ファイル取り込み
- 要約生成（箇条書き/文章）
- ノート生成
- チャット（履歴保存・再開）

## 非機能要件整理
- 10ページ相当で30秒以内の要約
- チャット応答3秒以内を目標
- ローカル永続化

## 全体構成図
Browser → FastAPI → SQLite / Local LLM

## 技術選定理由
- FastAPI: API開発効率と型ヒント
- SQLite: ローカル運用に最適
- Ollama: ローカルLLM実行基盤として簡便

## コンポーネント構成
- Frontend: React UI
- Backend: API + Usecases
- Infra: SQLite, LLM, Parser

## 外部依存
- Ollama (ローカル実行)
- Pythonライブラリ: pypdf / python-docx

## 制約事項
- 外部クラウドAPIには依存しない
