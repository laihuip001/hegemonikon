#!/usr/bin/env python3
# PROOF: [L2/Impl] <- mekhane/ Automated fix for CI
"""
MCP Server Integration Tests — mneme/ochema 統合後の回帰テスト

mneme_server.py に統合した gnosis/sophia tools と
ochema_mcp_server.py に統合した jules tools をテストする。
"""
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


# ============ mneme: search_papers ============

class TestMnemeSearchPapers:
    """gnosis → mneme に移植した search_papers のテスト"""

    @pytest.mark.asyncio
    async def test_search_papers_returns_results(self):
        """正常ケース: 論文検索で結果が返る"""
        mock_results = [
            {
                "title": "Free Energy Principle",
                "source": "semantic_scholar",
                "citations": 100,
                "authors": "Karl Friston",
                "abstract": "The free energy principle...",
                "url": "https://example.com/paper1",
            }
        ]

        with patch("mekhane.anamnesis.index.GnosisIndex") as MockIndex:
            instance = MockIndex.return_value
            instance.search.return_value = mock_results

            # mneme_server の handler を直接テスト
            from mekhane.mcp.mneme_server import _handle_search_papers

            result = await _handle_search_papers({"query": "free energy", "limit": 5})
            assert len(result) == 1
            text = result[0].text
            assert "Free Energy Principle" in text
            assert "Karl Friston" in text
            assert "100" in text

    @pytest.mark.asyncio
    async def test_search_papers_empty_query(self):
        """空クエリでエラーメッセージ"""
        from mekhane.mcp.mneme_server import _handle_search_papers

        result = await _handle_search_papers({"query": ""})
        assert "Error" in result[0].text

    @pytest.mark.asyncio
    async def test_search_papers_no_results(self):
        """結果なしのケース"""
        with patch("mekhane.anamnesis.index.GnosisIndex") as MockIndex:
            instance = MockIndex.return_value
            instance.search.return_value = []

            from mekhane.mcp.mneme_server import _handle_search_papers

            result = await _handle_search_papers({"query": "nonexistent_topic_xyz"})
            assert "No results" in result[0].text


# ============ mneme: recommend_model ============

class TestMnemeRecommendModel:
    """gnosis → mneme に移植した recommend_model のテスト"""

    @pytest.mark.asyncio
    async def test_p1_security(self):
        """P1: セキュリティタスク → Claude"""
        from mekhane.mcp.mneme_server import _handle_recommend_model

        result = await _handle_recommend_model({"task_description": "security audit of API"})
        text = result[0].text
        assert "P1" in text
        assert "Claude" in text

    @pytest.mark.asyncio
    async def test_p2_visual(self):
        """P2: 画像/UI タスク → Gemini"""
        from mekhane.mcp.mneme_server import _handle_recommend_model

        result = await _handle_recommend_model({"task_description": "UI design for dashboard"})
        text = result[0].text
        assert "P2" in text
        assert "Gemini" in text

    @pytest.mark.asyncio
    async def test_p4_batch(self):
        """P4: 高速/バッチタスク → Gemini Flash"""
        from mekhane.mcp.mneme_server import _handle_recommend_model

        result = await _handle_recommend_model({"task_description": "fast batch triage"})
        text = result[0].text
        assert "P4" in text
        assert "Gemini Flash" in text

    @pytest.mark.asyncio
    async def test_p5_default(self):
        """P5: マッチなし → Claude (default)"""
        from mekhane.mcp.mneme_server import _handle_recommend_model

        result = await _handle_recommend_model({"task_description": "generic task analysis"})
        text = result[0].text
        assert "P5" in text
        assert "Claude" in text

    @pytest.mark.asyncio
    async def test_empty_description(self):
        """空の task_description でエラー"""
        from mekhane.mcp.mneme_server import _handle_recommend_model

        result = await _handle_recommend_model({"task_description": ""})
        assert "Error" in result[0].text


# ============ mneme: backlinks ============

