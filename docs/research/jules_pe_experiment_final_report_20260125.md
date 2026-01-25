# Jules PE 実験 — 最終レポート

**実験日**: 2026-01-25
**目的**: Claude と Jules の実行者を区別する方法を調査

---

## 1. 実験結果

### A/B 設定比較

| 実験 | AGENTS.md 設定 | 生成ファイル | 結果 |
|:---|:---|:---|:---|
| A | Jules 最大化 | `experiment_a_jules_max.prompt` | 生成成功 |
| B | Jules 最小化 | `experiment_b_jules_min.prompt` | 生成成功 |
| 差異 | - | - | **なし（完全に同一）** |

### 結論

**AGENTS.md の設定は、ファイル内容に影響を与えなかった。**

---

## 2. Runtime ログ調査

### Perplexity 調査結果

```
期待されるログの場所:
C:\Users\[ユーザー名]\.gemini\antigravity\logs\main.log
```

### 実際の環境

```
C:\Users\makar\.gemini\antigravity\
├── annotations/
├── brain/
├── browser_recordings/
├── code_tracker/
├── context_state/
├── conversations/
├── global_workflows/
├── implicit/
├── knowledge/
├── playground/
├── scratch/
└── (logs フォルダなし)
```

**`logs` フォルダは存在しない。**

---

## 3. 発見事項

### GEMINI.md は適用されている

`C:\Users\makar\.gemini\GEMINI.md` は存在し、以下の記述がある:

```markdown
> [!IMPORTANT]
> **Jules ≠ Claude**: Jules は Gemini Code Assist（外部コーディングAI）。
> このドキュメントは Claude（Antigravity AI）への指示である。
```

**これはユーザーが設定した Kernel Doctrine。適用されている。**

### AGENTS.md（実験用）の問題点

私が作成した `M:\Hegemonikon\AGENTS.md` は:
- 正しい場所ではない可能性がある
- `.agent/rules/*.md` が正しい場所かもしれない
- 記法が Antigravity の期待と異なる可能性がある

---

## 4. 仮説の更新

### 当初の仮説

```
対話 = Claude
ファイル操作 = Jules
```

### 実験結果に基づく更新

| 証拠 | 解釈 |
|:---|:---|
| A/B 設定が同一結果 | 設定が効いていない or 同じ実行者 |
| logs フォルダなし | デバッグ情報が取得できない |
| GEMINI.md は存在 | 適用されている可能性あり |

**結論を出すには情報が不足。**

---

## 5. 次のステップ候補

1. **VSCode Output パネル** で「Antigravity」チャンネルを確認
2. **環境変数** `LOG_LEVEL=debug` で起動して再実験
3. **`.agent/rules/`** フォルダにルールを配置して再実験
4. **Google 公式フォーラム** で質問

---

## 6. 参考資料

- [antigravity_architecture_final_report_20260125.md](file:///M:/Hegemonikon/docs/research/antigravity_architecture_final_report_20260125.md)
- [antigravity_prompt_generation_strategy_20260125.md](file:///M:/Hegemonikon/docs/research/antigravity_prompt_generation_strategy_20260125.md)
- [ask_antigravity_runtime_logs_20260125.md](file:///M:/Hegemonikon/docs/research/ask_antigravity_runtime_logs_20260125.md)
