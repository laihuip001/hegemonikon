# PROOF: [L2/Mekhane] <- mekhane/api/ A0->Auto->AddedByCI
#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/
# PURPOSE: FastAPI アプリケーション本体 — CORS, ルーター登録, uvicorn 起動
"""
Hegemonikón API Server

Tauri v2 デスクトップアプリのバックエンド。
既存の mekhane/* モジュールを REST API として公開する。

Usage:
    # TCP モード (開発・n8n 連携用)
    python -m mekhane.api.server
    python -m mekhane.api.server --port 9696

    # UDS モード (Tauri デスクトップアプリ用)
    python -m mekhane.api.server --uds /tmp/hgk.sock
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

# R4 fix: scripts/ パッケージが PYTHONPATH なしで import 可能になるよう
# プロジェクトルートを sys.path に追加
_PROJECT_ROOT = Path(__file__).resolve().parents[2]  # hegemonikon/
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mekhane.api import API_PREFIX, API_TITLE, DEFAULT_PORT, __version__


# PURPOSE: Embedder を起動時に事前ロード (warm cache for /boot-context)
@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Startup: Embedder 事前ロード → Shutdown: cleanup."""
    import asyncio
    try:
        def _preload():
            # Vertex AI Embedding に切り替え (ローカル Embedder を廃止)
            from mekhane.anamnesis.vertex_embedder import VertexEmbedder
            embedder = VertexEmbedder()
            logger.info(
                "VertexEmbedder preloaded: %s (dim=%d, gpu=%s)",
                embedder.model_name, embedder._dimension, embedder._use_gpu,
            )
            return embedder

        embedder = await asyncio.to_thread(_preload)
        # 後方互換のため app.state.embedder に格納
        app.state.embedder = embedder
        logger.info("🧠 VertexEmbedder warm cache ready")
    except Exception as exc:
        logger.warning("VertexEmbedder preload failed (non-fatal): %s", exc)
        app.state.embedder = None
    yield
    # Shutdown — nothing to cleanup for now

# PURPOSE: デフォルト UDS パス
DEFAULT_UDS_PATH = "/tmp/hgk.sock"

# PURPOSE: ロギング設定
logger = logging.getLogger("hegemonikon.api")


# PURPOSE: FastAPI アプリケーション生成
def create_app() -> FastAPI:
    """FastAPI インスタンスを生成し、ルーターを登録する。"""
    app = FastAPI(
        title=API_TITLE,
        version=__version__,
        description="Hegemonikón mekhane モジュールの REST API",
        docs_url=f"{API_PREFIX}/docs",
        redoc_url=f"{API_PREFIX}/redoc",
        openapi_url=f"{API_PREFIX}/openapi.json",
        lifespan=_lifespan,
    )

    # CORS — TCP モード時のみ意味がある（UDS では不要だが害もない）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # R3 fix: app.state.start_time でサーバー起動時刻を正確に記録
    app.state.start_time = time.time()

    # ルーター登録
    _register_routers(app)

    return app