class TestMnemeBacklinks:
    """sophia → mneme に移植した backlinks のテスト"""

    @pytest.mark.asyncio
    async def test_backlinks_returns_links(self):
        """バックリンクが正しく返る"""
        with patch("mekhane.symploke.sophia_backlinker.SophiaBacklinker") as MockBL:
            instance = MockBL.return_value
            instance.build_graph.return_value = 5
            instance.get_backlinks.return_value = {"KI_A", "KI_B"}
            instance.get_outlinks.return_value = {"KI_C"}

            from mekhane.mcp.mneme_server import _handle_backlinks

            result = await _handle_backlinks({"ki_name": "FEP"})
            text = result[0].text
            assert "KI_A" in text
            assert "KI_B" in text

    @pytest.mark.asyncio
    async def test_backlinks_empty_ki(self):
        """空の ki_name でエラー"""
        from mekhane.mcp.mneme_server import _handle_backlinks

        result = await _handle_backlinks({"ki_name": ""})
        assert "Error" in result[0].text


# ============ mneme: graph_stats ============

class TestMnemeGraphStats:
    """sophia → mneme に移植した graph_stats のテスト"""

    @pytest.mark.asyncio
    async def test_graph_stats_returns_stats(self):
        """グラフ統計が返る"""
        with patch("mekhane.symploke.sophia_backlinker.SophiaBacklinker") as MockBL:
            instance = MockBL.return_value
            instance.build_graph.return_value = 10
            instance.get_stats.return_value = {
                "nodes": 20,
                "edges": 15,
                "isolated": 3,
                "most_linked": [("FEP", 5), ("HGK", 3)],
            }

            from mekhane.mcp.mneme_server import _handle_graph_stats

            result = await _handle_graph_stats({})
            text = result[0].text
            assert "20" in text
            assert "15" in text


# ============ ochema: jules API key pool ============

class TestOchemaJulesPool:
    """jules → ochema に移植した API key pool のテスト"""

    def test_jules_init_pool(self):
        """API key pool の初期化"""
        import mekhane.mcp.ochema_mcp_server as ochema

        ochema._jules_api_key_pool = []

        env_vars = {f"JULES_API_KEY_{i:02d}": f"test_key_{i}" for i in range(1, 4)}
        with patch.dict("os.environ", env_vars, clear=False):
            ochema._jules_init_pool()
            assert len(ochema._jules_api_key_pool) >= 3

    def test_jules_get_key_round_robin(self):
        """Round-robin でキーが巡回する"""
        import mekhane.mcp.ochema_mcp_server as ochema

        ochema._jules_api_key_pool = [(1, "key_a"), (2, "key_b"), (3, "key_c")]
        ochema._jules_api_key_index = 0
        ochema._jules_dashboard = None

        key1, idx1 = ochema._jules_get_key()
        key2, idx2 = ochema._jules_get_key()
        key3, idx3 = ochema._jules_get_key()

        assert key1 == "key_a"
        assert key2 == "key_b"
        assert key3 == "key_c"

    def test_jules_get_key_empty_pool(self):
        """空プールでは None を返す"""
        import mekhane.mcp.ochema_mcp_server as ochema

        ochema._jules_api_key_pool = []
        with patch.dict("os.environ", {}, clear=True):
            key, idx = ochema._jules_get_key()
            # キーがない場合 None
            assert key is None


# ============ ochema: jules handler ============

