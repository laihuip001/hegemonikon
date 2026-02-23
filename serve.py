#!/usr/bin/env python3
# PURPOSE: Phase 5 Self-Modification PoC Target Application
# PROOF: [L2/Verification] <- PoC Target

from fastapi import FastAPI
import uvicorn
import sys

app = FastAPI()

@app.get("/api/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = 9999
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    uvicorn.run(app, host="127.0.0.1", port=port)
