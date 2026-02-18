# FileMaker Add-on Technical Teardown: Schema & Analysis

This document consolidates technical analysis, reverse-engineering logs, and schema specifications for FileMaker Add-on (.fmaddon) packages.

---

## 1. Internal Packaging (XAR Structure)

An add-on is a directory packaged as a **XAR archive**. The directory must contain precise metadata and localization files to be recognized by the FileMaker Pro engine.

### Mandatory File List

- `info.json`: GUID, Clients, Attribution, URL.
- `info_*.json` (12 languages): UI Metadata.
- `*.xml` (12 languages): Localized dynamic template strings.
- `template.xml`: The SaXML component definition.
- `records_*.xml`: Initial record data.
- `icon.png`, `icon@2x.png`: UI Icons.
- `preview.png`: High-resolution preview.

---

## 2. Manifest Schema (info.json)

```json
{
  "GUID": "UUID-STRING",
  "Clients": ["Pro", "Go"],
  "Attribution": "Author/Org",
  "URL": "https://example.com",
  "Icon_Color": "#HEXCOLOR",
  "Version": "1.0.0"
}
```

- **GUID**: Must match the `UUID` attribute in `template.xml`.
- **Icon_Color**: Background color for the icon in the FM UI.

---

## 3. Structural Specification (template.xml)

Uses FileMaker's **SaXML (Save as XML)** format.

### Encoding Requirement

- **UTF-16 Little Endian (UTF-16LE)** with **BOM (FF FE)**.
- XML Declaration: `<?xml version="1.0"?>` (Simplified version often more stable).

### Complexity Benchmarks (Role Models)

Analysis of official add-ons revealed a "Complexity Floor":

- **gcRecordNavigation**: ~4,657 lines (Minimum Floor).
- **ImageMap**: ~18,460 lines.
- **gcTimestampPicker**: ~58,510 lines.

Barebones XMLs (< 100 lines) created in early tests consistently failed recognition.

### Required Catalog Wrappers

`<AddAction>` must contain catalog tags even if empty:

- `BaseTableCatalog`, `TableOccurrenceCatalog`, `FieldsForTables`, `ScriptCatalog`, `LayoutCatalog`, etc.
- **Namespacing**: Official models use `com.fmi.<type>.<id>` for internal names to ensure integrity during update imports.

---

## 4. Component Mapping Patterns

### 4.1 Tables & Fields

- `BaseTable id="129"` mapping to `TableOccurrence`.
- Fields require `AutoEnter`, `Storage`, and `LanguageReference` definitions even at minimal scope.

### 4.2 Localized Mapping (en.xml, ja.xml)

Uses `<DynamicTemplateString>` to map internal IDs in the XML to user-friendly names.

```xml
<DynamicTemplateString>
    <StringID>com.fmi.basetable.MyTable</StringID>
    <TargetText>My Display Table Name</TargetText>
</DynamicTemplateString>
```

---

## 5. Reverse Engineering Findings (v4 - v6)

- **v4 Analysis**: Proved that UTF-8 BOM is required for JSON localization files. Without it, the "Translator not found" error occurs.
- **v6 bit-perfect verify**: Confirmed that bit-perfect identification leads to UUID conflicts if the source add-on is still installed. This proved that **UUID Uniqueness** is checked at the loader level.
- **Incident Report**: Manual SaXML manipulation caused permanent Layout Mode crashes in the test file, leading to the establishment of the **Isolation Axiom**.

---

## 6. Implementation: Programmatic Generation

While full creation is restricted, the transformation of skeletons is achievable via Python:

- **BOM & UTF-16LE Encoding**: Mandatory for `template.xml`. Use `'\ufeff'` to ensure FileMaker's parser recognizes the file.
- **TO-BT Mapping**: Each `BaseTable` must have a corresponding `TableOccurrence` referencing its ID/UUID.
- **Direct Deployment**: Folders placed in `%LOCALAPPDATA%\FileMaker\Extensions\AddonModules\` are recognized without `.fmaddon` packaging, aiding rapid iteration.

## 7. Operational Failures (The "Translator Not Found" Error)

This error (`トランスレーターが見つからない`) often stems from:

1. **Missing Localization**: Lack of `en.xml` or `ja.xml` mapping `DynamicTemplateString` IDs.
2. **Missing Metadata**: Failure to provide `info_en.json` or `icon.png` in the package folders.
3. **Namespace Violations**: Official loaders expect `com.fmi` namespaces for consistency.

### リビジョン

*Technical Teardown Consolidated: 2026-02-06*
