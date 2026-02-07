# Claude Code "Skills" ── AIの振る舞いを「仕様で定義」する、チーム開発の新常識

> **Source**: https://note.com/tasty_dunlin998/n/n17d2978623cd
> **Published**: 2026-01-19T14:11:02+09:00
> **Collected**: 2026-02-06T21:35:28.232214

---

TL;DRClaude Code Skills は、`SKILL.md` を含むフォルダとしてAIの振る舞いを定義し、Git管理可能にする仕組みである。

Progressive Disclosure （段階的開示）により、コンテキストを圧迫せず、必要な時だけスキルが読み込まれる。

チーム開発において、「誰が実行しても同じ品質」を実現するプロンプトのポータビリティが鍵となる。

用語: 本記事では、Skills＝機能全体、Skill＝個別の`<skill-name>/SKI
