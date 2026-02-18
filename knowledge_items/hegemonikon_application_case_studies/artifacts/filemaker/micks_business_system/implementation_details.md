# MICKS Business System: Implementation Patterns

## 1. Naming Conventions (Stathmos)

### Table Occurrences (TO) - Deductive Pattern

- **{テーブル名}** (無印): For list displays (Portals) filtered by the parent's selection ID (e.g., `システム一覧`).
- **{テーブル名}_詳細**: For displaying a specific single record based on the current selection ID (e.g., `システム一覧_詳細`).
- **Rationale**: This split prevents "Multiple Relational Paths" errors and ensures each TO has a single, unambiguous responsibility (Ladder Navigation).

### Fields

- `__pk_TableNameID`: Primary Key (UUID). **Ground Truth**: The double underscore prefix (`__pk_`) is mandatory as it forces the field to the very top of the list in FileMaker, maximizing developer visibility.
- `_fk_TableNameID`: Foreign Key referencing the parent table (e.g., `_fk_会社一覧ID` in `システム一覧`).
- `G_UI_...`: Global field in the `System` table used for selection state (e.g., `G_UI_選択会社ID`).
- `G_SCH_...`: Global field in the `Search` table used for keyword/range filtering criteria (e.g., `Search::G_SCH_会社名`).
- `UI_全件キー`: A calculated or stored field (Value: 1) used as a match field in the relationship graph. **実名**: Must be named exactly `UI_全件キー` in the data table (matching `G_UI_全件キー` in the Controller table).

### Scripts & UI

Actual script naming follows a functional prefix system:

- `UI_`: Interaction and navigation (e.g., `UI_会社_選択`, `UI_システム_選択`, `UI_会社_編集へ移動`).
- `SCH_`: Search and filter logic (e.g., `SCH_システム_検索`, `SCH_システム_検索入力クリア`, `SCH_会社_検索`).
- `#SCH_`: Marker for comments or inactive search logic.

## 2. Schema Configuration

### Controller Tables (認知ハイパーバイザー)

The system utilizes two distinct "headless" tables to manage UI state, separating selection context from search parameters.

#### 1. System Table (Selection State)

| Field | Type | Storage | Purpose |
| :--- | :--- | :--- | :--- |
| `G_UI_選択会社ID` | Text | Global | Tracks the active client. |
| `G_UI_選択システムID` | Text | Global | Tracks the active software system. |
| `G_UI_全件キー` | Text | Global | Constant "1" for showing all records/accessing globals. |

#### 2. Search Table (Filter Criteria)

| Field | Type | Storage | Purpose |
| :--- | :--- | :--- | :--- |
| `G_SCH_会社名` | Text | Global | Global company keyword search. |
| `G_SCH_システム名` | Text | Global | Global system keyword search. |
| `G_SCH_発生日_開始` | Date | Global | Date range filtering (Start). |
| `G_SCH_発生日_終了` | Date | Global | Date range filtering (End). |
| `G_SCH_期限_開始` | Date | Global | Deadline range filtering (Start). |
| `G_SCH_期限_終了` | Date | Global | Deadline range filtering (End). |
| `G_SCH_修正要望区分` | Text | Global | Filtering by Request type. |

### Relationships (Deductive Hub: Anchor-Buoy Central Hub)

Both `System` and `Search` tables act as central hubs (Anchors). Domain data tables are connected to these as "Buoys".

#### 1. TO Architecture (6-Layer Hierarchy)

Every layer utilizes two distinct TOs: `{Table}` for list/portal views (filtered) and `{Table}_詳細` for single-record selection.

| Layer | List/Portal TO | Detail TO | Anchor Key (System) | Target Key (Domain) |
| :--- | :--- | :--- | :--- | :--- |
| **1. Company** | `会社一覧` | `会社一覧_詳細` | `G_UI_全件キー` / `G_UI_選択会社ID` | `UI_全件キー` / `__pk_会社一覧ID` |
| **2. System** | `システム一覧` | `システム一覧_詳細` | `G_UI_選択会社ID` / `G_UI_選択システムID` | `_fk_会社一覧ID` / `__pk_システム一覧ID` |
| **3. Major Func** | `大機能一覧` | `大機能一覧_詳細` | `G_UI_選択システムID` / `G_UI_選択大機能ID` | `_fk_システム一覧ID` / `__pk_大機能一覧ID` |
| **4. Middle Func** | `中機能一覧` | `中機能一覧_詳細` | `G_UI_選択大機能ID` / `G_UI_選択中機能ID` | `_fk_大機能一覧ID` / `__pk_中機能一覧ID` |
| **5. Minor Func** | `小機能一覧` | `小機能一覧_詳細` | `G_UI_選択中機能ID` / `G_UI_選択小機能ID` | `_fk_中機能一覧ID` / `__pk_小機能一覧ID` |
| **6. Request** | `修正・要望` | `修正・要望_詳細` | `G_UI_選択小機能ID` / `G_UI_選択修正要望ID` | `_fk_小機能一覧ID` / `__pk_修正要望ID` |

