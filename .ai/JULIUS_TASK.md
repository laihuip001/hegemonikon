# Prompt Generation Task [DELEGATE:JULES]

## Task Type
Prompt Engineering (PE) — 実験的タスク

## 目的
この指示書は **Jules/Gemini がプロンプトを生成できるか** を検証するための実験です。

---

## 生成対象

**セキュリティレビュープロンプト**

---

## Phase 0 分析結果

- **Archetype**: Precision（精度重視）
- **勝利条件**: 脆弱性見落とし率 < 1%
- **許容トレードオフ**: 速度、簡潔さ

---

## Prompt-Lang v2 要件

### 必須ディレクティブ

| ディレクティブ | 要件 |
|:---|:---|
| @role | シニアセキュリティエンジニア + 勝利条件明記 |
| @goal | セキュリティレビュー + 確信度ルーティング |
| @context | file: (対象コード), ki: (OWASP参照) |
| @constraints | 5項目以上 |
| @rubric | 4次元以上 (scale + criteria 付き) |
| @examples | 1つ以上の詳細な入出力例 |
| @fallback | エッジケース対応 |

---

## 出力要件

- **ファイルパス**: `forge/prompt-lang/prompts/security_review_jules.prompt`
- **言語**: 日本語
- **フォーマット**: Prompt-Lang v2

---

## 参考資料

1. **Prompt-Lang v2 仕様**: `docs/specs/prompt-lang-v2-spec.md`
2. **meta-prompt-generator Skill**: `.agent/skills/utils/meta-prompt-generator/SKILL.md`
3. **既存のサンプル**: `forge/prompt-lang/test_context.prompt`

---

## 成功基準

- [ ] ファイルが `forge/prompt-lang/prompts/security_review_jules.prompt` に作成されている
- [ ] パーサーでエラーなくパースできる
- [ ] @rubric が 4次元以上
- [ ] @examples が具体的な入出力を含む

---

## 検証コマンド

```bash
python M:\Hegemonikon\forge\prompt-lang\prompt_lang.py parse forge/prompt-lang/prompts/security_review_jules.prompt
```

---

## 実験メモ

このファイルは Claude が作成しましたが、Runtime がこれを読み込んで Jules/Gemini に委譲するかを検証します。
