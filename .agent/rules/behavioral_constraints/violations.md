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

---

## 統計コマンド

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python scripts/violation_analyzer.py
```
