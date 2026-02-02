# /mek+ Audit CCL Design

> **Target**: SEL Phase 1 & 2 Implementation
> **Goal**: Generate a CCL command to audit the SEL enhancements.

## S1: Metron (尺度) - 監査スコープ

**対象アーティファクト**:
1. `hegemonikon/mekhane/ccl/sel_validator.py` (Phase 1)
2. `hegemonikon/synergeia/gemini_api.py` (Phase 1)
3. `hegemonikon/synergeia/claude_api.py` (Phase 1)
4. `.agent/workflows/vet.md` (Phase 2)

**監査レベル**:
- **Code Integrity**: ファイル存在、構文エラーなし
- **Functional**: Unit test pass
- **Semantic**: SEL v1.0 要件への準拠 (Bootstrap check)

## S2: Mekhanē (方法配置) - 監査ロジック

監査を 3 段階のパイプラインで構成する。

1. **Static Analysis (`/dia`)**: ファイル構造とコード品質の静的解析。
2. **Dynamic Validation (`/ene`)**: テストスクリプト生成・実行による機能検証。
3. **Compliance Verification (`/vet`)**: SEL 基準に基づく最終監査（L5チェック含む）。

## S3: Stathmos (基準) - 合格条件

- 全ファイルが存在し、import error がないこと
- `sel_validator` が自身を「遵守」と判定できること
- `/vet` が L5 モードで動作すること

## S4: Praxis (実践) - CCL Command Generation

以上の設計に基づき、以下の CCL コマンドを定義する。

```ccl
/dia+ "Metacognitive Audit of SEL Components" \
  |> /ene "Execute Validation Suite: sel_validator_test.py" \
  |> /vet+ "L5 SEL Compliance Check"
```

### Detailed Execution Plan (Implicit in CCL)

1. **/dia+**:
   - `grep` で `sel_validator` のインポート確認
   - `flake8` 等簡易チェック（または目視レビュー）
2. **/ene**:
   - `python -m mekhane.ccl.sel_validator` 実行
   - `python -c "import claude_api; import gemini_api"` 実行
3. **/vet+**:
   - `/vet sel` モードのテスト
   - 最終的な変更の整合性確認

---

## 🚀 Generated CCL Command

以下をコピーして実行:

```bash
/dia+ "Phase 1/2 Artifacts Review" |> /ene "Validate Modules" |> /vet+ "Final SEL Check"
```
