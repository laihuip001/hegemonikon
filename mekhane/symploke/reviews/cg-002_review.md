# 認知チャンク分析者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **Line 179**: Medium severity - Excessive operations (4 `len()` calls + string formatting in one line)
  ```python
  lines.append(f"  統計: {len(projects)}件 / Active {len(active)} / Dormant {len(dormant)} / Archived {len(archived)}")
  ```
- **Line 683**: Medium severity - Complex string formatting with multiple variables and dictionary lookups
  ```python
  lines.append(f"- {icon} **{name}** [{phase}]: {summary_text}")
  ```
- **Line 685**: Medium severity - Excessive operations (4 `len()` calls + string formatting in one line)
  ```python
  lines.append(f"統計: Active {len(active)} / Dormant {len(dormant)} / Archived {len(archived)} / Total {len(projects)}")
  ```
- **Line 754**: Medium severity - Complex line with nested conditional expression inside f-string
  ```python
  + (f" (≥ {min_chars})" if char_count >= min_chars else f" (< {min_chars}, need {min_chars - char_count} more)"),
  ```
- **Line 826-830**: Medium severity - Extremely complex expression with nested f-strings, conditionals, and joins
  ```python
  "detail": f"Adjunction L⊣R: ε={epsilon_precision:.0%}, Drift={drift:.0%}"
      + (f" (fill_penalty: {fill_remaining} FILL remaining)" if fill_remaining > 0 else "")
      + f" ({', '.join(k for k, v in adjunction_indicators.items() if v)})"
      if epsilon_count > 0
      else f"Adjunction L⊣R: ε=0%, Drift=100% (no context restoration detected)",
  ```

## 重大度
Medium
