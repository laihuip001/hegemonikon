# NotebookLM「Deep Research」をRAGワークフローに組み込むときの設計図

> **Source**: https://note.com/tasty_dunlin998/n/ndcaeb737cc8e
> **Published**: 2025-12-11T12:26:14+09:00
> **Collected**: 2026-02-06T21:35:28.236680

---

 信頼ソースを守りながら、外部Web調査を最大活用するには

はじめにNotebookLM に「Deep Research」が統合され、
・外部Webの自動調査
・出典付きレポート生成
・各種ファイル形式（Word, Sheets など）対応の拡張

といった機能が使えるようになりました。

一方で、これまで NotebookLM を「自分が信頼できるソースだけを集約する安全な編集室」として使ってきた人にとっては、

Deep Research を使った瞬間に「外部情報まみれ
