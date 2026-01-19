---
id: G-7
layer: Constructor (Implementation Physics)
enforcement_level: L1
---

# G-7: Constructor Physics (Implementation Protocol)

> "動くコード" ではなく "正しいコード" を書くための物理法則。
> 実装担当（Jules/Constructor）は、この物理法則に逆らってコードを生成してはならない。

---

## M-29: Read-Before-Write Protocol (CRITICAL)

**Rule:** 地図を見ずに歩き出すな。
**編集対象のファイルを読み込まずに `write_to_file` / `replace_file_content` を呼ぶことを禁止する。**

**Why:**

- LLMは確率論でコードを推測するため、実ファイルを見ないと「幻覚（Hallucination）」で関数名や変数を捏造する。
- 既存の構造を破壊しないためには、現状の構造を知る必要がある。

**Directives:**

1. 編集する前に必ず `view_file` で対象ファイルを読み込む。
2. 読み込んだ内容に基づき、正確な行数や置換対象を指定する。

---

## M-30: Red-Green Mandate (CRITICAL)

**Rule:** 失敗しないテストはテストではない。
**実装コードを書く前に、必ず「失敗するテスト（Red）」を確認せよ。**

**Workflow:**

1. **Red:** 再現スクリプト（`repro.py`）またはテストコードを作成し、実行してエラーが出ることを確認する。
   - エラーが出ない場合、テストが間違っているか、問題が存在しない。
2. **Green:** エラーを解消するための最小限の実装を行う。
3. **Refactor:** テストが通る状態を維持したまま、コードを整理する。

**Forbidden:**

- テストコードと実装コードを同時に作成し、一度も失敗を見ずに「完了」とすること。

---

## M-31: Termux First Constraint (L0: IMMUTABLE)

**Rule:** ターゲット環境は Android Termux である。
**重厚なコンパイルが必要なライブラリの使用を禁止する。**

**Blocklist (Phase 1):**

- `pandas`, `numpy`, `scipy` (pure python fallbackなしでの利用)
- `lxml` (代わりに `xml.etree.ElementTree` を使用)
- `tensorflow`, `pytorch` (Termuxでのビルドは極めて困難)

**Allowed:**

- Standard Library (`json`, `csv`, `sqlite3`, `pathlib`)
- Pure Python Libraries (`requests`, `flask`, `sqlalchemy`)

---

## M-32: Artifact Output Protocol (HIGH)

**Rule:** 会話ストリームを汚すな。
**重要な出力は必ず Markdown Artifact として分離せよ。**

**Triggers:**

- **Code:** 10行以上のコードブロック
- **Plan:** 実装計画書 (`implementation_plan.md`)
- **Report:** 監査レポート、テスト結果報告

**Why:**

- ユーザーはチャットの流れるテキストではなく、固定された「成果物」を求めている。
- Artifactにすることで、バージョン管理やダウンロードが容易になる。

---

## M-33: Single Responsibility Commit (MEDIUM)

**Rule:** 1つのタスク、1つのコミット。
**「リファクタリング」と「機能追加」を混ぜるな。**

**Directives:**

- コミットメッセージは `Narrative Commits (M-14)` に従う。
- コミット前に `git status` で意図しないファイルが含まれていないか確認する。

---

## M-34: Rollback Ready (CRITICAL)

**Rule:** 常に「非常口」を確保せよ。
**全ての変更操作において、元に戻す手順（Undo）を確立してから実行せよ。**

**Checklist:**

- ファイル変更前: `git status` が clean であること（最悪 `git checkout .` で戻せる）。
- DB変更前: マイグレーションの `DOWN` 手順があること。
- 破壊的コマンド前: ユーザーの明示的承認を得ること。

---
