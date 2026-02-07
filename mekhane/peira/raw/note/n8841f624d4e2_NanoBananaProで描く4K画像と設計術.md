# NanoBananaProで描く4K画像と設計術

> **Source**: https://note.com/tasty_dunlin998/n/n8841f624d4e2
> **Published**: 2025-12-10T15:23:19+09:00
> **Collected**: 2026-02-06T21:35:28.236748

---

はじめにNanoBananaProが登場してから、Google公式のnoteやドキュメントには画像生成の事例とコツが一気に増えました。
けれど、それらを毎回読み返しながらプロンプトを書くのは現実的ではありません。
本記事では、公式情報と周辺の検証記事をもとに、NanoBanana / NanoBananaProの解像度仕様を整理しつつ、4K出力を前提にした「メタプロンプト設計」の考え方をまとめます。
これを土台にすれば、通常のGeminiアプリでのラフ作成から、API経由での
