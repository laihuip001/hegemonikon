# 違反ログ（構造化版）

> パターン認識による自己改善のための構造化違反ログ。
> 各エントリは YAML ブロックで管理され、violation_analyzer.py で自動分析される。

---

## パターン定義

| ID | 名称 | 説明 |
|:---|:-----|:-----|
| `skip_bias` | 知っている→省略 | 「知っているつもり」で参照・確認を省略する |
| `env_gap` | 環境強制なし | ルールはあるが環境的強制がなく守れない |
| `accuracy_vs_utility` | 正確 ≠ 有用 | 正確だが読み手が行動できない出力 |
| `false_impossibility` | できない ≠ やっていない | 未試行を「不可能」と断定 |
| `selective_omission` | 勝手な省略 | 存在するものを「不要」と判断して報告から落とす |
| `stale_handoff` | 古い情報を信じる | Handoff/残タスク表の古い情報を鵜呑みにし、実態を確認せず重複作業する |

---

## エントリ

### V-001: /boot+ 出力堕落

```yaml
id: V-001
date: "2026-02-08"
bc: [BC-1, BC-3]
pattern: env_gap
severity: high
recurrence: false
summary: "/boot+ (detailed) を実行したが、出力は /boot- レベルの圧縮サマリーだった"
root_cause: "boot.md に sel_enforcement がなく、+ の最低要件が環境で未定義"
corrective: "sel_enforcement を boot.md に追加"
lesson: "ルールだけでは守れない。環境で強制する"
```

### V-002: dispatch() 不使用

```yaml
id: V-002
date: "2026-02-08"
bc: [BC-10]
pattern: skip_bias
severity: medium
recurrence: false
summary: "dispatch() を使わず手動実行した"
root_cause: "道具の利用導線がなかった"
corrective: "BC-10 道具利用義務を強化"
lesson: "道具が見えないと使わない"
```

### V-003: WF 定義未読で実行

```yaml
id: V-003
date: "2026-02-08"
bc: [BC-3, BC-10]
pattern: skip_bias
severity: high
recurrence: true
summary: "「知っている」と感じて WF 定義を view_file せずに実行"
root_cause: "知っているつもりバイアス"
corrective: "BC-16 参照先行義務の新設"
lesson: "知っているは参照の代替にならない"
```

### V-004: 不可能断定

```yaml
id: V-004
date: "2026-02-09"
bc: [BC-13, BC-6]
pattern: false_impossibility
severity: high
recurrence: false
summary: "「日本語思考はできない」と断定（確認怠り）"
root_cause: "未試行を不可能と断定"
corrective: "BC-6 に不可能断定チェックを追加"
lesson: "できないとやっていないは違う"
```

### V-005: 読み手不在の出力

```yaml
id: V-005
date: "2026-02-10"
bc: [BC-15]
pattern: accuracy_vs_utility
severity: medium
recurrence: false
summary: "正確なマッピング表だが、読み手が行動できない"
root_cause: "正確性に集中し読み手視点を忘れた"
corrective: "BC-15 他者理解可能性の新設"
lesson: "正確であること ≠ 役に立つこと"
```

### V-006: PJ リスト選択的省略

```yaml
id: V-006
date: "2026-02-10"
bc: [BC-1, BC-7]
pattern: selective_omission
severity: high
recurrence: false
summary: "Boot 報告から dormant/archived の3PJを無断で省略。指摘されてもまだ active のみ表示"
root_cause: |
  1. boot_integration.py の generate_boot_template() が active フィルタ → 出力を無批判に信用
  2. 「active だけ表示すれば十分」という暗黙判断を Creator に確認せず実行
  3. registry.yaml を自分で直接読んで照合しなかった (BC-1 違反)
  4. 指摘されて出力しても同じフィルタ結果をそのまま使った (1回目の反省が不十分)
corrective: |
  - boot_integration.py L574-586 を修正: 全PJを status アイコン付き表示
  - パターン定義に selective_omission を追加
  - 教訓: 「何かを省略する判断」は Creator の判断。自分が勝手にしない
lesson: "省略は暴力。存在するものを見えなくすることは、消すことと同じ"
```

### V-007: 重複作業 (Bou-Ene 随伴再分析)

```yaml
id: V-007
date: "2026-02-11"
bc: [BC-16, BC-1]
pattern: stale_handoff
severity: medium
recurrence: false
summary: |
  bou.md L47-64, ene.md L55-63 に既に実装済みの随伴注釈を、
  /noe+ で丸々再分析した。Creator の「同じ話をしていた気がする」で発覚。
root_cause: |
  1. 57b0835f walkthrough.md の「残りタスク: 統一随伴パターン完遂」を鵜呑みにした
  2. 実装対象の bou.md/ene.md を開かずに作業を開始した (BC-16 違反)
  3. walkthrough は「計画時点」の記録であり、その後の実装を反映していなかった
corrective: |
  - adjunction_status.py を作成: 12ペアの実装状態をWFファイルから自動スキャン
  - 環境で防ぐ: スクリプトを走らせれば実態がわかる
lesson: |
  Handoff/残タスク表は「ある時点のスナップショット」であり、真実ではない。
  真実はファイルの中にある。参照先行 (BC-16) は知識だけでなく状態にも適用される。
  Creator の直感 > 私のトークン消費。
```

---

## 統計コマンド

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python scripts/violation_analyzer.py
```
