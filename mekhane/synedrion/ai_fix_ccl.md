# AI Audit Fix CCL Program

# Generated: 2026-02-01 by /mek+

# Purpose: 検出された1204件の問題を優先度別に修正

## CCL Expression (v6.45)

```ccl
# 全体パイプライン: 22pt (Standard 帯域内)
let audit_fix = 
  /dia.audit{target=mekhane/}       # 監査実行
    >> F:×4{                         # 4回ループ (Critical→High→Medium→Low)
      /ene.fix{                      # 修正実行
        priority = [critical, high, medium, low][@i],
        autofix = @i <= 2            # Critical/High は自動修正
      }
    }
    >> /sta.verify                   # 検証

# 詳細版: 優先度別の修正パイプライン
let fix_pipeline =
  # Phase 1: Critical (7件) - 即時対応
  /ene.fix+{severity=critical}
    >> V:[:pass]{retry=3}            # 検証ループ
  
  # Phase 2: High (334件) - 自動修正
  >> /ene.fix{severity=high, batch=50}
    >> V:[:pass]{retry=2}
  
  # Phase 3: Medium (264件) - レビュー付き
  >> /ene.fix-{severity=medium}
    >> /dia-                         # クイックレビュー
  
  # Phase 4: Low (599件) - 任意
  >> E:{
    condition = @creator.approve,
    then = /ene.fix-{severity=low},
    else = @skip
  }
```

## 実行手順

### Step 1: Critical 修正 (7件)

```bash
# Dry-run で確認
python mekhane/synedrion/ai_fixer.py mekhane/ --severity critical --dry-run

# 実行
python mekhane/synedrion/ai_fixer.py mekhane/ --severity critical
```

**CCL**: `/ene.fix+{severity=critical}`

### Step 2: High 優先度修正 (334件)

```bash
# bare except → except Exception の一括修正
find mekhane/ -name "*.py" -exec sed -i 's/except\s*:/except Exception:/g' {} \;

# または Python スクリプトで
python mekhane/synedrion/ai_fixer.py mekhane/ --severity high
```

**CCL**: `/ene.fix{severity=high, batch=50}`

### Step 3: Medium 優先度 (264件)

```bash
# Hardcoded paths の検出
grep -rn "'/home/" mekhane/ --include="*.py" | head -20

# 個別に修正 (自動修正は危険)
python mekhane/synedrion/ai_fixer.py mekhane/ --severity medium --dry-run
```

**CCL**: `/ene.fix-{severity=medium} >> /dia-`

### Step 4: Low 優先度 (599件)

```bash
# Magic number は手動レビュー推奨
python mekhane/synedrion/ai_auditor.py mekhane/ 2>&1 | grep "AI-017" | head -20
```

**CCL**: `E:{condition=@creator.approve, then=/ene.fix-}`

## 問題別修正パターン

| Code | 自動修正 | パターン |
|:-----|:--------:|:---------|
| AI-009 | ❌ | Hardcoded secrets → env var 手動 |
| AI-012 | ✅ | `time.sleep` → `await asyncio.sleep` |
| AI-018 | ⚠️ | Hardcoded paths → `Path(__file__).parent` |
| AI-019 | ✅ | Deprecated API → 新しいAPI |
| AI-020 | ✅ | `except:` → `except Exception:` |

## 検証 CCL

```ccl
# 修正後の再監査
/dia.audit{target=mekhane/}
  >> E:{
    condition = @issues.critical == 0 && @issues.high < 100,
    then = @success,
    else = @alert{msg="Remaining issues"}
  }
```

## 期待される結果

| 指標 | Before | After |
|:-----|-------:|------:|
| Critical | 7 | 0 |
| High | 334 | <50 |
| Medium | 264 | <100 |
| Low | 599 | ~500 |
