# FileMaker Add-on Generation Implementation

This document describes the implementation of a programmatic FileMaker Add-on (.fmaddon) generator using Python and the `xar` utility on Linux.

## Overview

FileMaker Add-ons are packaged as `.fmaddon` files, which are actually **XAR archives**. They contain metadata (`info.json`) and a template of FileMaker objects (`template.xml`) in SaXML format.

## Implementation: `addon_generator.py`

### Implementation v2: `addon_generator_v2.py` (2026-02-04)

The generator was improved to address recognition failures by incorporating insights from commercial role models.

1. **BOM & UTF-16LE Encoding**: Mandatory for `template.xml`.
2. **Catalog Inclusion**: Explicitly adds `BaseDirectoryCatalog` and `TableOccurrenceCatalog`.
3. **TO-BT Mapping**: Each `BaseTable` must have a corresponding `TableOccurrence` referencing its ID/UUID for the schema to be considered valid by FileMaker's parser.

### Key Code Snippet (BOM & Encoding Logic)

```python
# Write files with BOM (UTF-16LE as per FileMaker format)
(addon_dir / 'template.xml').write_text('\ufeff' + template_xml, encoding='utf-16-le')

# Standard Metadata (UTF-8 with BOM is generally safe for JSON)
(addon_dir / 'info.json').write_text('\ufeff' + info_json, encoding='utf-8')
```

## Known Issues and Troubleshooting

### "Translator Not Found" Error

When double-clicking a generated `.fmaddon` file in Windows, FileMaker may throw an error:
> 「このファイル形式に対応するトランスレーターが見つからないか初期化できませんでした」
> (The translator for this file format could not be found or initialized)

**Causes**:

1. **Missing Localization Files**: Official add-ons (like Carafe) include `en.xml`, `ja.xml`, etc., which map `DynamicTemplateString` IDs to localized strings.
2. **Strict XAR Requirements**: FileMaker's built-in expansion might expect specific headers or additional files (`preview.png`, `icon.png`).

### Workaround: Direct Folder Deployment

Instead of using the `.fmaddon` package, the **uncompressed folder** can be placed directly in the FileMaker Add-on directory:

**Path**: `%LOCALAPPDATA%\FileMaker\Extensions\AddonModules\`

**Procedure**:

1. Generate the add-on folder (containing `info.json` and `template.xml`).
2. Copy the entire folder to `AddonModules/`.
3. The add-on will appear in the "Add-ons" tab in Layout mode.

### Add-on Not Recognized (Even with Direct Placement)

If the add-on does not appear in the "Choose Add-on" dialog:

**Causes**:

1. **Missing `info_en.json`**: FileMaker might skip folders that do not provide a localized "Title" and "Description" in at least English or the system language.
2. **Missing `icon.png`**: A valid icon might be required for the UI to consider the folder a valid add-on module. **Update**: Adding icons alone to a barebones structure is not enough for recognition.
3. **Namespaced IDs**: Objects in `template.xml` must be named using the `com.fmi` namespace (e.g., `com.fmi.basetable.MyTable`) and mapped in `en.xml`.
4. **Registry/Cache**: FileMaker may require a full restart or clearing of its extension cache.

**Refinement Strategy**:
Include `info_en.json` with basic metadata (Title, Description) in every generated package to ensure visibility in the UI.

## Conclusion and Future Direction

Our experiments (2026-02-04) conclude that while the outer shell of an add-on (XAR packaging, metadata, icons) can be programmatically generated on Linux, the inner `template.xml` is the critical failure point. Even with correct metadata and icons, FileMaker Pro rejects barebones `template.xml` structures.

### Recommended Strategy

1. **Design-First**: Use Hegemonikón for the conceptual schema design (Markdown).
2. **Template-Based Generation**: Use a pre-existing `template.xml` exported from FileMaker Pro as a base, and programmatically swap identifiers/names using string replacement in the IDE.
