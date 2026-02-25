# PROOF: [L2/Mekhane] <- mekhane/api/routes/
# PURPOSE: /ask/agent/* — Agent Self-Modification PoC Endpoints
"""
Agent Routes — Self-Modification PoC

POST /ask/agent         — Request a change
POST /ask/agent/approve — Approve a change
"""

import logging
from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger("hegemonikon.api.agent")

class AgentRequest(BaseModel):
    """Request to the agent."""
    prompt: str = Field(..., description="The user's request")

class AgentResponse(BaseModel):
    """Agent's response with a plan."""
    plan: str
    status: str
    requires_approval: bool

class ApprovalRequest(BaseModel):
    """Approval decision."""
    approved: bool

class ApprovalResponse(BaseModel):
    """Result of the approval."""
    status: str
    result: str

router = APIRouter(prefix="/ask/agent", tags=["agent"])

@router.post("", response_model=AgentResponse)
async def ask_agent(req: AgentRequest):
    """Submit a request to the agent."""
    logger.info("Agent received request: %s", req.prompt)
    # Mock response for PoC
    return AgentResponse(
        plan=f"Proposed plan for: {req.prompt}\n1. Analyze\n2. Modify\n3. Verify",
        status="waiting_for_approval",
        requires_approval=True
    )

@router.post("/approve", response_model=ApprovalResponse)
async def approve_change(req: ApprovalRequest):
    """Approve or reject the agent's plan."""
    if req.approved:
        logger.info("Agent plan approved.")
        return ApprovalResponse(status="success", result="Changes applied successfully.")
    else:
        logger.info("Agent plan rejected.")
        return ApprovalResponse(status="rejected", result="Changes discarded.")
