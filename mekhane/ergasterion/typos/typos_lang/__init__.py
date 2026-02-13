# Dummy typos_lang module for testing
# PURPOSE: Dummy ContextItem for testing
class ContextItem:
    # PURPOSE: Initialize ContextItem
    def __init__(self, ref_type=None, path=None, tool_chain=None):
        self.ref_type = ref_type
        self.path = path
        self.tool_chain = tool_chain

# PURPOSE: Dummy parse_mcp for testing
def parse_mcp(code):
    return {"mcp_context": ["dummy_tool"]}
