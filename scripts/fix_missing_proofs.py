
import os
import sys

def main():
    root_dir = 'mekhane'
    missing_proof = [
        'mekhane/tape.py',
        'mekhane/api/routes/cortex.py',
        'mekhane/api/routes/devtools.py',
        'mekhane/mcp/mcp_guard.py',
        'mekhane/mcp/mcp_base.py',
        'mekhane/ccl/ccl_linter.py',
        'mekhane/ccl/operator_loader.py',
        'mekhane/dendron/falsification_checker.py',
        'mekhane/dendron/falsification_matcher.py',
        'mekhane/symploke/intent_wal.py',
        'mekhane/periskope/cli.py',
        'mekhane/periskope/synthesizer.py',
        'mekhane/periskope/query_expander.py',
        'mekhane/periskope/page_fetcher.py',
        'mekhane/periskope/citation_agent.py',
        'mekhane/periskope/engine.py',
        'mekhane/periskope/__init__.py',
        'mekhane/periskope/models.py',
        'mekhane/periskope/searchers/brave_searcher.py',
        'mekhane/periskope/searchers/internal_searcher.py',
        'mekhane/periskope/searchers/searxng.py',
        'mekhane/periskope/searchers/playwright_searcher.py',
        'mekhane/periskope/searchers/semantic_scholar_searcher.py',
        'mekhane/periskope/searchers/tavily_searcher.py',
        'mekhane/periskope/searchers/__init__.py',
        'mekhane/basanos/l2/g_struct.py',
        'mekhane/basanos/l2/hom.py',
        'mekhane/basanos/l2/cli.py',
        'mekhane/basanos/l2/history.py',
        'mekhane/basanos/l2/resolver.py',
        'mekhane/basanos/l2/__init__.py',
        'mekhane/basanos/l2/models.py',
        'mekhane/basanos/l2/deficit_factories.py',
        'mekhane/basanos/l2/g_semantic.py',
        'mekhane/ochema/ls_launcher.py',
        'mekhane/ochema/fake_extension_server.py',
        'mekhane/ochema/proto/extension_server_pb2_grpc.py',
        'mekhane/ochema/proto/extension_server_pb2.py',
        'mekhane/ochema/proto/__init__.py',
        'mekhane/anamnesis/vertex_embedder.py',
        'mekhane/exagoge/__main__.py'
    ]

    for filepath in missing_proof:
        if not os.path.exists(filepath):
            print(f'Skipping missing file: {filepath}')
            continue

        with open(filepath, 'r') as f:
            lines = f.readlines()

        if lines and lines[0].startswith('#!'):
            insert_idx = 1
        else:
            insert_idx = 0

        header = f'# PROOF: [L2/Auto] <- {filepath}\n'

        # Check if already present to avoid duplicates
        has_proof = False
        for line in lines[:5]:
            if line.startswith('# PROOF:'):
                has_proof = True
                break

        if not has_proof:
            lines.insert(insert_idx, header)
            with open(filepath, 'w') as f:
                f.writelines(lines)
            print(f'Added PROOF to {filepath}')
        else:
            print(f'PROOF already exists in {filepath}')

if __name__ == '__main__':
    main()
