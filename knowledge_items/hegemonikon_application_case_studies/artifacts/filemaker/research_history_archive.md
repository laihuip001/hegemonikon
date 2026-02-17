# FileMaker Add-on Research: 2024-2025 History Archive

This document consolidates the historical research SOPs, requests, and initial findings from the investigation phase of the FileMaker Add-on integration project.

---

## 🔒 The Isolation Axiom (Safety Protocol)

**"Never test experimental add-ons on important files."**

The process of "Adding" an add-on involves internal schema modifications. Incomplete or malformed add-ons can cause permanent corruption (e.g., permanent renderer crashes in Layout Mode). Testing must exclusively use sacrificial `.fmp12` files.

---

## 1. Initial Research SOP: Add-on Integration (Feb 2024)

### Objective

Determine the exact XML schema and deployment steps required to package IDE-generated structural designs into an "importable" `.fmaddon` file.

### Key Hypothesis

By understanding the SaXML format used in add-ons, we can automate the "Integration (連携)" from Hegemonikón to FileMaker.

### Research Points

- Add-on Package Structure: Folder/file hierarchy, naming conventions.
- Programmatic Generation: CLI tools or direct SaXML manipulation.
- Deployment: Automated deployment to `AddonModules` via CI/CD.

---

## 2. Technical Standard: Add-on Generation Requirements (v1.9)

### Mandatory File Structure (38 Files)

A valid add-on that FileMaker Pro recognizes requires exactly:

- `info.json`: Main metadata.
- `info_*.json` (12 languages): Display settings.
- `*.xml` (12 languages): UI strings.
- `records_*.xml` (12 languages): Initial data.
- `template.xml`: Structural definition (UTF-16LE + BOM).
- `icon.png`, `icon@2x.png`, `preview.png`: UI assets.

### Encoding Standards

| File | Encoding | Trigger |
| :--- | :--- | :--- |
| **template.xml** | UTF-16LE | BOM (FF FE) |
| **info_*.json** | UTF-8 | BOM (EF BB BF) |

### Catalog Requirements

The `<AddAction>` section in `template.xml` must include 9 catalogs (even if empty with `membercount="0"`):

1. BaseTableCatalog
2. TableOccurrenceCatalog
3. FieldsForTables
4. ScriptCatalog
5. ThemeCatalog
6. LayoutCatalog
7. CustomMenuCatalog
8. RelationshipCatalog
9. ValueListCatalog

---

## 3. Failure Analysis: Recognition & Loading (Feb 2024)

### Recognition Failures

Addon v4/v5 attempts failed despite matching official structures. This identified that:

- **BOM Absence**: Missing Byte Order Marks on JSONs/XMLs triggers "Translator not found" errors.
- **Complexity Floor**: The `template.xml` has a complexity floor—highly simplified XMLs (< 4,000 lines) are frequently ignored.
- **UUID Collisions**: Duplicate UUIDs in the `AddonModules` directory cause loading index collisions.

---

## 4. Community Knowledge Search (Japanese Focus)

### Objective

Identify successful community projects that generated add-ons externally.

### Findings

- High-quality add-ons (ImageMap, Carafe) reveal a strict `com.fmi.<type>.<id>` naming convention.
- No public "Add-on SDK" exists from Claris; schema definitions must be reverse-engineered from FileMaker Pro's native output.
- `preview.png` is suspected to be a mandatory trigger for display in the "Choose Add-on" dialog.

---

## 5. Summary of Initial Integration Research

### Core Conclusions (Early 2025)

- **Automation Potential**: ~80% for JSON-to-XML conversion.
- **Critical Bottlenecks**: The undocumented complexity of `template.xml` and the requirement for specific binary signatures (BOMs).
- **Tooling**: `xar` utility is confirmed for packaging on Linux.

---
*Archive Consolidated: 2026-02-05*
