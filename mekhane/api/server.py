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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mekhane.api import API_PREFIX, API_TITLE, DEFAULT_PORT, __version__

# PURPOSE: デフォルト UDS パス
DEFAULT_UDS_PATH = "/tmp/hgk.sock"

# PURPOSE: ロギング設定
logger = logging.getLogger("hegemonikon.api")


# PURPOSE: FastAPI アプリケーション生成
def create_app() -> FastAPI:
    """FastAPI インスタンスを生成し、ルーターをマウントする。"""
    app = FastAPI(
        title=API_TITLE,
        version=__version__,
        description="Hegemonikón mekhane モジュールの REST API",
        docs_url=f"{API_PREFIX}/docs",
        redoc_url=f"{API_PREFIX}/redoc",
        openapi_url=f"{API_PREFIX}/openapi.json",
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
    _mount_routers(app)

    return app


# PURPOSE: 全ルーターをマウント（Gnōsis は遅延ロードで安全に）
def _mount_routers(app: FastAPI) -> None:
    """各ルートモジュールのルーターをマウントする。"""
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


# PURPOSE: アプリケーションインスタンス（uvicorn 用）
app = create_app()


# PURPOSE: 残留ソケットファイルの安全な削除
def _remove_stale_socket(uds_path: str) -> None:
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
        _remove_stale_socket(args.uds)
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
