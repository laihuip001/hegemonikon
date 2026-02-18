# FileMaker Development: Troubleshooting & Lessons Learned

## 1. Object Naming & TO Conflicts

- **Problem**: Table Occurrence (TO) names with spaces or reserved words cause FileMaker to use `${ }` syntax in scripts/calculations, leading to confusion.
- **Solution**: Normalize TO names by removing spaces and using standard suffixes (`_選択`, `_詳細`).

## 2. UI Interactivity Issues

- **Problem**: Lower layers (portals/buttons) not responding to clicks or scrolling.
- **Solution A (Layering)**: Check for invisible objects (rectangles, containers) overlaying the interactive area. Use "Bring to Front" or Move to Back.
- **Solution B (Portal Setup)**: Ensure "Allow Vertical Scrolling" is enabled in Portal Setup.

## 3. Data Sync & Portal Emptiness

- **Problem**: Portal displays no records despite correct relationship logic.
- **Solution**: Verify the data match. Often, IDs in the child table (FK) do not exactly match the parent ID (PK), especially with manually entered test data or Excel imports.

## 4. Structural Constraints

- **Problem**: Cannot replicate the persistent footer bar seen in design PDFs.
- **Solution**: Explicitly add a "Footer" part via the Layout Part Setup menu. FileMaker layouts default to Top Navigation, Header, Body, and Bottom Navigation; a true Footer remains fixed regardless of body scrolling.

## 5. Script Trigger Failures

- **Problem**: Navigation buttons not executing scripts.
- **Solution**: Check if the "Go to Layout" step exists inside the script. Often, developers update the ID state but forget to actually trigger the layout change.

## 6. Implementation Verification (Zero Trust)

- **Problem**: AI-generated reports or code often "guess" naming conventions based on initial instructions.
- **Problem**: Search functionality fails despite correct logic.
  - **Root Cause A**: The search keyword field (e.g., `G_SCH_会社名`) is not set to **Global Storage**. If it's a normal field, the value only exists in one record, and the portal filter (which evaluates every row) won't see it for other rows.
  - **Root Cause B**: `Refresh Window` is sometimes insufficient for portal filters. **`Refresh Portal`** with a specific object name is required when the filter depends on global fields.
- **Lesson**: Always verify actual object names and field storage settings via screenshots.
- **Naming Nuances**: The current environment uses a mix of functional prefixes and underscores (e.g., `UI_システム_選択` vs `SCH_システム_検索入力クリア`). Ground-truth verification of the **actual underscores** is mandatory as the naming is inconsistent across components.
- **Pattern Matching**: The user's system follows a `Prefix_Table_Action` format (e.g., `SCH_会社_検索`, `UI_会社_編集へ移動`). Maintain this strictly as the user uses a "Zero Trust" policy for report accuracy.

## 7. UI/UX "Stickiness"

- **Problem**: Button bar segments stay blue (active) after clicking.
- **Reason**: This is default behaviour for "Button Bars" which track active segments. For "one-off" actions like search or clear, using a standard **"Button"** object instead of a "Button Bar" is often cleaner to avoid the "stuck" visual state.

## 8. Behavioral Protocols & Project Integrity

- **The Skimming Proviso (流し読み禁止)**: Skimming conversation logs or source material is defined as a "betrayal" (裏切り) of project integrity and the Creator's trust. Absolute precision and "Zero Trust" verification of naming conventions (e.g., `__pk_` vs `_pk_`) are mandatory.
- **One Line One Sentence Principle (一行一文)**: Adopting the /dendron spirit, every line of a log or code must be fully "understood" before refactoring. Refactoring without deep understanding is an act of transgression.
- **Sorting Logic in Naming**: Primary keys must use the **`__pk_`** (double underscore) prefix. This ensures they sort to the very top of field lists in FileMaker, maximizing visibility for developers.

## 9. Scripting Error: The "Select by Number" (番号で指定) Dialog