class TestOchemaJulesHandler:
    """jules → ochema に移植した _handle_jules のテスト"""

    @pytest.mark.asyncio
    async def test_jules_create_task_missing_params(self):
        """必須パラメータ不足でエラー"""
        import mekhane.mcp.ochema_mcp_server as ochema

        ochema._jules_api_key_pool = [(1, "test_key")]
        ochema._jules_api_key_index = 0

        from mekhane.mcp.ochema_mcp_server import _handle_jules

        result = await _handle_jules("jules_create_task", {"prompt": "", "repo": ""})
        assert "Error" in result[0].text

    @pytest.mark.asyncio
    async def test_jules_get_status_missing_id(self):
        """session_id 不足でエラー"""
        import mekhane.mcp.ochema_mcp_server as ochema

        ochema._jules_api_key_pool = [(1, "test_key")]
        ochema._jules_api_key_index = 0

        from mekhane.mcp.ochema_mcp_server import _handle_jules

        result = await _handle_jules("jules_get_status", {"session_id": ""})
        assert "Error" in result[0].text

    @pytest.mark.asyncio
    async def test_jules_list_repos(self):
        """list_repos は stub メッセージを返す"""
        import mekhane.mcp.ochema_mcp_server as ochema

        ochema._jules_api_key_pool = [(1, "test_key")]
        ochema._jules_api_key_index = 0

        from mekhane.mcp.ochema_mcp_server import _handle_jules

        result = await _handle_jules("jules_list_repos", {})
        assert "Repositories" in result[0].text

    @pytest.mark.asyncio
    async def test_jules_no_api_keys(self):
        """API キーなしでエラー"""
        import mekhane.mcp.ochema_mcp_server as ochema

        ochema._jules_api_key_pool = []

        with patch.dict("os.environ", {}, clear=True):
            from mekhane.mcp.ochema_mcp_server import _handle_jules

            result = await _handle_jules("jules_create_task", {"prompt": "test", "repo": "owner/repo"})
            assert "Error" in result[0].text or "No JULES" in result[0].text

    @pytest.mark.asyncio
    async def test_jules_batch_empty_tasks(self):
        """空タスクリストでエラー"""
        import mekhane.mcp.ochema_mcp_server as ochema

        ochema._jules_api_key_pool = [(1, "test_key")]
        ochema._jules_api_key_index = 0

        from mekhane.mcp.ochema_mcp_server import _handle_jules

        result = await _handle_jules("jules_batch_execute", {"tasks": []})
        assert "Error" in result[0].text


# ============ digestor: semantic scholar ============

class TestDigestorS2:
    """semantic-scholar → digestor に移植した S2 tools のテスト"""

    def _mock_paper(self, title="Test Paper", year=2025, citations=42):
        """テスト用 Paper 互換オブジェクト"""
        p = MagicMock()
        p.paper_id = "abc123"
        p.title = title
        p.year = year
        p.abstract = "An abstract."
        p.citation_count = citations
        p.doi = "10.1234/test"
        p.arxiv_id = None
        p.url = "https://example.com/paper"
        p.authors = ["Author A", "Author B"]
        return p

    @pytest.mark.asyncio
    async def test_paper_search_returns_results(self):
        """paper_search で結果が返る"""
        paper = self._mock_paper()

        with patch("mekhane.pks.semantic_scholar.SemanticScholarClient") as MockClient:
            instance = MockClient.return_value
            instance.search.return_value = [paper]

            from mekhane.mcp.digestor_mcp_server import handle_semantic_scholar

            result = await handle_semantic_scholar("paper_search", {"query": "FEP"})
            text = result[0].text
            assert "Test Paper" in text
            assert "42" in text

    @pytest.mark.asyncio
    async def test_paper_search_empty_query(self):
        """空クエリでエラー"""
        from mekhane.mcp.digestor_mcp_server import handle_semantic_scholar

        result = await handle_semantic_scholar("paper_search", {"query": ""})
        assert "Error" in result[0].text

    @pytest.mark.asyncio
    async def test_paper_details_returns_info(self):
        """paper_details で論文詳細が返る"""
        paper = self._mock_paper(title="FEP Paper")

        with patch("mekhane.pks.semantic_scholar.SemanticScholarClient") as MockClient:
            instance = MockClient.return_value
            instance.get_paper.return_value = paper

            from mekhane.mcp.digestor_mcp_server import handle_semantic_scholar

            result = await handle_semantic_scholar("paper_details", {"paper_id": "abc123"})
            text = result[0].text
            assert "FEP Paper" in text
            assert "42" in text

    @pytest.mark.asyncio
    async def test_paper_details_empty_id(self):
        """空 paper_id でエラー"""
        from mekhane.mcp.digestor_mcp_server import handle_semantic_scholar

        result = await handle_semantic_scholar("paper_details", {"paper_id": ""})
        assert "Error" in result[0].text

    @pytest.mark.asyncio
    async def test_paper_citations_returns_list(self):
        """paper_citations で被引用論文リストが返る"""
        papers = [self._mock_paper(title="Citing Paper", citations=10)]

        with patch("mekhane.pks.semantic_scholar.SemanticScholarClient") as MockClient:
            instance = MockClient.return_value
            instance.get_citations.return_value = papers

            from mekhane.mcp.digestor_mcp_server import handle_semantic_scholar

            result = await handle_semantic_scholar("paper_citations", {"paper_id": "abc123"})
            text = result[0].text
            assert "Citing Paper" in text
            assert "10" in text

    @pytest.mark.asyncio
    async def test_paper_citations_empty_id(self):
        """空 paper_id でエラー"""
        from mekhane.mcp.digestor_mcp_server import handle_semantic_scholar

        result = await handle_semantic_scholar("paper_citations", {"paper_id": ""})
        assert "Error" in result[0].text


