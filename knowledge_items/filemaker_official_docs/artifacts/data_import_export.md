# FileMaker Data Import/Export Patterns

## 1. Character Encoding (Japanese Environment)

### The UTF-8 with BOM Requirement

When importing CSV data containing Japanese characters, FileMaker Pro may fail to recognize the encoding correctly if the file is standard UTF-8. This leads to **garbled text (文字化け)**.

- **Observed Behavior**: Standard UTF-8 (No BOM) generated on Linux/Web is often misinterpreted.
- **Requirement**: Use **UTF-8 with BOM (Byte Order Mark)**. The BOM (`\xEF\xBB\xBF`) serves as an explicit hint to the FileMaker import engine.
- **Verification**: Verified in production environments that adding the BOM resolves character corruption without changing the underlying data.

### Automation Protocol (Idempotent Fix)

To prepare CSVs for FileMaker, use the following bash logic to ensure the BOM is present exactly once:

```bash
if ! head -c3 "$file" | grep -q $'\xef\xbb\xbf'; then
  tmp=$(mktemp)
  printf '\xEF\xBB\xBF' > "$tmp"
  cat "$file" >> "$tmp"
  mv "$tmp" "$file"
fi
```

## 2. CSV Import Constraints

- **Field Mapping**: FileMaker allows manual mapping between CSV columns and table fields. Using a **Header Row** is highly recommended to prevent mapping errors.
- **Encoding Selection**: During the import dialog, the "Character Set" (文字セット) is typically set to "Unicode (UTF-8)" for modern files. If the BOM is present, FileMaker identifies it reliably.
- **Line Endings**: FileMaker generally supports CRLF (Windows) and LF (Unix/macOS), but CRLF is most consistent for large batch imports on Windows systems.

### リビジョン

- Knowledge Item: Data Exchange | 2026-02-06
