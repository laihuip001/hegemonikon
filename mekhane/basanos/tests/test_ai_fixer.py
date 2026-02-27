# PROOF: [L2/テスト] <- mekhane/basanos/ ai_fixer の修正テスト
"""ai_fixer.py の _fix_ai_013_mutable_defaults と _fix_ai_018_hardcoded_paths のテスト"""

import textwrap
from pathlib import Path

from mekhane.basanos.ai_fixer import AIFixer


# PURPOSE: AI-013: mutable default arguments の修正
class TestFixMutableDefaults:
    """AI-013: mutable default arguments の修正"""

    # PURPOSE: 空リストのデフォルト引数を検出する
    def test_detect_empty_list_default(self):
        """空リストのデフォルト引数を検出する"""
        fixer = AIFixer(dry_run=True)
        code = textwrap.dedent('''\
            def process(items=[]):
                return items
        ''')
        fixes = fixer._fix_ai_013_mutable_defaults(code, Path("test.py"))
        assert len(fixes) >= 1
        assert any(f.code == "AI-013" for f in fixes)
        assert any("items=None" in f.replacement for f in fixes)

    # PURPOSE: 空辞書のデフォルト引数を検出する
    def test_detect_empty_dict_default(self):
        """空辞書のデフォルト引数を検出する"""
        fixer = AIFixer(dry_run=True)
        code = textwrap.dedent('''\
            def configure(options={}):
                return options
        ''')
        fixes = fixer._fix_ai_013_mutable_defaults(code, Path("test.py"))
        assert len(fixes) >= 1
        assert any("options=None" in f.replacement for f in fixes)

    # PURPOSE: set() のデフォルト引数を検出する
    def test_detect_set_call_default(self):
        """set() のデフォルト引数を検出する"""
        fixer = AIFixer(dry_run=True)
        code = textwrap.dedent('''\
            def collect(seen=set()):
                return seen
        ''')
        fixes = fixer._fix_ai_013_mutable_defaults(code, Path("test.py"))
        assert len(fixes) >= 1
        assert any("seen=None" in f.replacement for f in fixes)

    # PURPOSE: 安全なデフォルト引数 (None, int, str) は無視する
    def test_safe_defaults_ignored(self):
        """安全なデフォルト引数 (None, int, str) は無視する"""
        fixer = AIFixer(dry_run=True)
        code = textwrap.dedent('''\
            def safe(x=None, y=0, z="hello"):
                return x, y, z
        ''')
        fixes = fixer._fix_ai_013_mutable_defaults(code, Path("test.py"))
        assert len(fixes) == 0

    # PURPOSE: None 変換と同時に guard 文が提案される
    def test_guard_insertion(self):
        """None 変換と同時に guard 文が提案される"""
        fixer = AIFixer(dry_run=True)
        code = textwrap.dedent('''\
            def process(items=[]):
                for item in items:
                    print(item)
        ''')
        fixes = fixer._fix_ai_013_mutable_defaults(code, Path("test.py"))
        guard_fixes = [f for f in fixes if "guard" in f.description]
        assert len(guard_fixes) >= 1
        assert any("if items is None" in f.replacement for f in guard_fixes)

    # PURPOSE: 構文エラーのあるコードでは空リストを返す
    def test_syntax_error_returns_empty(self):
        """構文エラーのあるコードでは空リストを返す"""
        fixer = AIFixer(dry_run=True)
        fixes = fixer._fix_ai_013_mutable_defaults("def broken(:", Path("test.py"))
        assert fixes == []

    # PURPOSE: async 関数でもmutable defaultsを検出する
    def test_async_function(self):
        """async 関数でもmutable defaultsを検出する"""
        fixer = AIFixer(dry_run=True)
        code = textwrap.dedent('''\
            async def fetch(urls=[]):
                return urls
        ''')
        fixes = fixer._fix_ai_013_mutable_defaults(code, Path("test.py"))
        assert len(fixes) >= 1
        assert any("urls=None" in f.replacement for f in fixes)


# PURPOSE: AI-018: hardcoded paths の修正
class TestFixHardcodedPaths:
    """AI-018: hardcoded paths の修正"""

    # PURPOSE: '/home/...' パスを検出する
    def test_detect_hardcoded_home_path(self):
        """'/home/...' パスを検出する"""
        fixer = AIFixer(dry_run=True)
        lines = ['    base_dir = Path("/home/user/project/src")\n']
        fixes = fixer._fix_ai_018_hardcoded_paths(lines, Path("test.py"))
        assert len(fixes) == 1
        assert fixes[0].code == "AI-018"
        assert "TODO: AI-018" in fixes[0].replacement

    # PURPOSE: 既に TODO コメントがある行はスキップする
    def test_skip_already_annotated(self):
        """既に TODO コメントがある行はスキップする"""
        fixer = AIFixer(dry_run=True)
        lines = ['    base_dir = Path("/home/user/src")  # TODO: fix later\n']
        fixes = fixer._fix_ai_018_hardcoded_paths(lines, Path("test.py"))
        assert len(fixes) == 0

    # PURPOSE: # noqa がある行はスキップする
    def test_skip_noqa_annotated(self):
        """# noqa がある行はスキップする"""
        fixer = AIFixer(dry_run=True)
        lines = ['    path = "/home/user/data"  # noqa: AI-018\n']
        fixes = fixer._fix_ai_018_hardcoded_paths(lines, Path("test.py"))
        assert len(fixes) == 0

    # PURPOSE: ハードコードパスがなければ空リスト
    def test_no_hardcoded_paths(self):
        """ハードコードパスがなければ空リスト"""
        fixer = AIFixer(dry_run=True)
        lines = ['    path = Path("./relative/path")\n']
        fixes = fixer._fix_ai_018_hardcoded_paths(lines, Path("test.py"))
        assert len(fixes) == 0

    # PURPOSE: 複数行にハードコードパスがある場合
    def test_multiple_hardcoded_paths(self):
        """複数行にハードコードパスがある場合"""
        fixer = AIFixer(dry_run=True)
        lines = [
            '    a = "/home/user/dir1"\n',
            '    b = "safe"\n',
            "    c = '/home/user/dir2'\n",
        ]
        fixes = fixer._fix_ai_018_hardcoded_paths(lines, Path("test.py"))
        assert len(fixes) == 2