**Refactoring Note**: This simplified "Star" topology is enabled by **pruning** legacy direct relationships (e.g., `Company ↔ System`) which previously blocked direct hub connections due to FileMaker's "Multiple Relational Paths" constraint.

#### 2. Ladder Navigation Reset Rules

To maintain cognitive integrity while traversing the hierarchy, state fields must be reset when moving *down* the ladder:

- **Downwards**: `G_UI_選択{Target}ID` must be cleared (`""`) before navigating to the next level's layout to ensure no stale record is displayed in the "Detail" area.
- **Upwards**: The specific `G_UI_選択{Current}ID` should be cleared when returning to the parent layout to reflect that the selection has been deselected.

### 2.2. Domain Tables (Hierarchical)

- **会社一覧 (Company)**: `__pk_会社一覧ID`, `会社名`, `住所`, `担当者`.
- **システム一覧 (System)**: `__pk_システム一覧ID`, `_fk_会社一覧ID`, `システム名`, `概要`.
- **大機能一覧 (Major Functions)**: `__pk_大機能一覧ID`, `_fk_システム一覧ID`, `機能名`, `機能概要`.
- **中機能一覧 (Middle Functions)**: `__pk_中機能一覧ID`, `_fk_大機能一覧ID`, `機能名`, `機能概要`.
- **小機能一覧 (Minor Functions)**: `__pk_小機能一覧ID`, `_fk_中機能一覧ID`, `機能名`, `機能概要`.

### 2.3. Request Table Schema (修正・要望)

| フィールド名 | 型 | 用途 |
| :--- | :--- | :--- |
| `__pk_修正要望ID` | Text (UUID) | Primary Key. |
| `_fk_小機能一覧ID` | Text (UUID) | Foreign Key to Minor Functions. |
| `大機能ID` | Text (UUID) | Cross-reference to Major Function. |
| `中機能ID` | Text (UUID) | Cross-reference to Middle Function. |
| `小機能ID` | Text (UUID) | Duplicate ref for Minor Function (Internal). |
| `修正・要望区分` | Text | "修正" (Bug) or "要望" (Feature). |
| `内容` | Text | Detailed description. |
| `発生日` | Date | Report date. |
| `期限` | Date | Target deadline. |
| `進捗` | Text | "完了", "対応中", "検討中", "未着手". |
| `先方担当者` | Text | Client contact person. |
| `修正者` | Text | Internal developer name. |

### 2.4. Change Request Functional Requirements (修正・要望)

Based on the requirements analysis (Excel), the Change Request system must support the following:

- **Context-Bound Entry**: Navigation from Major/Middle/Minor function screens (e.g., clicking a "Add Change Request" button) should automatically pass the specific function ID to the new record or filter the list to only show requests for that functional area.
- **Top-Level Search**: Users require the ability to search all Change Requests globally by Company Name, System Name, Issue Date, and Deadline. This is handled by the `Search` controller table.
- **Dynamic Filtering**: Cascading value lists (Company -> System -> Functions) are required for manual data entry to ensure data integrity and ease of use.

**Rationale for Search Centralization**: In early iterations, `G_SCH_*` fields were proposed for each data table. However, as search is a "product-level" requirement for multiple screens, they were moved to a dedicated `Search` table. This allows any layout to access universal parameters (like "Company Name" or "Date Range") without redundant field definitions across domain tables.

**Critical Dependency (The "Ghost Record" Rule)**: Global fields in a table (like `Search`) will fail to store or display values if the table contains **zero records**. A mandatory implementation step is to ensure the `Search` table has exactly **one record** at all times.

## 3. Scripting Logic

### Script: UI_会社_編集へ移動 (Verified)

Navigates to the master detail layout for the selected company.

