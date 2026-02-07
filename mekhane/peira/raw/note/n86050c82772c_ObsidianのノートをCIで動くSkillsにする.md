# ObsidianのノートをCIで動くSkillsにする

> **Source**: https://note.com/tasty_dunlin998/n/n86050c82772c
> **Published**: 2026-01-22T14:43:27+09:00
> **Collected**: 2026-02-06T21:35:28.231841

---

SKILL.md → JSON ManifestをNode/TypeScriptで自動生成し、PRでレビューしてから使う

結論を一文で言うと、Obsidianに書いた手順書やチェックリストをfront-matter付きのSKILL.mdとして管理し、Node/TypeScriptの変換CLIでJSON化してPR運用に乗せると、AIエージェントの振る舞いを「チームの常識」として固定できます。

その結果として得られるメリットは次の3つです。

プロンプト芸のブレが減る
個人の