- **Problem**: A dialog appears asking for a record number (e.g., "0/6") when trying to navigate to a specific ID.
- **Cause**: Using the `Go to Record/Request/Page` (レコード/検索条件/ページへ移動) step with a calculation like `__pk_ID = G_UI_SelectedID`. FileMaker interprets this as a request for a record *index number* (1, 2, 3...) rather than a value match.
- **Solution**:
  - **Option A (Preferred)**: Use **`Go to Related Record`** (関連レコードへ移動) which uses the relationship graph to find the match.
  - **Option B**: Use a search sequence (`Enter Find Mode` -> `Set Field [__pk_ID; G_UI_SelectedID]` -> `Perform Find`).

## 10. Global Storage Sync Issues

- **Problem**: Portal filters or relationships based on search fields fail intermittently or show stale data.
- **Root Cause**: The search field (e.g., `G_SCH_会社名`) is not set to **Global Storage** in the Database Manage dialog. Without global storage, the value is record-specific, meaning the portal (standing on a different record context) cannot "see" the search term consistently.
- **Action**: Always verify that `G_SCH_...` and `G_UI_...` fields are explicitly set to Global Storage in the field options.

## 11. "Ladder Navigation" (Phase 2): Layout to Layout

- **Requirement**: The President's request for split layouts means we must jump from Layout A (Company) to Layout B (System), showing only relevant systems.
- **Problem**: Just switching layouts resets context if no specific find/filter is applied.
- **Solution (Global State Anchor)**:
  1. Store the selection ID in a global "bridge" field (`System::G_UI_選択会社ID`).
  2. Perform `Go to Layout`.
  3. Ensure the target layout's data source is a TO that relates back to the bridge field.
- **Lesson**: Navigation in a split architecture is a two-step process: **Anchor State** -> **Change Context**.

## 12. "Complement Error" (补完误差) & VGT-Loop

- **Definition**: A phenomenon where an AI agent "complements" missing or ambiguous instructions with its own assumptions/hallucinations, leading to architectural drift.
- **Prevention (VGT-Loop)**:
  - **Evidence First**: Do not proceed with the next design step until the current implementation is verified by an **Actual Screenshot** (Ground Truth).
  - **Object Name Accuracy**: Standardized names (e.g., `ptl_Name`) often fail because the actual object in FileMaker is more complex (e.g., `UI_システム一覧UI_ptl_システム名一覧`). The VGT-Loop catches these discrepancies early.
  - **Script Step Verification**: Screen-capturing the Script Workspace is the only way to prove a script actually implements the intended logic (e.g., verifying `Refresh Portal` targets the correct object).
- **Metric**: Success is measured by "Zero Interpretation" — the manual should be so precise that a non-thinking agent could execute it perfectly.

## 13. Hallucinated Architecture & Patterns

- **Syndrome**: A specific type of "Complement Error" where an agent attempts to refactor the user's architecture toward an "ideal" pattern (e.g., centralizing all search fields in a Controller table) without ensuring environmental compatibility.
- **The MICKS Case (Evolution)**: Initially, centralizing search fields in the `System` table was rejected to avoid table bloat. However, as the hierarchy grew to 6 layers, a **Search TO** (dedicated controller table) was proposed and approved. This separates "Selection State" from "Filter Criteria," satisfying both product-grade search requirements and architectural cleanliness.
- **Principle (Separation of Controllers)**:
  - `System`: Manages "Where the user is" (Current Selection IDs).
  - `Search`: Manages "What the user is looking for" (Filter match fields like `G_SCH_...`).
- **Proposal vs. Fabrication**:
  - **Fabrication (Transgression)**: Using a field or name assuming it exists (e.g., `System::G_SCH_...`) when it hasn't been verified. This leads to broken logic and user frustration.
  - **Proposal (Professionalism)**: Identifying a missing logical link and proposing the creation of a new field or table (e.g., "I propose creating a dedicated `Search` table for global criteria") before using it in instructions.
- **Verification Ritual**: Before suggesting an architectural shift, the agent must verify the current state of **all related entities** (e.g., checking if the Company list uses the same proposed pattern) to avoid inconsistency.

- **Constraint**: Changing these or "simplifying" them (e.g., `__pk_ID` -> `ID`, or `UI_全件キー` -> `全件キー`) is a direct violation of the project protocol.
- **Verbatim Requirement**: All object names must be used exactly as they appear in screenshots or established lists. Case sensitivity, underscores, and prefixes are non-negotiable.
- **Action**: Failure to use exact naming is categorized as a "transgression" (捏造). Before providing instructions, verify the verbatim name of every field and TO involved.