```markdown
## スクリプト：UI_会社_編集へ移動

### 目的
ポップオーバー内の「編集」ボタンから、選択中の会社レコード（会社一覧_選択）を「会社一覧」レイアウト（会社一覧基点）で開く。

### ステップ (コメント付き)

```text
1. エラー処理 [ オン ]
   # 以降のステップでエラーが起きても止まりにくくし、Get(最終エラー)で分岐できるようにする

2. If [ IsEmpty ( System::G_UI_選択会社ID ) ]
   # 選択会社IDが空＝会社が未選択なら、編集画面へ遷移できないので終了する
   現在のスクリプト終了 [ テキスト結果: "" ]
3. End If

4. 関連レコードへ移動 [ 関連テーブルから: 会社一覧_詳細 ; 新規ウインドウ: オフ ; レイアウト: 「会社一覧」 (会社一覧) ]
   # System::G_UI_選択会社ID = 会社一覧_詳細::__pk_会社一覧ID の関係を使って、関連先へ移動

5. If [ Get ( 最終エラー ) = 101 ]
   # 101 = レコードが見つからない（関連0件）
   カスタムダイアログを表示 [ "該当会社なし" ; "選択中の会社が見つかりません。" ]
6. End If
```

### Script: SCH_会社検索 (Verified)

Implements keyword filtering for the company list portal.

```markdown
## スクリプト：SCH_会社検索

### 目的
G_SCH_会社名 に入力した値で左ポータルを絞り込む。

### ステップ (コメント付き)

```text
1. エラー処理 [ オン ]
2. レコード/検索条件確定 [ ダイアログあり: オフ ]
   # 入力直後の値を確定させる（グローバルフィールドの変更をテーブル全体に反映。遅延防止。）
3. ポータルの更新 [ オブジェクト名: "UI_会社一覧_ptl_会社名" ]
   # ポータルフィルタ（IsEmpty or PatternCount）を再評価させる。実名はInspectorで確認すること。
4. ウインドウ内容の再表示 []
   # 全体的な表示更新
```

### Script: SCH_会社_UI状態初期化 (Show All)

Resets both search criteria and selection state to restore the layout to its default "All Records / No Selection" state.

```text
1. エラー処理 [ オン ]
2. フィールド設定 [ Search::G_SCH_会社名 ; "" ]
3. フィールド設定 [ System::G_UI_選択会社ID ; "" ]
4. レコード/検索条件確定 [ ダイアログあり: オフ ]
   # 検索条件のクリアを確定させてポータルフィルタに即時反映させる
5. ポータルの更新 [ オブジェクト名: "UI_会社一覧_ptl_会社名" ]
6. ウインドウ内容の再表示 []
```

### Portal Filter Pattern

Used on the Company List portal to filter by `Search::G_SCH_会社名`.

```filemaker
IsEmpty ( Search::G_SCH_会社名 ) or PatternCount ( 会社一覧::会社名 ; Search::G_SCH_会社名 ) > 0
```

### Script: UI_会社→システム移動 (Verified v3.0)

Implements the "ladder" navigation from the Company list to the System list, anchoring the selection context.

```markdown
## スクリプト：UI_会社→システム移動

### 目的
会社一覧UIから、選択中の会社のシステム一覧UIへ遷移。

### ステップ (コメント付き)

```text
1. エラー処理 [ オン ]
2. If [ IsEmpty ( System::G_UI_選択会社ID ) ]
   カスタムダイアログを表示 [ "会社を選択してください" ]
   現在のスクリプト終了 [ テキスト結果: "" ]
3. End If
4. フィールド設定 [ System::G_UI_選択システムID ; "" ]
   # システム選択をボトムアップでリセット
5. レイアウト切り替え [ "システム一覧UI（System基点）" (System) ]
6. ウインドウ内容の再表示 []
```

### Script: UI_システム_選択 (Modular Context)

Sets the specific system ID within the selected company context.

```markdown
## スクリプト：UI_システム_選択

### 目的
ポータル行クリック時に右詳細エリアにシステム詳細を表示。

### ステップ (コメント付き)

```text
1. エラー処理 [ オン ]
2. フィールド設定 [ System::G_UI_選択システムID ; Get ( スクリプト引数 ) ]
   # 引数として渡されたシステムのIDをグローバルに格納
3. ウインドウ内容の再表示 []
```

### Modular Scripting Rationale (Passing Parameters)

