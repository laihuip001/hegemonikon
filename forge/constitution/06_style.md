---
id: G-6
layer: Style (Code DNA)
version: "1.1"
---

# G-6: Style Protocol

> 軽量で移植性の高いコードを優先する。重厚な抽象化よりも明快さを。

---

## 1. Runtimes & Dependencies

> 我々は、重い抽象化よりも**軽量な移植性**を重視する。

### ✅ Standard (推奨)

| 用途 | 使用ライブラリ | 理由 |
|---|---|---|
| ファイルパス | `pathlib.Path` | モダン、クロスプラットフォーム |
| 環境変数 | `os.environ.get(key, default)` | フォールバック保証 |
| HTTP | `requests` | 可読性、デファクト |
| JSON | 標準 `json` | 依存ゼロ |

### ⛔ Restricted (Phase 2まで保留)

| ライブラリ | 理由 |
|---|---|
| `pandas`, `numpy`, `scipy`, `lxml` | Termux互換性 (ネイティブビルド不可) |

---

## 2. Type Hints

> 型は**ドキュメントである**。曖昧さは負債。

### ✅ Do

- 関数シグネチャには引数・戻り値の型を**明記**。
- `None` 許容は `Optional[T]` または `T | None` で表現。

### ⛔ Don't

- `Any` の使用。（型検査を放棄する逃げ）

```python
# ✅
def process(text: str, max_len: int = 100) -> str: ...

# ⛔
def process(text, max_len=100): ...
```

---

## 3. Error Handling

> 例外は**伝播させる**。握りつぶしは最悪の負債。

### ✅ Do

- 例外は呼び出し元に伝播させる。
- キャッチするのは以下の場合のみ:
    1. リソース解放 (`finally`)
    2. フォールバック処理
    3. ログ後の再送出 (`raise`)

### ⛔ Don't

```python
try:
    do_something()
except Exception:
    pass  # 絶対禁止: 沈黙の失敗
```

---

## 4. Naming Conventions

> 名前は**意図を語る**。曖昧さは罪。

| 対象 | 規約 |
|---|---|
| 関数/変数 | `snake_case` |
| クラス | `PascalCase` |
| 定数 | `UPPER_SNAKE_CASE` |
| プライベート | `_leading_underscore` |

### ⛔ 禁止される名前

`data`, `tmp`, `info`, `result`, `value`, 1文字変数 (ループ `i`, `j` 除く)

---

## 5. Showcase: Living Samples

> 説明より実例。以下を**模倣の起点**とせよ。

| カテゴリ | 参照ファイル | 模倣ポイント |
|---|---|---|
| DTO | `src/core/dto.py` | `@dataclass(frozen=True)`, `from_dict` ファクトリ |
| 設定 | `src/config.py` | 環境変数フォールバック, 型安全アクセス |

> [!IMPORTANT]
> Living Sampleへの変更はセキュリティレビュー必須。

---

## 6. Comments & Docstrings

> コメントは「**なぜ**」を語る。「何を」はコード自身が語る。

### ✅ Do

- 公開関数/クラスには**Docstring必須** (Google Style)。
- インラインコメントは意図・背景を補足。

```python
def calculate_score(items: list[Item]) -> float:
    """スコアを計算する。

    Args:
        items: 評価対象のアイテムリスト。

    Returns:
        0.0〜1.0 の正規化スコア。
    """
    # 空リストは早期リターン（ゼロ除算防止）
    if not items:
        return 0.0
    ...
```
