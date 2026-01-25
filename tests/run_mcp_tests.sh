#!/bin/bash
set -e

echo "Running direct MCP server test..."
python3 tests/test_mcp_integration.py

echo "Running Prompt-Lang compilation test (context resolution)..."
python3 forge/prompt-lang/prompt_lang.py compile tests/mcp_sample.prompt > tests/output.md

if grep -q "generated_skill" tests/output.md; then
    echo "SUCCESS: Context resolution verified."
else
    echo "FAILURE: Context resolution did not produce expected output."
    exit 1
fi

echo "All tests passed."
