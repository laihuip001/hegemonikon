#!/bin/bash
pip install pytest pytest-asyncio pytest-timeout pyyaml pydantic lancedb numpy scipy \
            networkx pandas tabulate requests httpx schedule \
            sentence-transformers torch fastapi[all] uvicorn python-dotenv aiohttp aioresponses \
            --extra-index-url https://download.pytorch.org/whl/cpu
