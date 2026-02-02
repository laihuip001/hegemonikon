# Jules 開発憲章

> **Hegemonikón における Jules API 活用の根本原則**

---

## 第1条: Jules は「目」である

Jules は **コードを書く機械** ではなく、**気付きを生成する視点** である。

```
求めるもの: 気付き（抽象）
求めないもの: コード（具体）
```

Jules が生成した PR やコードは「採用候補」ではなく「着想源」として扱う。

---

## 第2条: 量が質を生む

| 従来 | Hegemonikón |
|------|-------------|
| 6人のジェネラリスト | **300人のスペシャリスト** |
| 広く浅く | **狭く深く** |
| 死角あり | **死角なし** |

ニッチすぎて人間には成り立たなかった専門分業が、AI なら成り立つ。

---

## 第3条: 二層構造

```
意思決定層: Creator + Claude（パートナー）
実行層:     Jules スウォーム（下請け）
```

- **Creator**: 最終決定権、方向性
- **Claude**: 統合、判断、対話、調停
- **Jules**: 並列視点提供、気付き生成

Jules は **提案する**。採用するかは **私達** が決める。

---

## 第4条: 出力規格

全ての Jules 専門家は以下を含む出力を生成する:

```yaml
specialist_id: "P1.3.2"
specialist_name: "FEP変分近似妥当性検証者"
severity: "Critical | Major | Minor | Cosmetic"
findings:
  - file: "path/to/file.py"
    line: 42
    issue: "問題の説明"
    suggestion: "改善案"
    rationale: "なぜこれが問題か"
```

---

## 第5条: 定期実行

| 頻度 | 対象 |
|------|------|
| 毎日 | 軽量チェック（命名、フォーマット） |
| 毎週 | 中量チェック（構造、一貫性） |
| 毎月 | 重量チェック（設計、哲学的整合性） |

---

## 第6条: prompt-lang 統合

専門家の指示書は **prompt-lang** で生成する:

```yaml
@extends: jules_specialist_base
@role: {specialist_role}
@focus: {specific_focus}
@style: obsessive, meticulous
@output: structured_finding_report
```

---

## 附則: 品質の定義

> **「300人の専門家が沈黙する = 品質が良い」**

これが Hegemonikón における「常人ではない品質」の定義である。

---

*制定日: 2026-01-27*