## 15. Multiple Relational Paths Error

- **Problem**: When trying to link TO `A` (e.g., `System`) and TO `B` (e.g., `システム一覧`), FileMaker returns the error: "Multiple relational paths cannot be specified between two tables in the graph."
- **Cause**: This occurs when the Relationship Graph already has a path between those two *base tables* (e.g., via a master-detail link or a parallel hierarchy).
- **The "Beautiful" Solution (Structural Pruning)**: Proactively delete legacy or direct table-to-table relationships (e.g., `会社一覧 ↔ システム一覧`) that are no longer strictly necessary. This "pruning" enables a clean, centralized **Star Schema** where all domain tables relate directly to the `System` controller hub.
- **The Tactical Fallback (Anchor-Buoy Chains)**: If legacy relationships must be preserved, create a uniquely named TO (e.g., `システム一覧_選択`) to establish a fresh, non-conflicting path.

## 16. Test Data Strategy: Hierarchy Debugging

- **Problem**: In a multi-layer hierarchy (Company -> System -> Major -> Middle -> Minor -> Request), verifying the correctness of the Relationship Graph (Anchor-Buoy) with generic UUIDs is difficult.
- **Solution (Prefix-Coded UUIDs)**: Use human-readable prefixes for UUIDs in test CSVs to immediately identify the "tier" and "context" of a record:
  - **Major Function**: `d001-0001-...` (d for "Dai" / Major)
  - **Middle Function**: `m001-0001-...` (m for "Midduru" / Middle)
  - **Minor Function**: `s001-0001-...` (s for "Shou" / Minor)
  - **Request**: `r001-0001-...` (r for "Request")
- **Benefit**: This allows the developer to instantly verify if a portal is correctly filtered (e.g., an `m001` record appearing in a `d001` portal is logically correct; an `m002` record is not).

## 17. Character Encoding (文字化け) on CSV Import

- **Problem**: When importing Japanese CSV data generated on Linux or modern web environments, FileMaker Pro may display the text as garbled characters (文字化け).
- **Cause**: Standard UTF-8 without a Byte Order Mark (BOM) is sometimes misinterpreted by FileMaker's import engine, especially in environments where the OS locale differs.
- **Solution (Idempotent BOM Fix)**: Ensure CSV files are saved as **UTF-8 with BOM (U-BOM)**. Use a script that checks if the BOM already exists before prepending to avoid double-corruption.
- **Linux Command-line Fix**:

  ```bash
  # Check for BOM (\xEF\xBB\xBF) and add if missing
  if ! head -c3 "$f" | grep -q $'\xef\xbb\xbf'; then
    tmp=$(mktemp)
    printf '\xEF\xBB\xBF' > "$tmp"
    cat "$f" >> "$tmp"
    mv "$tmp" "$f"
    echo "Added BOM to: $f"
  else
    echo "BOM already exists: $f"
  fi
  ```

- **Lesson**: Standardize all test data generation to include the BOM to prevent visual corruption of Japanese strings.

## 18. Context Mismatch After Controller Split

- **Problem**: In the MICKS Company List, search input and clear scripts execute without error, but the list portal remains unfiltered or "stuck" (no data change).
- **Relational Context**: A dedicated `Search` table (TO) was introduced to centralize global search fields (`G_SCH_...`), moving them out of the domain data tables (e.g., `会社一覧`).
- **Root Cause**: The **Portal Filter calculation** was still referencing the field from the domain table (e.g., `会社一覧::G_SCH_会社名`) instead of the centralized table (e.g., `Search::G_SCH_会社名`).
- **Diagnosis**:
  - Verification of the Portal Setup showed: `IsEmpty ( 会社一覧::G_SCH_会社名 ) or ...`
  - **Corrected to**: `IsEmpty ( Search::G_SCH_会社名 ) or ...`
- **Lesson**: Architectural centralization of global state (moving from domain to controller tables) requires a **cascading audit** of all layout objects (fields on screen) and portal filters to ensure they reference the new TO context.

## 19. Search Table "Ghost" Values (No Record)

