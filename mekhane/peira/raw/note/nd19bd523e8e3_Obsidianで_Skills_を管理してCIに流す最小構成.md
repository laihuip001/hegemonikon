# Obsidianで「Skills」を管理してCIに流す最小構成

> **Source**: https://note.com/tasty_dunlin998/n/nd19bd523e8e3
> **Published**: 2026-01-21T11:57:02+09:00
> **Collected**: 2026-02-06T21:35:28.232026

---

（SDLC 要件→設計→実装→レビュー→テスト→リリースまで適用する）

Obsidianに、1ノート=1スキルで「実行可能なSkill定義」を置きます。そのノートを、Dataviewで一覧化し、Templaterで /export/ に CIが読める成果物として吐き出します。結果として、属人化しがちな「判断」「観点」「手順」を、チームの常識として固定できます。

この記事は、読者がそのままコピペして試せるように、フォルダ構成、YAMLスキーマ、Dataview、Templa
