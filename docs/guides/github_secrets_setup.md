# GitHub Secrets 設定手順

## 前提

- GitHub リポジトリ: `hegemonikon`
- P1-P5: 設定済み
- P6: 以下の3つのキーを設定

---

## P6 統合者 — 3アカウント分の設定

GitHub Web UI から設定:

1. **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** をクリック
3. 以下を登録:

### JULES_API_KEY_P6_A

```
AQ.Ab8RN6I_KHu4LZyqOSMqa04OSfpsftx-eOVLFizLFTJ0DuU4dA
```

### JULES_API_KEY_P6_B

```
AQ.Ab8RN6KpRQCDKOtxbwiL0lleZA7-fstJvwwsJWMf2iUQCZ3KgA
```

### JULES_API_KEY_P6_C

```
AQ.Ab8RN6JtzFNxjIh-WJZtloeHGHLhH6uQKAabK6jZSsk_X8JF4w
```

---

## 設定確認チェックリスト

| Secret Name | Status |
|-------------|--------|
| JULES_API_KEY_P1 | ✅ 設定済み |
| JULES_API_KEY_P2 | ✅ 設定済み |
| JULES_API_KEY_P3 | ✅ 設定済み |
| JULES_API_KEY_P4 | ✅ 設定済み |
| JULES_API_KEY_P5 | ✅ 設定済み |
| JULES_API_KEY_P6_A | ⬜ 要設定 |
| JULES_API_KEY_P6_B | ⬜ 要設定 |
| JULES_API_KEY_P6_C | ⬜ 要設定 |

---

## 注意事項

- キーは **コピー＆ペースト** で正確に入力
- 前後の空白に注意
- 登録後は値を再確認できないため、ローカルバックアップを保持
  - バックアップ: `/home/makaron8426/oikos/hegemonikon/.env.jules`
