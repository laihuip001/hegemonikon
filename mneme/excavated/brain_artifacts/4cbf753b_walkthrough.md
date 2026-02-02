# Walkthrough - Import Rules and Workflows

## Changes
### Imported Workflows
The following files were imported from `G:\その他のパソコン\太郎` to `c:\Users\raikh\.gemini\.agent\workflows`:

- `do.md`: Session initialization workflow
- `flow-dev-ecosystem.md`: Ecosystem architecture definition
- `global-rules.md`: Global workspace rules (Protocol G, D, D-Extended)
- `update-manual.md`: Manual update procedure

## Verification Results
### Automated Verification
- [x] Directory `c:\Users\raikh\.gemini\.agent\workflows` created.
- [x] All 4 markdown files exist in the destination.
- [x] Content of `global-rules.md` matches the source.

### Refinement
The following adjustments were made to match the current environment:

- **`do.md`**: Updated `GEMINI.md` path to `C:\Users\raikh\.gemini\GEMINI.md`.
- **`global-rules.md`**: Updated scope path to `c:\Users\raikh\.gemini\`.
- **`flow-dev-ecosystem.md`**: Updated model names (Gemini 2.0 Flash, Claude 3.5 Sonnet) and removed outdated references.

---

## Phase 2: Environmental Safeguards

### Kernel Doctrine (GEMINI.md)
Created [GEMINI.md](file:///c:/Users/raikh/.gemini/GEMINI.md) with the **「意志より環境」(Environment over Will)** principle:

| 概念 | 説明 |
|---|---|
| **意志** | 内部チェックリスト（守れない可能性がある） |
| **環境** | 強制的な手続き（ツール実行は記録に残る） |

**核心的認識:**
> 「自分を信じない」ことが、最も信頼できる自分を作る

### Protocol V (global-rules.md)
Added [Protocol V: バージョン検証](file:///c:/Users/raikh/.gemini/.agent/workflows/global-rules.md#L107) as a **forced procedure**:

- **トリガー**: バージョン番号、モデル名、リリース年月
- **強制手順**: `search_web` を実行 → 検索結果に基づき出力 → ソースを明記
- **禁止**: 未検証での推測、学習データへの過信

---

## Phase 3: Human Error Prevention Protocols (P1-P9)

人間のミス対策フレームワークをAIエージェント用に転用:

| Protocol | 名称 | 出典 |
|---|---|---|
| P1 | Failure Classification | Swiss Cheese Model |
| P2 | Error Taxonomy | CREAM |
| P3 | Root Cause Drilling | 5 Whys |
| P4 | Forcing Function | Poka-Yoke |
| P5 | Redundancy Check | Double-Check |
| P6 | Bias Countermeasures | 認知バイアス研究 |
| P7 | Structured Decision | FORDEC, Checklist |
| P8 | Near-Miss Reporting | ヒヤリハット報告 |
| P9 | Post-Action Review | AAR, RCA, Fishbone |

**重要な設計判断:**
- 「報酬を感じる」メカニズムは採用しなかった（LLMには主観的体験がないため機能しない）
- 代わりに「反証探索の強制手順化」(P6-A) で対応

**実装ファイル:** [global-rules.md](file:///c:/Users/raikh/.gemini/.agent/workflows/global-rules.md)