# PURPOSE: 全ルーターを登録（Gnōsis は遅延ロードで安全に）
def _register_routers(app: FastAPI) -> None:
    """各ルートモジュールのルーターを登録する。"""
    from mekhane.api.routes.status import router as status_router
    from mekhane.api.routes.fep import router as fep_router
    from mekhane.api.routes.postcheck import router as postcheck_router
    from mekhane.api.routes.dendron import router as dendron_router
    from mekhane.api.routes.graph import router as graph_router

    app.include_router(status_router, prefix=API_PREFIX)
    app.include_router(fep_router, prefix=API_PREFIX)
    app.include_router(postcheck_router, prefix=API_PREFIX)
    app.include_router(dendron_router, prefix=API_PREFIX)
    app.include_router(graph_router, prefix=API_PREFIX)

    # Gnōsis — shape mismatch の可能性があるため遅延ロード
    try:
        from mekhane.api.routes.gnosis import router as gnosis_router
        app.include_router(gnosis_router, prefix=API_PREFIX)
        logger.info("Gnōsis router registered")
    except Exception as exc:
        logger.warning("Gnōsis router skipped: %s", exc)

    # CCL — Hermēneus/Synergeia に依存するため遅延ロード
    try:
        from mekhane.api.routes.ccl import router as ccl_router
        app.include_router(ccl_router, prefix=API_PREFIX)
        logger.info("CCL router registered")
    except Exception as exc:
        logger.warning("CCL router skipped: %s", exc)

    # Sympatheia — AttractorAdvisor (モデルロード) に依存するため遅延ロード
    try:
        from mekhane.api.routes.sympatheia import router as sympatheia_router
        app.include_router(sympatheia_router, prefix=API_PREFIX)
        logger.info("Sympatheia router registered")
    except Exception as exc:
        logger.warning("Sympatheia router skipped: %s", exc)

    # Cortex — Lite proxy for Gemini
    try:
        from mekhane.api.routes.cortex import router as cortex_router
        # Cortex router は API_PREFIX に既に /cortex が含まれている前提なので、prefix をどうするか確認
        # cortex.py で prefix="/api/cortex" としているので、ここでは prefix="" または削除
        app.include_router(cortex_router)
        logger.info("Cortex router registered")
    except Exception as exc:
        logger.warning("Cortex router skipped: %s", exc)

    # PKS — 埋め込みモデルに依存するため遅延ロード
    try:
        from mekhane.api.routes.pks import router as pks_router
        app.include_router(pks_router, prefix=API_PREFIX)
        logger.info("PKS router registered")
    except Exception as exc:
        logger.warning("PKS router skipped: %s", exc)

    # Gnōsis Narrator — PKSEngine + PKSNarrator に依存するため遅延ロード
    try:
        from mekhane.api.routes.gnosis_narrator import router as narrator_router
        app.include_router(narrator_router, prefix=API_PREFIX)
        logger.info("Gnōsis Narrator router registered")
    except Exception as exc:
        logger.warning("Gnōsis Narrator router skipped: %s", exc)

    # Link Graph — ファイルシステム IO に依存するため遅延ロード
    try:
        from mekhane.api.routes.link_graph import router as link_graph_router
        app.include_router(link_graph_router, prefix=API_PREFIX)
        logger.info("Link Graph router registered")
    except Exception as exc:
        logger.warning("Link Graph router skipped: %s", exc)

    # Sophia KI — ファイルシステム CRUD
    try:
        from mekhane.api.routes.sophia import router as sophia_router
        app.include_router(sophia_router, prefix=API_PREFIX)
        logger.info("Sophia KI router registered")
    except Exception as exc:
        logger.warning("Sophia KI router skipped: %s", exc)

    # Symploke — 埋め込みモデル (ベクトル検索) に依存するため遅延ロード
    try:
        from mekhane.api.routes.symploke import router as symploke_router
        app.include_router(symploke_router, prefix=API_PREFIX)
        logger.info("Symploke router registered")
    except Exception as exc:
        logger.warning("Symploke router skipped: %s", exc)

    # Synteleia — 6視点認知アンサンブル監査 (外部依存なし)
    try:
        from mekhane.api.routes.synteleia import router as synteleia_router
        app.include_router(synteleia_router, prefix=API_PREFIX)
        logger.info("Synteleia router registered")
    except Exception as exc:
        logger.warning("Synteleia router skipped: %s", exc)

    # Basanos — SweepEngine 多視点スキャン + ResponseCache
    try:
        from mekhane.api.routes.basanos import router as basanos_router
        app.include_router(basanos_router, prefix=API_PREFIX)
        logger.info("Basanos router registered")
    except Exception as exc:
        logger.warning("Basanos router skipped: %s", exc)

    # Timeline — セッション・タイムライン (ファイルシステム IO のみ)
    try:
        from mekhane.api.routes.timeline import router as timeline_router
        app.include_router(timeline_router, prefix=API_PREFIX)
        logger.info("Timeline router registered")
    except Exception as exc:
        logger.warning("Timeline router skipped: %s", exc)

    # Kalon — Fix(G∘F) 判定の記録と参照
    try:
        from mekhane.api.routes.kalon import router as kalon_router
        app.include_router(kalon_router, prefix=API_PREFIX)
        logger.info("Kalon router registered")
    except Exception as exc:
        logger.warning("Kalon router skipped: %s", exc)

    # MCP Gateway — PolicyEnforcer + DiscoveryEngine に依存するため遅延ロード
    try:
        from mekhane.api.routes.gateway import router as gateway_router
        app.include_router(gateway_router, prefix=API_PREFIX)
        logger.info("Gateway router registered")
    except Exception as exc:
        logger.warning("Gateway router skipped: %s", exc)

    # Digestor — 候補レポート閲覧 (ファイルシステム IO のみ)
    try:
        from mekhane.api.routes.digestor import router as digestor_router
        app.include_router(digestor_router, prefix=API_PREFIX)
        logger.info("Digestor router registered")
    except Exception as exc:
        logger.warning("Digestor router skipped: %s", exc)

    # Chat — Gemini API SSE プロキシ (httpx に依存するため遅延ロード)
    try:
        from mekhane.api.routes.chat import router as chat_router
        app.include_router(chat_router, prefix=API_PREFIX)
        logger.info("Chat router registered")
    except Exception as exc:
        logger.warning("Chat router skipped: %s", exc)

    # Quota — agq-check.sh (subprocess) に依存するため遅延ロード
    try:
        from mekhane.api.routes.quota import router as quota_router
        app.include_router(quota_router, prefix=API_PREFIX)
        logger.info("Quota router registered")
    except Exception as exc:
        logger.warning("Quota router skipped: %s", exc)

    # Aristos — L2 Evolution Dashboard (ファイルシステム IO のみ)
    try:
        from mekhane.api.routes.aristos import router as aristos_router
        app.include_router(aristos_router, prefix=API_PREFIX)
        logger.info("Aristos router registered")
    except Exception as exc:
        logger.warning("Aristos router skipped: %s", exc)

    # Sentinel — Paper Sentinel レポート (ファイルシステム IO のみ)
    try:
        from mekhane.api.routes.sentinel import router as sentinel_router
        app.include_router(sentinel_router, prefix=API_PREFIX)
        logger.info("Sentinel router registered")
    except Exception as exc:
        logger.warning("Sentinel router skipped: %s", exc)

    # Epistemic — 認識論的地位レジストリ (YAML ファイル IO のみ)
    try:
        from mekhane.api.routes.epistemic import router as epistemic_router
        app.include_router(epistemic_router, prefix=API_PREFIX)
        logger.info("Epistemic router registered")
    except Exception as exc:
        logger.warning("Epistemic router skipped: %s", exc)

    # Scheduler — Jules Daily Scheduler ログ (ファイルシステム IO のみ)
    try:
        from mekhane.api.routes.scheduler import router as scheduler_router
        app.include_router(scheduler_router, prefix=API_PREFIX)
        logger.info("Scheduler router registered")
    except Exception as exc:
        logger.warning("Scheduler router skipped: %s", exc)

    # Periskopē — 研究エンジン API (非同期研究リクエスト・履歴参照)
    try:
        from mekhane.api.routes.periskope import router as periskope_router
        app.include_router(periskope_router, prefix=API_PREFIX)
        logger.info("Periskopē router registered")
    except Exception as exc:
        logger.warning("Periskopē router skipped: %s", exc)

    # Theorem — 定理使用頻度トラッキング (ファイルシステム IO のみ)
    try:
        from mekhane.api.routes.theorem import router as theorem_router
        app.include_router(theorem_router, prefix=API_PREFIX)
        logger.info("Theorem router registered")
    except Exception as exc:
        logger.warning("Theorem router skipped: %s", exc)

    # WAL — Intent-WAL ダッシュボードカード (ファイルシステム IO のみ)
    try:
        from mekhane.api.routes.wal import router as wal_router
        app.include_router(wal_router, prefix=API_PREFIX)
        logger.info("WAL router registered")
    except Exception as exc:
        logger.warning("WAL router skipped: %s", exc)

    # DevTools — ファイル操作・ターミナル・Ochema AI (CortexClient に依存)
    try:
        from mekhane.api.routes.devtools import router as devtools_router
        app.include_router(devtools_router, prefix=API_PREFIX)
        logger.info("DevTools router registered")
    except Exception as exc:
        logger.warning("DevTools router skipped: %s", exc)



