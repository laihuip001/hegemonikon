import subprocess
import tempfile
import os
import pytest
import shutil

def test_optimized_get_text_content():
    """
    Verifies that the optimized O(N) getTextContent JavaScript function
    correctly extracts text while skipping excluded tags (SCRIPT, STYLE, PRE, CODE).
    """
    if not shutil.which("node"):
        pytest.skip("Node.js is not installed, skipping JS verification test")

    js_code = """
class Node {
    constructor(type, name, content) {
        this.nodeType = type;
        this.tagName = name;
        this.textContent = content || '';
        this.childNodes = [];
        this.parentElement = null;
    }

    appendChild(child) {
        child.parentElement = this;
        this.childNodes.push(child);
        return child;
    }
}

const ELEMENT_NODE = 1;
const TEXT_NODE = 3;

// Create structure
// div ->
//   span -> "Hello "
//   pre -> "code block"
//   div ->
//     span -> "nested text"
//     script -> "bad code"
//   text -> " direct text"

const root = new Node(ELEMENT_NODE, 'DIV');

const span1 = root.appendChild(new Node(ELEMENT_NODE, 'SPAN'));
span1.appendChild(new Node(TEXT_NODE, null, 'Hello '));

const pre = root.appendChild(new Node(ELEMENT_NODE, 'PRE'));
pre.appendChild(new Node(TEXT_NODE, null, 'code block'));

const div2 = root.appendChild(new Node(ELEMENT_NODE, 'DIV'));
const span2 = div2.appendChild(new Node(ELEMENT_NODE, 'SPAN'));
span2.appendChild(new Node(TEXT_NODE, null, 'nested text'));

const script = div2.appendChild(new Node(ELEMENT_NODE, 'SCRIPT'));
script.appendChild(new Node(TEXT_NODE, null, 'bad code'));

root.appendChild(new Node(TEXT_NODE, null, ' direct text'));

// Optimized implementation to be used in export_chats.py
function getTextContent(node) {
    const excludeTags = new Set(['STYLE', 'SCRIPT', 'CODE', 'PRE']);
    let text = '';

    for (const child of node.childNodes) {
        if (child.nodeType === TEXT_NODE) {
            text += child.textContent;
        } else if (child.nodeType === ELEMENT_NODE) {
            if (!excludeTags.has(child.tagName)) {
                text += getTextContent(child);
            }
        }
    }
    return text;
}

console.log(getTextContent(root));
"""
    # Use a temporary file to run the JS code
    with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
        f.write(js_code)
        temp_path = f.name

    try:
        result = subprocess.run(["node", temp_path], capture_output=True, text=True, check=True)
        # Expected output: "Hello nested text direct text"
        # (PRE and SCRIPT content are excluded)
        assert result.stdout.strip() == "Hello nested text direct text"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    pytest.main([__file__])
