# Obsidian×GitHub Actionsで日次コンテンツを自動生成する

> **Source**: https://note.com/tasty_dunlin998/n/ne91578869d52
> **Published**: 2026-01-08T09:19:26+09:00
> **Collected**: 2026-02-06T21:35:28.233433

---

Obsidianはローカル、CIはNode＋Cursorで最小自動配信

この記事でやること毎朝 07:30（JST） に、リポジトリ内のコンテンツを自動生成・更新し、差分があればコミットして配信（または配信準備）まで進める仕組みを作ります。ポイントは「ローカルは自由、CIは最小で堅く」です。

Obsidian: 便利プラグイン（Dataview/Templater等）を好きに使って良い  

CI（GitHub Actions）: frontmatter正規化 → 生成 
