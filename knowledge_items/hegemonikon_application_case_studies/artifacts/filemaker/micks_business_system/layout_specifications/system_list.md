# Layout Specification: System List (システム一覧)

## 1. Overview

The "System List" layout is the second rung in the "Ladder Navigation" hierarchy. Users arrive here after selecting a company in the Company List. It displays all software systems associated with the selected company.

## 2. Technical Configuration

| Attribute | Value |
| :--- | :--- |
| **Layout Name** | `システム一覧UI（System基点）` |
| **Data Source (Base TO)** | `System` (Controller Table) |
| **Navigation Context** | `System::G_UI_選択会社ID` (Anchored from Company List) |
| **List Relationship** | `System::G_UI_選択会社ID = システム一覧::_fk_会社一覧ID` |
| **Search Hub (1=1)** | `System::G_UI_全件キー = システム一覧::UI_全件キー` (Optional/Context Dependent) |

## 3. UI Components

### Top Bar (Header)

| Element | Property | Value |
| :--- | :--- | :--- |
| **Header Part** | Background | `#4A90D9` (Blue), Height: 40 pt |
| **Back Button** | Label | `← 戻る`, Font: `游ゴシック 12 pt`, Color: `#FFFFFF` |
| **Title** | Text | `システム一覧`, Font: `游ゴシック 16 pt Bold`, Center Aligned |
| **Context Label** | Field | `会社一覧_詳細::会社名`, Font: `游ゴシック 12 pt`, Color: `#FFFFFF` |

### Left Panel (Selection - 40% Width)

- **Search Header**:
  - Global Search Field: `Search::G_SCH_システム名` (Global Storage). Object name: `fld_システム検索`.
  - UI Specs: Position X: 55 pt, Y: 50 pt. Background: `#FFFFFF`, Border: `#CCCCCC`.
  - Actions: "[検索]" (#4A90D9) and "[クリア]" (#E0E0E0) buttons.
- **System Portal**:
  - **TO**: `システム一覧`.
  - **Object Name**: `UI_システム一覧_ptl_システム名`.
  - **Relationship**: `System::G_UI_選択会社ID = システム一覧::_fk_会社一覧ID`.
  - **Visuals**: Height: 40 pt per row, Alternating colors `#FFFFFF` / `#F9F9F9`.
  - **Portal Filter**: `IsEmpty ( Search::G_SCH_システム名 ) or PatternCount ( システム一覧::システム名 ; Search::G_SCH_システム名 ) > 0`
  - **Interaction**: Clicking a system name triggers `UI_システム_選択` script.
    - **Crucial**: Must pass `システム一覧::__pk_システム一覧ID` as a **Script Parameter**.

### Right Panel (Details - 60% Width)

- **Header**: "システム詳細" (Font: `游ゴシック 14 pt Bold`).
- **Form Fields**:
  - Labels: `游ゴシック 12 pt`, Color: `#666666`, Right Aligned.
  - Value Fields: `游ゴシック 12-13 pt`, Background: `#FAFAFA`, Border: `#E0E0E0`.
- **Relationship**: `System::G_UI_選択システムID = システム一覧_詳細::__pk_システム一覧ID`.
- **Navigation Buttons**:
  - "[編集]": Background `#E8E8E8`.
  - "[→ 大機能一覧へ]": Background `#4A90D9`.

## 4. Scripting Requirements

### UI_システム_選択

```markdown
1. フィールド設定 [ System::G_UI_選択システムID ; Get ( スクリプト引数 ) ]
   # 引数: システム一覧::__pk_システム一覧ID
2. ウインドウ内容の再表示 []
```

## 5. Visual Logic

- Implements the "Split Architecture" principle: One screen dedicated to the `System` entity for a specific `Company` context.
- Maintains the same "Two-Pane" look and feel as the Company List to ensure UI consistency.
