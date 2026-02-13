# Dummy typos_lang module for testing
class ContextItem:
    def __init__(self, ref_type=None, path=None, tool_chain=None):
        self.ref_type = ref_type
        self.path = path
        self.tool_chain = tool_chain

def parse_mcp(code):
    return {"mcp_context": ["dummy_tool"]}