- **Problem**: Global fields (e.g., `Search::G_SCH_会社名`) appear to work in one session but fail to hold values or return data in another, or seem completely non-functional despite correct script logic.
- **Cause**: The `Search` table (Controller) has **zero records**.
- **The Rule**: In FileMaker, global fields **cannot hold values** if the table they belong to has no records. Even though the value is technically global to the file, it requires a "record context" to exist in memory for that table.
- **Solution**:
  - Create exactly **one record** in the `Search` table.
  - This is typically done during the "OnFirstWindowOpen" startup script or manually during development.
  - Verification: Go to a layout based on `Search` and check the record count (e.g., 1/1). Use a UUID field (`__pk_SearchID`) to ensure the record is identifiable.
- **Lesson**: "One Record for Controllers" is a mandatory prerequisite for using global search/state fields in high-layer hierarchies.

## 20. Portal Object Name Mismatch (Visual Refresh Failure)

- **Problem**: The search keyword is correctly entered and verified in the database, but the portal does not refresh visually even after executing the script.
- **Cause**: The `Refresh Portal` (ポータルの更新) script step specifies an object name (e.g., `UI_会社一覧UI_ptl_会社名リスト`) that does not **exactly match** (character-by-character) the name defined in the Layout Inspector's Name field (e.g., `UI_会社一覧_ptl_会社名`).
- **Lesson**: Standardized "ideal" names from AI-generated manuals are prone to "Complement Errors." Ground-truth verification via the **Inspector panel screenshot** is the only way to ensure the refresh command hits the target.

## 21. Search Latency (Focus/Commit Requirement)

- **Problem**: Portal results do not update immediately after finishing typing; the UI only changes after the user clicks outside the field (releasing focus).
- **Cause**: FileMaker holds values in "Edit Focus." Portal filters (calculated at the record level) may not reliably see the updated global value until the state is **committed** to the database engine.
- **Solution**: The search script must begin with **`Commit Records/Requests [With dialog: Off]`** (レコード/検索条件確定) before the `Refresh Portal` step.
- **Deductive Reason**: This "forces" the global memory to broadcast the change to the layout calculation engine.

## 22. Clear Search Targeting Mismatch

- **Problem**: Clicking the "Clear" button clears the text field visually, but the portal list remains filtered or behaves erratically.
- **Cause**: In an evolution from "Domain Table Search" to "Centralized Controller Search," the script was clearing the old domain field (e.g., `会社一覧::G_SCH_会社名`) while the actual layout field and portal filter had already been migrated to the new table (e.g., `Search::G_SCH_会社名`).
- **Lesson**: Architectural migrations require a **Total Script Audit (TSA)** to ensure all "Clear" and "Search" logic targets the new Controller TOs.

## 23. Missing Script Parameters (Parameter Blindness)

- **Problem**: Selecting a portal record (e.g., clicking on a system name) does not update the "Detail" area, even though the selection script is triggered.
- **Root Cause**: The modular selection script (e.g., `UI_システム_選択`) utilizes `Get ( ScriptParameter )` to identify which record was clicked. If the button setup in the portal has the **"Optional script parameter"** field empty, the script receives an empty value and fails to update the global selection ID.
- **Prevention**: When implementing portal interactions, always verify the "Script Parameter" field in the Button Setup dialog.
- **Ground Truth Reference**: This was observed in the MICKS System List UI where the button was correctly set to the script but missing the ID parameter. **Verified Fixed**: Adding the script parameter immediately resolved the Detail panel sync issue.

## 24. Portal Filter Reference Mismatch (Ghost Fields)

- **Problem**: Portal Filter calculation displays `<Table Missing>` or `<Field Missing>` errors, or the filter simply stops working after an architectural change.
- **Cause**: When moving fields from a domain table (e.g., `会社一覧`) to a controller table (e.g., `Search`), the calculation engine "orphans" the old reference. FileMaker does not automatically update string-based references or calculation formulas when the TO context changes significantly.
- **Action**: Manually audit and re-select the correct fields in the Portal Filter calculation:
  - **Old**: `IsEmpty ( システム一覧::G_SCH_システム名 )`
  - **New**: `IsEmpty ( Search::G_SCH_システム名 )`
- **Metric**: If you see "Table Missing" in a screenshot of a calculation dialog, it is a 100% indicator of an un-migrated TO reference.
