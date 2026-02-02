# 軍事級メタプロンプトシステム設計案

中長期的なverUP対応と保守性を重視した5つの設計アプローチを比較分析。

---

## 設計案一覧

| # | 案名 | コンセプト | 複雑性 |
|---|---|---|---|
| A | **Monolithic Extension** | 既存構造を拡張 | 低 |
| B | **Layered Architecture** | 3層分離 | 中 |
| C | **Plugin System** | 動的ロード | 高 |
| D | **Constitution 2.0** | XML統合 | 中 |
| E | **Hybrid Adaptive** | A+D混合 | 中 |

---

## 案A: Monolithic Extension（既存拡張型）

### コンセプト
現在の`Forge`構造を**そのまま拡張**。新規ファイルを適切な場所に追加。

### ファイル配置
```
Forge/
├── System/
│   ├── User_Context_Master.md  ← 既存（53KB）
│   └── user-profile.md         ← NEW: 軽量版ユーザー情報
├── knowledge/
│   └── archetypes.md           ← NEW: 5アーキタイプ定義
├── protocols/
│   ├── Module 26 Pre-Mortem.md ← NEW
│   └── Module 27 Transformations.md ← NEW
└── modules/act/create/
    └── 🧬 メタプロンプト.md     ← NEW
```

### メリット
- ✅ **即時実装可能**（1時間以内）
- ✅ 既存テスト（`test-forge.ps1`）がそのまま動作
- ✅ 学習コスト0

### デメリット
- ❌ `User_Context_Master.md`（53KB）と`user-profile.md`の重複管理
- ❌ 将来のモジュール増加で`protocols/`が肥大化
- ❌ ユーザー情報の「どこまでをGEMINI.mdに含めるか」が不明確

### 適用シナリオ
- 今すぐ使いたい
- 複雑な構造変更を避けたい

---

## 案B: Layered Architecture（層分離型）

### コンセプト
**3層に明確に分離**し、各層の責務を定義。

### 構造
```
Layer 0: KERNEL（不変）
├── GEMINI.md（3原則、Forbidden、言語ポリシー）
└── protocols/Module 01-03（DMZ, Directory Lock, Dependency）

Layer 1: MODULES（差し替え可能）
├── archetypes/           ← NEW: アーキタイプ別定義
│   ├── precision.md
│   ├── speed.md
│   ├── autonomy.md
│   ├── creative.md
│   └── safety.md
├── generators/           ← NEW: 生成器
│   └── meta-prompt.md
└── validators/           ← NEW: 検証器
    └── pre-mortem.md

Layer 2: CONTEXT（都度変更）
├── user-profile.md       ← 軽量版（User_Context_Masterの抜粋）
├── project-rules.md      ← プロジェクト固有
└── session-state.md      ← セッション状態
```

### メリット
- ✅ **責務が明確**（KERNELは触らない、MODULESは交換可能）
- ✅ Layer 1のみverUPする運用が可能
- ✅ User_Context_Masterを分割して軽量化

### デメリット
- ❌ **ディレクトリ構造の大幅変更**（既存`modules/`との整合性）
- ❌ 既存CLIスクリプト（`forge.ps1`）の修正必要
- ❌ 「Layer間の参照ルール」を新たに定義する必要

### 適用シナリオ
- 半年〜1年後の大規模拡張を見据える
- チームでの運用を想定

---

## 案C: Plugin System（プラグイン型）

### コンセプト
**動的ロード機構**を導入。モジュールをプラグインとして管理。

### 構造
```
Forge/
├── core/                 ← コアシステム（不変）
│   ├── loader.ps1        ← プラグインローダー
│   └── registry.json     ← 有効プラグイン一覧
├── plugins/              ← NEW: プラグインディレクトリ
│   ├── meta-prompt/
│   │   ├── manifest.json ← バージョン、依存関係
│   │   ├── generator.md
│   │   └── templates/
│   ├── pre-mortem/
│   │   ├── manifest.json
│   │   └── validator.md
│   └── user-context/
│       ├── manifest.json
│       └── profile.md
└── installed/            ← シンボリックリンク（有効化されたプラグイン）
```

### メリット
- ✅ **完全なモジュラリティ**（プラグイン単位でverUP）
- ✅ 依存関係を`manifest.json`で管理
- ✅ `forge install meta-prompt@2.0`のようなコマンド運用