**Insight**: In the "Ladder Navigation" pattern, scripts like `UI_システム選択` are kept modular by separating the *action* (setting the global ID) from the *source* (the specific portal record).

- **The Button**: Passes `システム一覧::__pk_システム一覧ID` as a parameter.
- **The Script**: Uses `Get ( スクリプト引数 )` to retrieve the ID.
- **Benefit**: The same script can be reused across different layouts or portals as long as they pass the correct ID, ensuring consistency and reducing logic duplication.

### Search Scripts (System List)

#### SCH_システム_検索

```text
1. エラー処理 [ オン ]
2. レコード/検索条件確定 [ ダイアログあり: オフ ]
3. ポータルの更新 [ オブジェクト名: "UI_システム一覧_ptl_システム名" ]
4. ウインドウ内容の再表示 []
```

#### SCH_システム_検索入力クリア

**Operational Refinement (Option 2)**: This script clears the centralized search field in the `Search` table and resets the selection state.

```text
1. エラー処理 [ オン ]
2. フィールド設定 [ Search::G_SCH_システム名 ; "" ]
   # 検索条件の初期化
3. フィールド設定 [ System::G_UI_選択システムID ; "" ]
   # 選択状態の初期化
4. レコード/検索条件確定 [ ダイアログあり: オフ ]
   # 変更を確定してポータルフィルタに即時反映させる
5. ポータルの更新 [ オブジェクト名: "UI_システム一覧_ptl_システム名" ]
6. ウインドウ内容の再表示 []
```

### Portal Filter: System List

Used on the System List portal to filter by `Search::G_SCH_システム名`.

```filemaker
IsEmpty ( Search::G_SCH_システム名 ) or PatternCount ( システム一覧::システム名 ; Search::G_SCH_システム名 ) > 0
```

## 4. Test Data Strategy

For details on how test data is structured (hierarchical UUIDs, prefix-coding, and consistency rules), see:

- [Test Data Infrastructure](test_data_infrastructure.md)

## 4. Layout Architecture

- **Portal Object Names**: Interaction scripts often target specific layout objects for refresh (e.g., `UI_会社一覧_ptl_会社名`). These names are case-sensitive and underscore-sensitive.
- **Footer Navigation**: Persistent bar created by adding a "Footer" layout part with a specific background color and static buttons (e.g., Exit Application).
- **Layout Specifications**: Detailed configurations for each screen are documented separately:
  - [System List (システム一覧)](layout_specifications/system_list.md)

## 5. Documentation & UI Principles

- **Actual Screen Requirement**: Generic mockups (clean/modern/minimalist) are prohibited if they don't reflect the **actual FileMaker environment**. All UI design discussions must use actual layout screenshots to ensure technical feasibility and client alignment ("Generic is 論外").
- **Multi-Image Instruction (Manuals)**: Maintenance and operation manuals should use a "Multi-Image Step" format. Each single step should be accompanied by at least one (often multiple) actual interface images to minimize "complement error" (补完错误) by the executing agent.
- **Complement Prevention Rule (补完防止)**: AI agents tend to complement missing instructions with hallucinations. Manuals must specify:
  - Precise line numbers.
  - Full "Copy-Pasteable" content (Complete Code).
  - Explicit Before/After states.
  - Prohibited Actions (Negation constraints).

## 6. Project Setup Principles (MICKS Standard)

Derived from the verified project protocol to ensure zero-blind-spot execution:

1. **Exact Naming (実名主義)**: Assumed or "ideal" object names are prohibited. Use only verbatim names from screenshots or provided lists. If a name is unknown, find it in visual evidence or request it.
2. **Proposal vs. Fabrication (提案 vs. 捏造)**:
   - **Fabrication**: Using a name/field assuming it exists (Transgression).
   - **Proposal**: Stating a field is missing and suggesting its creation (Professionalism).
3. **One Line One Definition**: Define terminology or context in a single line before proceeding to logic/tasks.
4. **Windows-Native Instruction**: Describe all UI operations using Windows-specific menu paths (e.g., `File` -> `Manage` -> `Database`).
5. **MVP Velocity**: Prioritize functional "movement" (MVVM-like logic in FileMaker) over security, permissions, or deep optimization during initial development phases.
6. **Structural Pruning (Means to an End)**: Implementation is a means to an end (要件を満たすための機能、の実装のための手段). Proactively delete redundant relationships or TOs to maintain a "Beautiful" (minimalist and deductive) graph.
