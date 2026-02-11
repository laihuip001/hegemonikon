---

hegemonikon: Akribeia
modules: [A2]
skill_ref: ".agent/skills/akribeia/a2-krisis/SKILL.md"
version: "2.0"
layer: "τ"
parent: "/dia"
lineage: "A2 Krisis → Epochē 4層プロトコル + Anti-Skip + 3層アーキテクチャ → /epo v2.0"
anti_skip: enabled
---

# /epo: 判断停止ワークフロー (Epochē)

> **正本参照**: [A2 Krisis SKILL.md](file:///home/makaron8426/oikos/.agent/skills/akribeia/a2-krisis/SKILL.md)
> **目的**: LLM の過信 (Overconfidence) を低減し、認識限界で判断を停止する
> **本質**: ἐποχή = 判断保留

---

## 発動条件

| トリガー | 動作 |
|:---------| :----- |
| `/epo` | 現在の出力に Epochē プロトコルを適用 |
| `/dia epo` | /dia から委譲 |
| 自動発動 | 確信度 LOW 検出時に自動適用 |

---

## ⚠️ 実行前必須: 正本読み込み

> **このステップは省略禁止。必ず実行すること。**

```text
実行手順:
1. view_file ツールで SKILL.md を読み込む
   パス: /home/makaron8426/oikos/.agent/skills/akribeia/a2-krisis/SKILL.md
2. Epochē: 判断停止 セクションを確認
3. 4層構造と出力マーカーを確認
4. 確認後、処理を開始
```

---

## 処理フロー

**詳細ロジックと出力形式は SKILL.md「Epochē: 判断停止」セクションに記載**

```text
[STEP 0] SKILL.md を view_file で読み込む ← 必須
  ↓
[層1] Preamble（確信度宣言: HIGH/MEDIUM/LOW）
  ↓
[層2] CoVe 自問（Chain-of-Verification）
  ↓
[層3] 出力マーカー付与
  ↓
[層4] Suspension Gate（判断停止判定）
  ↓
Hollow Detection（形骸化防止チェック）
```

---

## 出力マーカー例

```text
【確信度: HIGH | 根拠: 直接訓練データ】
【確信度: MEDIUM | 根拠: ~の推論に基づく】
【確信度: LOW | 理由: ~についての情報不足】
【判断停止: 是 | 原因: ~の限界に到達】
```

---

## 哲学

> 「知らないことを知っている」— ソクラテス
> 過信は知識の敵である。
> Epochē は謙虚さの制度化である。

---

## Hegemonikon Status

| Module | Workflow | Skill (正本) | Status |
| :------- |:---------|--------------| :------- |
| A2 Krisis | /epo | [SKILL.md](file:///home/makaron8426/oikos/.agent/skills/akribeia/a2-krisis/SKILL.md) | v2.0 Ready |

---

*v2.0 — 3層アーキテクチャ対応 (Skill = 正本)*
