#!/bin/bash
pip install pytest pytest-asyncio pytest-timeout pyyaml pydantic lancedb numpy scipy \
            networkx pandas tabulate requests httpx schedule
pip install sentence-transformers torch --index-url https://download.pytorch.org/whl/cpu
pip install fastapi uvicorn aiohttp python-dotenv filelock aioresponses
