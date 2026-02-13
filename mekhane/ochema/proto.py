# PROOF: [L2/Transport] <- mekhane/ochema/ Protocol Definitions
# PURPOSE: Ochema (LLM Server) との通信プロトコル定義
"""
Ochema Protocol Definitions
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

# PURPOSE: リクエスト/レスポンスモデル

class ChatMessage(BaseModel):
    """チャットメッセージ"""
    role: str
    content: str

class CompletionRequest(BaseModel):
    """補完リクエスト"""
    model: str
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 1000
    stop: Optional[List[str]] = None
    stream: bool = False

class CompletionResponse(BaseModel):
    """補完レスポンス"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
