#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/
# PURPOSE: FastAPI アプリケーション本体 — CORS, ルーター登録, uvicorn 起動
"""
Hegemonikón API Server

Tauri v2 デスクトップアプリのバックエンド。
既存の mekhane/* モジュールを REST API として公開する。

Usage:
    PYTHONPATH=. python -m mekhane.api.server
    PYTHONPATH=. python -m mekhane.api.server --port 9696
"""

import argparse
import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mekhane.api import API_PREFIX, API_TITLE, DEFAULT_PORT, __version__

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
    )

    # CORS — Tauri WebView (localhost) からのアクセスを許可
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Tauri は tauri://localhost を使う
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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

    app.include_router(status_router, prefix=API_PREFIX)
    app.include_router(fep_router, prefix=API_PREFIX)
    app.include_router(postcheck_router, prefix=API_PREFIX)
    app.include_router(dendron_router, prefix=API_PREFIX)

    # Gnōsis — shape mismatch の可能性があるため遅延ロード
    try:
        from mekhane.api.routes.gnosis import router as gnosis_router
        app.include_router(gnosis_router, prefix=API_PREFIX)
        logger.info("Gnōsis router registered")
    except Exception as exc:
        logger.warning("Gnōsis router skipped: %s", exc)


# PURPOSE: アプリケーションインスタンス（uvicorn 用）
app = create_app()


# PURPOSE: CLI エントリポイント
def main() -> int:
    """サーバーを起動する。"""
    import uvicorn

    parser = argparse.ArgumentParser(description="Hegemonikón API Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port (default: {DEFAULT_PORT})")
    parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

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
