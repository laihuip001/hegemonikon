# メタプロンプトSKILL統合計画

ClaudeのメタプロンプトSKILL（アーキタイプ駆動設計システム）をForgeプロジェクトの軍事級メタプロンプトシステムに統合する。

---

## User Review Required

> [!IMPORTANT]
> **2つの統合アプローチから選択が必要:**
> 
> | アプローチ | メリット | デメリット |
> |---|---|---|
> | **A: モジュール分離型** | 既存構造を維持、段階的導入可能 | 参照が複雑化 |
> | **B: Hypervisor統合型** | 統一的な制御、強力なガバナンス | 大規模変更 |

> [!WARNING]
> **破壊的変更の可能性:**
> - `The Cognitive Hypervisor Architecture.md` の拡張が必要
> - 新規カテゴリ `modules/meta/` の追加

---

## Proposed Changes

### Component 1: メタプロンプトジェネレーター

プロンプト生成のコア機能を追加。

---

#### [NEW] [🧬 メタプロンプト.md](file:///C:/Users/user/.gemini/Forge/modules/act/create/🧬 メタプロンプト.md)

SKILLの6フェーズワークフローを実装:
1. Intent Crystallization（意図結晶化）
2. Archetype Selection（アーキタイプ選択）
3. Core Stack Assembly（必須技術構成）
4. Situational Augmentation（状況依存技術追加）
5. Anti-Synergy Check（禁忌チェック）
6. Structure Assembly（構造組み立て）

---

### Component 2: アーキタイプ定義

5つのアーキタイプを`knowledge/`に追加。

---

#### [NEW] [archetypes.md](file:///C:/Users/user/.gemini/Forge/knowledge/archetypes.md)

| アーキタイプ | 勝利条件 | 犠牲 |
|---|---|---|
| 🎯 Precision | 誤答率 < 1% | 速度, コスト |
| ⚡ Speed | レイテンシ < 2秒 | 精度（95%許容） |
| 🤖 Autonomy | 人間介入 < 10% | 制御性 |
| 🎨 Creative | 多様性 > 0.8 | 一貫性 |
| 🛡 Safety | リスク = 0 | 有用性 |

---

### Component 3: 品質検証システム

Pre-Mortem検証とFallback階層を統合。

---

#### [NEW] [pre-mortem.md](file:///C:/Users/user/.gemini/Forge/protocols/pre-mortem.md)

Universal Checks（全アーキタイプ共通）とArchetype-Specific Checksを定義:
- 入力異常系（空入力、超長文、言語混在等）
- 敵対的入力（Jailbreak、ロール逸脱誘導等）
- システム境界（知識範囲外、能力範囲外等）

---

#### [MODIFY] [The Cognitive Hypervisor Architecture.md](file:///C:/Users/user/.gemini/Forge/The Cognitive Hypervisor Architecture.md)

新規モジュールをModule Registryに追加:

```xml
<module id="30" name="Archetype_Routing" priority="HIGH">
    <rule>All prompt generation must declare an Archetype before technical selection.</rule>
    <action>Route to appropriate technology stack based on archetype.</action>
</module>

<module id="31" name="Pre_Mortem_Protocol" priority="CRITICAL">
    <rule>Execute Pre-Mortem simulation before finalizing any prompt.</rule>
    <action>Check all Universal and Archetype-Specific vulnerabilities.</action>
</module>
```

---

### Component 4: 変換ルール

曖昧語→具体化変換をプロトコル化。

---

#### [NEW] [transformations.md](file:///C:/Users/user/.gemini/Forge/protocols/transformations.md)

| 曖昧語 | 変換後 |
|---|---|
| 適切に | [条件A]なら[処理X]、[条件B]なら[処理Y] |
| 高品質な | [指標]が[閾値]以上 |
| 必要に応じて | [トリガー条件]を満たした場合のみ |

---

### Component 5: テンプレートライブラリ

3つのテンプレートを`presets/`に追加。

---

#### [NEW] [python-code-reviewer.md](file:///C:/Users/user/.gemini/Forge/presets/python-code-reviewer.md)
#### [NEW] [project-producer.md](file:///C:/Users/user/.gemini/Forge/presets/project-producer.md)
#### [NEW] [ruthless-mirror.md](file:///C:/Users/user/.gemini/Forge/presets/ruthless-mirror.md)

---

## Verification Plan

### Automated Tests

既存の`test-forge.ps1`を使用してモジュール検証:

```powershell
# 全テスト実行
cd C:\Users\user\.gemini\Forge\tests
.\test-forge.ps1 all
```

**期待結果:** 
- 新規モジュールがsyntax/completeness/referenceテストに合格
- 合格率 80%以上を維持

---

### Manual Verification

1. **CLIでのモジュール検索テスト:**
   ```powershell
   cd C:\Users\user\.gemini\Forge
   .\forge.ps1 search archetype
   ```
   - 新規追加の`archetypes.md`が検索結果に表示されることを確認

2. **インデックス再構築テスト:**
   ```powershell
   .\build-index.ps1
   ```
   - エラーなく完了し、`index.json`に新規モジュールが含まれることを確認

3. **Web UI確認:**
   - `file:///C:/Users/user/.gemini/Forge/web/index.html` をブラウザで開き、新規モジュールが表示されることを確認

---

## ファイル一覧

| ファイル | 操作 | 優先度 |
|---|---|---|
| `knowledge/archetypes.md` | 新規作成 | HIGH |
| `modules/act/create/🧬 メタプロンプト.md` | 新規作成 | HIGH |
| `protocols/pre-mortem.md` | 新規作成 | CRITICAL |
| `protocols/transformations.md` | 新規作成 | MEDIUM |
| `presets/python-code-reviewer.md` | 新規作成 | LOW |
| `presets/project-producer.md` | 新規作成 | LOW |
| `presets/ruthless-mirror.md` | 新規作成 | LOW |
| `The Cognitive Hypervisor Architecture.md` | 修正 | HIGH |