# PURPOSE: アプリケーションインスタンス（uvicorn 用）
app = create_app()


# PURPOSE: 残留ソケットファイルの安全な削除
def _cleanup_stale_socket(uds_path: str) -> None:
    """前回のクラッシュで残ったソケットファイルを削除する。"""
    sock = Path(uds_path)
    if sock.exists():
        try:
            # ソケットファイルかどうか確認
            import stat
            if stat.S_ISSOCK(sock.stat().st_mode):
                sock.unlink()
                logger.info("Removed stale socket: %s", uds_path)
            else:
                logger.error("%s exists but is not a socket file", uds_path)
                sys.exit(1)
        except OSError as e:
            logger.error("Cannot remove %s: %s", uds_path, e)
            sys.exit(1)


# PURPOSE: CLI エントリポイント
def main() -> int:
    """サーバーを起動する。"""
    import uvicorn

    parser = argparse.ArgumentParser(description="Hegemonikón API Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port (default: {DEFAULT_PORT})")
    parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    parser.add_argument("--uds", type=str, default=None,
                        help=f"Unix Domain Socket path (default: None, use --uds for Tauri mode)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    if args.uds:
        # UDS モード — Tauri デスクトップアプリ用
        _cleanup_stale_socket(args.uds)
        logger.info("Starting Hegemonikón API on UDS: %s", args.uds)
        uvicorn.run(
            "mekhane.api.server:app",
            uds=args.uds,
            reload=args.reload,
            log_level="info",
        )
    else:
        # TCP モード — 開発・n8n 連携用
        logger.info("Starting Hegemonikón API on %s:%d", args.host, args.port)
        uvicorn.run(
            "mekhane.api.server:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