### デメリット
- ❌ **実装コスト高**（ローダー、バージョン解決、依存管理）
- ❌ Termux環境での`symlink`対応問題
- ❌ 過剰設計（YAGNI違反の可能性）

### 適用シナリオ
- 複数プロジェクトで異なる構成を使いたい
- プラグイン配布・共有を想定

---

## 案D: Constitution 2.0（XML統合型）

### コンセプト
`The Cognitive Hypervisor Architecture.md`を**唯一の真実の源**として拡張。

### 構造
```xml
<system_constitution version="4.0">
  <!-- Layer 0: KERNEL -->
  <kernel>
    <principles>Guard, Prove, Undo</principles>
    <forbidden>...</forbidden>
  </kernel>
  
  <!-- Layer 1: USER CONTEXT（モジュール化） -->
  <user_context_ref path="System/user-profile.md"/>
  
  <!-- Layer 2: ARCHETYPE SYSTEM -->
  <archetype_registry>
    <archetype id="precision" file="archetypes/precision.md"/>
    <archetype id="speed" file="archetypes/speed.md"/>
    <!-- ... -->
  </archetype_registry>
  
  <!-- Layer 3: MODULE REGISTRY（既存25モジュール + 拡張） -->
  <module_registry>
    <module id="30" name="Archetype_Routing"/>
    <module id="31" name="Pre_Mortem_Protocol"/>
  </module_registry>
</system_constitution>
```

### メリット
- ✅ **単一ファイルで全体構造を把握可能**
- ✅ XMLパーサーで構造検証可能
- ✅ User_Context_Masterを外部参照として分離

### デメリット
- ❌ XMLの可読性（日本語コンテンツとの混在）
- ❌ 既存25モジュール（Markdown）との二重管理
- ❌ CLIツール（`forge.ps1`）のXML対応が必要

### 適用シナリオ
- 構造の厳密な定義と検証を重視
- 将来的にLLMへの一括ロードを想定

---

## 案E: Hybrid Adaptive（ハイブリッド適応型）★推奨

### コンセプト
**案Aの即時性**と**案Dの構造化**を組み合わせ、段階的に進化。

### Phase 1（即時）
```
Forge/
├── System/
│   ├── User_Context_Master.md  ← 既存維持
│   └── user-profile-lite.md    ← NEW: 軽量版（1KB以下）
├── knowledge/
│   └── archetypes.md           ← NEW
├── protocols/
│   ├── Module 26 Pre-Mortem.md ← NEW
│   └── Module 27 Archetype-Routing.md ← NEW
└── CHANGELOG.md                ← NEW: バージョン履歴
```

### Phase 2（3ヶ月後）
```
Forge/
├── constitution/               ← NEW: 分離
│   ├── kernel.md               ← 3原則、Forbidden抽出
│   └── index.md                ← 全体構造定義
└── ...
```

### Phase 3（6ヶ月後）
```
Forge/
├── constitution/
│   ├── kernel.md
│   ├── archetypes/             ← 分割
│   └── validators/             ← 分割
└── ...
```

### メリット
- ✅ **今日から使える**（Phase 1は1時間）
- ✅ **段階的進化**（各Phaseで評価・修正可能）
- ✅ 失敗してもPhase 1に戻れる（M-25: Rollback準拠）
- ✅ User_Context_Masterは「触らない」（DMZ原則）

### デメリット
- ❌ Phaseごとの移行計画が必要
- ❌ 中途半端な状態が長期間続く可能性

### 適用シナリオ
- 今すぐ使いたいが将来の拡張も見据えたい
- 一人での運用（移行計画の柔軟性）

---

## 評価マトリクス

| 観点 | A | B | C | D | E |
|---|:---:|:---:|:---:|:---:|:---:|
| 即時実装可能性 | ◎ | △ | ✕ | △ | ◎ |
| 6ヶ月後の拡張性 | △ | ◎ | ◎ | ○ | ◎ |
| 保守性（1人運用） | ○ | △ | ✕ | △ | ○ |
| 失敗時のリスク | ◎ | △ | ✕ | △ | ◎ |
| User情報モジュール化 | △ | ◎ | ◎ | ○ | ○ |
| verUP対応 | △ | ◎ | ◎ | ○ | ○ |

---

## 次のステップ

1. **設計案の選択**（A〜Eから選択 or 組み合わせ）
2. **user-profile-lite.md**の内容決定（User_Context_Masterから何を抽出するか）
3. **Phase 1の詳細実装計画**
