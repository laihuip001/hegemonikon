# Python 3.11 → 3.13 移行 — 要件書

> **目的**: 全コード・ドキュメント・環境を Python 3.13 に統一
> **環境**: Debian 12 (bookworm), GCP c4-standard-24

---

## 現状

- **System**: Python 3.11.2 (Debian 12 デフォルト)
- **venv**: 3.11.2
- **pyproject.toml**: `requires-python = ">=3.11"`
- **ドキュメント言及**: 13箇所 (`grep -r "3.11" --include="*.md" --include="*.toml"`)

## 作業手順

### Step 1: pyenv で 3.13 インストール

```bash
# ビルド依存
sudo apt install -y build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev libncursesw5-dev \
  xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# pyenv
curl https://pyenv.run | bash
# ~/.bashrc に追加:
# export PATH="$HOME/.pyenv/bin:$PATH"
# eval "$(pyenv init -)"

pyenv install 3.13.2
pyenv global 3.13.2
```

### Step 2: .venv 再構築

```bash
cd ~/oikos/hegemonikon
mv .venv .venv_311_backup  # ロールバック用
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **リスク**: LanceDB, ONNX Runtime 等のバイナリパッケージが 3.13 wheel を提供していない可能性。失敗時は `.venv_311_backup` から復元。

### Step 3: テスト実行

```bash
PYTHONPATH=. python -m pytest --tb=short -q
PYTHONPATH=. python mekhane/symploke/boot_integration.py --mode fast
```

### Step 4: ドキュメント更新 (13箇所)

| ファイル | 変更 |
|:---------|:-----|
| pyproject.toml | `>=3.11` → `>=3.13` |
| GEMINI.md | `3.11+` → `3.13` |
| README.md | `Python 3.11` → `Python 3.13` |
| kernel/constitution/01_environment.md | Docker タグ例 |
| mekhane/ergasterion/protocols/Module 19*.md | `python:3.11-slim` → `3.13-slim` (3箇所) |
| mekhane/mcp/project_knowledge/05_creator_profile.md | `3.11+` → `3.13` |
| knowledge_items/.../gcp_linux.md | venv コマンド (3箇所) |
| knowledge_items/.../debian_local.md | venv コマンド |
| knowledge_items/.../post_migration_verification.md | バージョンチェック |

### Step 5: 残存チェック

```bash
grep -rn "3\.11" --include="*.md" --include="*.toml" --include="*.cfg" --include="*.yml" ~/oikos/hegemonikon/
# 0件であること
```

## ロールバック手順

```bash
rm -rf .venv
mv .venv_311_backup .venv
# pyproject.toml を git checkout
```

## 完了条件

1. `python3 --version` → `3.13.x`
2. `.venv/bin/python --version` → `3.13.x`
3. `pytest` 全テスト PASS
4. `boot_integration.py --mode fast` 正常終了
5. `grep -r "3.11"` で文書内の残存 0件
