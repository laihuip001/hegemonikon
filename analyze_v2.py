import ast
import sys

class LineAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.line_counts = {}

    def visit(self, node):
        if hasattr(node, 'lineno'):
            lineno = node.lineno
            if lineno not in self.line_counts:
                self.line_counts[lineno] = {'ops': 0, 'calls': 0}

            if isinstance(node, (ast.BinOp, ast.UnaryOp, ast.AugAssign)):
                self.line_counts[lineno]['ops'] += 1
            elif isinstance(node, ast.BoolOp):
                self.line_counts[lineno]['ops'] += len(node.values) - 1
            elif isinstance(node, ast.Compare):
                self.line_counts[lineno]['ops'] += len(node.ops)
            elif isinstance(node, ast.Call):
                self.line_counts[lineno]['calls'] += 1

        self.generic_visit(node)

analyzer = LineAnalyzer()
with open(sys.argv[1], 'r') as f:
    tree = ast.parse(f.read())
    analyzer.visit(tree)

print("Violations:")
for lineno, counts in sorted(analyzer.line_counts.items()):
    ops = counts['ops']
    calls = counts['calls']
    if ops >= 5:
        print(f"Line {lineno}: {ops} ops (>=5)")
    if calls >= 4:
        print(f"Line {lineno}: {calls} calls (>=4)")
