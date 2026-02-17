# FileMaker Terminology: User Glossary & Translation

This document captures the specific conceptual "translations" used by the user to internalize FileMaker development.

| FileMaker Term | User's Mental Model (Translation) | Role in MICKS System |
| :--- | :--- | :--- |
| **Table** | データ置き場 (Data Storage/Place) | `会社一覧`, `システム一覧`, `System`. |
| **Record** | 行 (Row / 1 Piece of Data) | A single system or company entry. |
| **Field** | 箱 (Box / Elements in the network) | The specific data points within a "place". |
| **Primary Key (ID)** | 本名 / 錨 (Real Name / Anchor) | `__pk_...` (Double underscore for top sorting). |
| **Foreign Key** | ラベル (Label / Attachment) | `_fk_...` labels identifying belonging. |
| **Relationship Graph** | 地図 / 路線図 (Map / Route Map) | The visual layout of how "places" connect. |
| **Table Occurrence (TO)** | 入口ラベル / 窓 (Entrance Label / Window) | A specific perspective on a table (e.g., "Company as Selection"). |
| **Layout** | 世界観 / 文脈設計 (Worldview / Context Design) | The scope of what is visible and operable. |
| **Context** | 包括的な操作の前提 (Operational Premise) | Determining what is possible based on which "entrance" you stand in. |
| **Found Set** | 対象レコード (Target records / Virtual World) | The subset of data actively adopted as the current "world". |
| **Find (Search)** | 世界を作り直す操作 (Operation to remake the world) | Redefining the active "found set". |
| **Portal** | 世界観に基づく決定的な抽出一覧 (Definitive projection) | A sampling of a connected world filtered by the current context. |
| **Global Field** | UI用変数箱 (UI Variable Box) | Used for states like `G_UI_選択会社ID` or searchable keys. |
| **Value List** | 表記ゆれ防止装置 (Fluctuation prevention device) | Forcing correct ID storage while showing readable names. |
| **`::` Operator** | 参照のアンカー (Reference Anchor) | Fixing a reference to a specific "entrance" (TO) regardless of current context. |

## Why it matters

The user explicitly stated that they "forget" the formal names but remember these conceptual translations. Use these terms to explain complex FileMaker behaviors (e.g., explaining why a portal filter failed as "the window isn't looking at the right box").
