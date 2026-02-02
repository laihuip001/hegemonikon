# Forge 設計思想の歴史的経緯

**記録日時**: 2026-01-21T15:35:00+09:00
**セッションID**: aad63313-efd1-4318-9509-98e8ff7520b6

---

## 当初の設計思想

Forgeの設計思想は以下だった:

1. **Antigravityでプロンプトを生成する**（そのための `prompt-lang`）
2. **GitHub & Obsidianに保存・同期する**
3. **Androidからでも使える機構を作る**

```
Antigravity → prompt-lang → プロンプト生成
                ↓
        GitHub + Obsidian 同期
                ↓
        Android からもアクセス可能
```

---

## 現状の問題

- **Forgeは活用すべき資産**だが、ライブラリの質が悪い
- `M:\Brain\03_📚_知識｜Knowledge\Forge\` に42個のプロンプトモジュールがあるが、未整備
- 実際には **アーカイブにあるプロンプトモジュール** を使用している

---

## OMEGAの経緯

1. **軍事級メタシステムプロンプト「OMEGA」** を設計・構築
2. OMEGAで「1つずつプロンプトを整備する」計画だった
3. **しかし**: OMEGA自体が M-Series と `GEMINI.md` に統合されてしまった
4. 結果: 個別プロンプト整備は未着手のまま

---

## 未整備のコンポーネント

| コンポーネント | パス | 状態 |
|---------------|-----|------|
| Forgeライブラリ | `M:\Brain\03_📚_知識｜Knowledge\Forge\` | 42個、品質未整備 |
| プロンプト生成Skill | `.agent/skills/meta-prompt-generator/` | 存在するが内容未整備 |
| prompt-lang | `M:\Hegemonikon\prompt-lang\` | v0.1仕様策定中 |

---

## 方針

- ForgeはForgeとして活用する（資産として眠らせない）
- ただし、全42個を個別ワークフロー化するのは悪手
- **FEP 4段階 × M-Series** でグルーピングし、Brainプロンプトは「Skillの内部リソース」として活用

---

*このコンテキストは M8 Anamnēsis により永続化された*
