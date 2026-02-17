# Python 3.11 → 3.13 移行 — 要件書

> **目的**: 全コード・ドキュメント・環境を Python 3.13 に統一
> **環境**: Debian 12 (bookworm), GCP c4-standard-24
> **ステータス**: ✅ 完了 (2026-02-17)

---

## 完了状態

| 項目 | 移行前 | 移行後 |
|:-----|:-------|:-------|
| System Python | 3.11.2 (`/usr/bin/python3`) | 3.13.2 (pyenv) |
| .venv Python | 3.11.2 | 3.13.2 |
| pyproject.toml | `>=3.11` | `>=3.13` |
| pip packages | 209 | 230 (cp313 wheel) |
| ドキュメント | 3.11 言及 ~20箇所 | 全て 3.13 に更新 |
| GitHub Actions | `python-version: "3.11"` | `python-version: "3.13"` |

## テスト結果

- **pytest**: 2684 passed, 15 failed (全て既存問題), 14 skipped
- **boot_integration --mode fast**: Exit code: 0
- **3.13 固有 regression**: **0件**

## 実施手順（記録）

### Step 1: pyenv + Python 3.13.2

```bash
# ビルド依存
sudo apt install -y build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev libncursesw5-dev \
  xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# pyenv (git clone)
curl https://pyenv.run | bash
# ~/.bashrc に追加済み

pyenv install 3.13.2
pyenv global 3.13.2
```

### Step 2: .venv 再構築

```bash
cd ~/oikos/hegemonikon
mv .venv .venv_311_backup
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 3: テスト → PASS

### Step 4: ドキュメント更新 (~20箇所)

更新ファイル: pyproject.toml, GEMINI.md, README.md, 05_creator_profile.md,
Module 19 (3箇所), gcp_linux.md (3箇所), debian_local.md,
post_migration_verification.md, GitHub Actions (4件),
01_environment.md, codex_infra.md (3箇所), ai_tools_config.md

### Step 5: requirements.txt 再固定

```bash
pip freeze > requirements.txt  # 230 packages
```

## ロールバック手順（未使用・backup 削除済み）

```bash
# pyenv で 3.11 に戻す場合:
pyenv install 3.11.2
pyenv global 3.11.2
python3.11 -m venv .venv
pip install -r requirements.txt
```

## 移行後の必須ステップ（教訓）

> **起源**: 2026-02-17 GCP 環境で `git commit` がハング。Python 3.13 venv の
> pre-commit キャッシュが古い Python 3.11 を参照していたことが原因。

### pre-commit キャッシュ再構築（移行後に必ず実行）

```bash
cd ~/oikos/hegemonikon

# 1. 古いキャッシュを完全削除
rm -rf ~/.cache/pre-commit

# 2. pre-commit を新しい venv に再インストール
.venv/bin/pip install --force-reinstall pre-commit

# 3. フック環境をクリーンアップ＋再インストール
.venv/bin/pre-commit clean
.venv/bin/pre-commit install

# 4. 動作確認
.venv/bin/pre-commit run --all-files
```

### 防御的 `.bashrc` 設定

```bash
# 対話プロンプト待ちによるハングを防止
export GIT_TERMINAL_PROMPT=0
```
