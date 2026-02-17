# FileMaker Development Mapping (Hegemonikón → FileMaker)

Mapping cognitive control structures to a low-code database environment.

## 1. Portability Evaluation

| Element | Portability | Strategy |
| :--- | :---: | :--- |
| **Workflow Philosophy** | ⭐⭐⭐⭐⭐ | Deeply compatible. Use /zet→/noe→/dia sequence. |
| **Quality Patterns** | ⭐⭐⭐⭐⭐ | Use /dia, /syn, /pan for code and UX review. |
| **Theorem Framework** | ⭐⭐⭐⭐⭐ | use 6 series (24 theorems) as "Audit Questions". |
| **Mnēmē System** | ⭐⭐⭐⭐☆ | Implement Chronos/Sophia/Kairos within the FM app. |
| **CCL Syntax** | ⭐⭐⭐☆☆ | Use for IDE-FM coordination and as a meta-language. |

## 2. IDE-Centered Integration (連携)

The Hegemonikón (IDE) serves as the "Production Core" (人生の中枢), while FileMaker is the "Target Platform" for execution.

- **Calculation & Design**: Database structures, script logic, and UI design are performed within the IDE using AI-driven analysis and CCL.
- **Data Simulation**: Abstract dummy data is generated for each requirement to test logic before implementation.
- **Export/Import**: Instead of manual entry, the results of the IDE's processing are exported and "imported" into the FileMaker environment.
- **Coordination**: CCL acts as the bridge between the AI's internal state and the external FileMaker system.

## 3. Theoretical Mapping (Theorem Application)

The system is governed by **24 Theorems** organized into **6 Series**. These are used as "Probes" or "Audit Questions" during the design phase:

- **6 Series**: Based on the 6 relational coordinates (Flow, Value, Scale, Function, Valence, Precision).
- **Probes**:
  - **O-Series (Ousia)**: "Do I truly understand the business logic? Is the table relation beautiful?"
  - **A-Series (Akribeia)**: "Is this script robust against user error? Have I critiqued my own design?"
  - **H-Series (Horme)**: "Is this implementation following the project's established best practices?"
  - **S-Series (Schema)**: "Is the performance efficient enough for the expected record count?"
  - **K-Series (Kairos)**: "Does this layout fulfill the core purpose for the user at the right moment?"
  - **P-Series (Perigraphe)**: "Are the functional boundaries clear? Is the navigation method logical?"

## 3. Workflow Archetypes for FileMaker

### 3.1. The "Zetesis" Phase (探求)

- Trigger: Vague senior instructions or Excel sheets.
- Action: Map the Excel columns to Table Entities. Identify "Friction Points" where the Excel structure fails to meet normalization standards.

### 3.2. The "Noesis" Phase (認識)

- Action: Design the Graph (Relationships). Ensure "Zero Entropy" in data flow.
- Output: ERD and Calculation Logic.

### 3.4. XML & Integration Strategy (突破口)

While direct structural import of DDR XML is not possible, the **Add-on (SaXML/fmaddon)** system provides a way to package and distribute designs:

1. **Design in IDE**: Hegemonikón generates table structures, scripts, and layout mocks.
2. **Build Base**: Create a base FileMaker file with these structural elements.
3. **Package as Add-on**: Use `Save a Copy as Add-on Package`.
4. **Deploy**: Move the `.fmaddon` package to the `AddonModules` directory.
5. **Install**: Restart FileMaker Pro and add the module to the target solution.

This bridges the gap between the IDE's "Production Core" logic and FileMaker's "Target Platform" execution.
