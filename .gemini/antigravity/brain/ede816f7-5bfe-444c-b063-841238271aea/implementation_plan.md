# 構造的強制と自動テストの設計

> **原則**: セルフチェックは信用できない。構造と検証で担保する。
> **知性**: 強制の程度はスケールに応じて調整する。

---

## 1. 設計思想

### 1.1 信頼性の階層

| レベル | 手法 | 信頼度 | 適用場面 |
|:-------|:-----|:-------|:---------|
| L1 | セルフチェック | 低 | 使わない |
| L2 | 構造的強制 | 中 | デフォルト |
| L3 | 自動テスト | 高 | 重要出力 |
| L4 | 外部検証 | 最高 | 重大判断 |

### 1.2 知性による調整

**スケール（S1 Metron）に応じて強制程度を調整**:

| Scale | 強制レベル | 理由 |
|:------|:-----------|:-----|
| 🔬 Micro | L2 最小 | 小タスクに儀式は過剰 |
| 🔭 Meso | L2 標準 | バランス |
| 🌍 Macro | L3 厳格 | 大きな影響には厳格な検証 |

---

## 2. 構造的強制（L2）

### 2.1 必須フィールド定義

**/mek 出力に必須のセクション**:

| フィールド | SE原則 | 検証方法 |
|:-----------|:-------|:---------|
| `## 失敗シナリオ` | 早期失敗 | セクション存在チェック |
| `→ 初版` マーカー | 反復 | 文字列検出 |
| `⏱️ 所要時間` | タイムボックス | 数値抽出 |

**/s 出力に必須のセクション**:

| フィールド | SE原則 | 検証方法 |
|:-----------|:-------|:---------|
| `STAGE 0-5` 全出力 | 可視化 | 6セクション存在 |
| `Keep/Problem/Try` | 継続改善 | 3項目存在 |
| `⏱️ 合計時間` | タイムボックス | 数値抽出 |

### 2.2 強制の実装

**Artifact Standard への追加**:

```yaml
# workflow_artifact_standard.md への追加
required_fields:
  mek:
    - pattern: "## 失敗シナリオ"
      error: "早期失敗原則違反: 失敗シナリオが未記載"
    - pattern: "→ 初版"
      error: "反復原則違反: 初版マーカーがない"
  s:
    - pattern: "STAGE [0-5]:"
      count: 6
      error: "可視化原則違反: 全STAGEの出力がない"
    - pattern: "Keep:|Problem:|Try:"
      count: 3
      error: "継続改善原則違反: KPTが不完全"
```

---

## 3. 自動テスト（L3）

### 3.1 検証スクリプト設計

```python
# se_principle_validator.py

from pathlib import Path
import re

class SEPrincipleValidator:
    """SE 5原則の遵守を検証"""
    
    REQUIRED_PATTERNS = {
        'mek': {
            'fail_fast': r'##\s*失敗シナリオ',
            'iteration': r'→\s*初版',
            'timebox': r'⏱️.*\d+分',
        },
        's': {
            'visibility': [rf'STAGE\s*{i}:' for i in range(6)],
            'kaizen': [r'Keep:', r'Problem:', r'Try:'],
            'timebox': r'⏱️.*合計.*\d+分',
        }
    }
    
    def validate(self, filepath: Path, workflow: str) -> list[str]:
        """検証して違反リストを返す"""
        content = filepath.read_text()
        violations = []
        
        patterns = self.REQUIRED_PATTERNS.get(workflow, {})
        for name, pattern in patterns.items():
            if isinstance(pattern, list):
                for p in pattern:
                    if not re.search(p, content):
                        violations.append(f"{name}: {p} not found")
            else:
                if not re.search(pattern, content):
                    violations.append(f"{name}: pattern not found")
        
        return violations
```

### 3.2 実行タイミング

| タイミング | トリガー | アクション |
|:-----------|:---------|:-----------|
| /mek 完了時 | Artifact 保存後 | 自動検証、違反があれば警告 |
| /s 完了時 | Artifact 保存後 | 同上 |
| /bye 実行時 | セッション終了前 | 全 Artifact を一括検証 |

---

## 4. 知性による調整ロジック

### 4.1 スケール判定 → 強制レベル

```python
def determine_enforcement_level(scale: str) -> int:
    """スケールに応じた強制レベルを返す"""
    levels = {
        'micro': 2,  # L2 最小: 必須フィールドのみ
        'meso': 2,   # L2 標準: 必須フィールド + 警告
        'macro': 3,  # L3 厳格: 自動テスト必須
    }
    return levels.get(scale.lower(), 2)
```

### 4.2 例外処理

| 状況 | 対応 |
|:-----|:-----|
| 緊急タスク（K1 Eukairia 高） | L2 に緩和 |
| 学習目的（実験・PoC） | L2 最小 |
| 本番影響あり | L3 強制 |

---

## 5. 変更対象ファイル

| ファイル | 変更 |
|:---------|:-----|
| `workflow_artifact_standard.md` | `required_fields` セクション追加 |
| 新規: `se_principle_validator.py` | 検証スクリプト |
| `mek.md` | Artifact 保存時に検証呼び出し追加 |
| `s.md` | 同上 |

---

## 6. 確認事項

> [!IMPORTANT]
>
> 1. **検証失敗時の挙動**: 警告のみ or ブロッキング？
> 2. **緩和条件**: 緊急時の緩和は自動判定か手動指定か？
> 3. **実装優先度**: validator.py を今作るか、まず Standard 定義のみか？

---

*v1 — 構造的強制と自動テスト設計 (2026-01-31)*