# ============ sympatheia: basanos_scan ============

class TestSympatheiBasanosScan:
    """basanos_scan ツールのテスト"""

    @pytest.mark.asyncio
    async def test_basanos_import_ok(self):
        """AIAuditor が正しくインポートできる"""
        from mekhane.basanos.ai_auditor import AIAuditor
        auditor = AIAuditor(strict=False)
        assert auditor is not None

    @pytest.mark.asyncio
    async def test_basanos_scan_missing_path(self):
        """path 未指定でエラー"""
        from mekhane.mcp.sympatheia_mcp_server import _handle_basanos_scan
        result = await _handle_basanos_scan({})
        assert "Error" in result[0].text

    @pytest.mark.asyncio
    async def test_basanos_scan_nonexistent_path(self):
        """存在しないパスでエラー"""
        from mekhane.mcp.sympatheia_mcp_server import _handle_basanos_scan
        result = await _handle_basanos_scan({"path": "/nonexistent/file.py"})
        assert "not found" in result[0].text

    @pytest.mark.asyncio
    async def test_basanos_scan_file(self, tmp_path):
        """正常ケース: 単一ファイルスキャン"""
        test_file = tmp_path / "test_sample.py"
        test_file.write_text("x = 1\n")

        from mekhane.mcp.sympatheia_mcp_server import _handle_basanos_scan
        result = await _handle_basanos_scan({"path": str(test_file)})
        # Either no issues or issues found — both are valid
        assert len(result) == 1
        assert isinstance(result[0].text, str)


# ============ sympatheia: peira_health ============

class TestSympatheiaPeiraHealth:
    """peira_health ツールのテスト"""

    @pytest.mark.asyncio
    async def test_peira_import_ok(self):
        """run_health_check / format_terminal が正しくインポートできる"""
        from mekhane.peira.hgk_health import run_health_check, format_terminal
        assert callable(run_health_check)
        assert callable(format_terminal)

    @pytest.mark.asyncio
    async def test_peira_health_returns_text(self):
        """peira_health がテキスト結果を返す"""
        from mekhane.mcp.sympatheia_mcp_server import _handle_peira_health
        result = await _handle_peira_health()
        assert len(result) == 1
        assert isinstance(result[0].text, str)
        # Should contain some health-related output
        assert len(result[0].text) > 0


# ============ mneme: dendron_check ============

class TestMnemeDendronCheck:
    """dendron_check ツールのテスト"""

    @pytest.mark.asyncio
    async def test_dendron_import_ok(self):
        """DendronChecker が正しくインポートできる"""
        from mekhane.dendron.checker import DendronChecker
        checker = DendronChecker()
        assert checker is not None

    @pytest.mark.asyncio
    async def test_dendron_check_missing_path(self):
        """path 未指定でエラー"""
        from mekhane.mcp.mneme_server import _handle_dendron_check
        result = await _handle_dendron_check({})
        assert "Error" in result[0].text or "path" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_dendron_check_nonexistent_path(self):
        """存在しないパスでエラー"""
        from mekhane.mcp.mneme_server import _handle_dendron_check
        result = await _handle_dendron_check({"path": "/nonexistent/file.py"})
        assert "not found" in result[0].text or "Error" in result[0].text

    @pytest.mark.asyncio
    async def test_dendron_check_file(self, tmp_path):
        """正常ケース: PROOF ヘッダー付きファイル"""
        test_file = tmp_path / "test_proof.py"
        test_file.write_text("# PROOF: [L1/test] <- test\n# PURPOSE: test\nx = 1\n")

        from mekhane.mcp.mneme_server import _handle_dendron_check
        result = await _handle_dendron_check({"path": str(test_file)})
        assert len(result) == 1
        assert isinstance(result[0].text, str)

