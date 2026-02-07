# 開発も記事生成も、AIは「ハーネス」で強くなる

> **Source**: https://note.com/tasty_dunlin998/n/n1247ca8e8dc2
> **Published**: 2025-12-23T10:44:11+09:00
> **Collected**: 2026-02-06T21:35:28.235326

---

Claude CodeのSkills/Hooks/Subagentsで“再現性”を資産化する設計

生成AIを日常運用していると、最初はうまくいっても、次第にこう感じ始めます。

返答の品質が日によってブレる

途中から会話が汚れて、意図と違う方向へ行く

「毎回同じこと」を言い直している

そして、手順・ノウハウが資産にならない

ここで効いてくるのが「ハーネス（harness）」という発想です。
Anthropicは、Claude Agent SDKを 汎用の“agent
