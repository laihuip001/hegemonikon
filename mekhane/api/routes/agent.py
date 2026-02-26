# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: Phase 5 Self-Modification Agent API
"""
Agent Routes — Self-modification proof-of-concept.

POST /ask/agent/         — Propose a modification
POST /ask/agent/approve  — Approve and apply a modification
"""

import uuid
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# In-memory storage for proposals
_proposals: Dict[str, Any] = {}

router = APIRouter(prefix="/ask/agent", tags=["agent"])


class ProposalRequest(BaseModel):
    instruction: str
    target_file: str


class ProposalResponse(BaseModel):
    proposal_id: str
    diff: str
    status: str


class ApproveRequest(BaseModel):
    proposal_id: str


class ApproveResponse(BaseModel):
    status: str


@router.post("/", response_model=ProposalResponse)
async def propose_modification(request: ProposalRequest) -> ProposalResponse:
    """Creates a modification proposal based on instruction."""
    proposal_id = str(uuid.uuid4())

    # Dummy diff generation for POC
    # In a real implementation, this would involve LLM reasoning and file parsing.
    diff = (
        f"--- {request.target_file}\n"
        f"+++ {request.target_file}\n"
        f"@@ -1,1 +1,2 @@\n"
        f"+ # Agent modification: {request.instruction}\n"
    )

    _proposals[proposal_id] = {
        "id": proposal_id,
        "instruction": request.instruction,
        "target_file": request.target_file,
        "diff": diff,
        "status": "pending"
    }

    return ProposalResponse(
        proposal_id=proposal_id,
        diff=diff,
        status="pending"
    )


@router.post("/approve", response_model=ApproveResponse)
async def approve_modification(request: ApproveRequest) -> ApproveResponse:
    """Approves and applies a modification proposal."""
    proposal = _proposals.get(request.proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # In a real implementation, this would apply the diff/changes to the file system.
    # For POC, we just mark it as applied in memory.
    proposal["status"] = "applied"

    return ApproveResponse(status="applied")
