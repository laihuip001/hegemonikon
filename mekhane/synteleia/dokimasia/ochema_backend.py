# PROOF: [L2/Dokimasia] <- mekhane/synteleia/dokimasia/ Ochema Backend Test
# PURPOSE: [L2-auto] Ochema Backend のモックおよびテスト用ユーティリティ
"""
Ochema Backend Mock Module.

Ochema (Antigravity LS) との通信をシミュレートするバックエンドモック。
本番環境での接続を行わずに統合テストを実行するために使用。
"""

from typing import Dict, Any, Optional, List
import json
import uuid
import time
from dataclasses import dataclass, field

@dataclass
class MockResponse:
    """モックレスポンス"""
    text: str
    delay_ms: int = 100
    error: Optional[str] = None

class OchemaBackendMock:
    """Ochema Backend (Mock)"""

    def __init__(self):
        self._responses: Dict[str, MockResponse] = {}
        self._history: List[Dict[str, Any]] = []
        self._connected = False

    def connect(self) -> bool:
        """接続シミュレーション"""
        self._connected = True
        return True

    def disconnect(self):
        """切断シミュレーション"""
        self._connected = False

    def send_message(self, message: str, model: str = "default") -> Dict[str, Any]:
        """メッセージ送信 (同期的に応答)"""
        if not self._connected:
            raise ConnectionError("Not connected to Ochema backend")

        req_id = str(uuid.uuid4())
        self._history.append({
            "id": req_id,
            "role": "user",
            "content": message,
            "timestamp": time.time()
        })

        # 定義済み応答があれば返す、なければエコー
        response = self._responses.get(message, MockResponse(text=f"Echo: {message}"))

        if response.error:
            raise RuntimeError(response.error)

        time.sleep(response.delay_ms / 1000.0)

        return {
            "id": str(uuid.uuid4()),
            "reply_to": req_id,
            "role": "assistant",
            "content": response.text,
            "model": model
        }

    def register_response(self, trigger: str, response: MockResponse):
        """特定のメッセージに対する応答を登録"""
        self._responses[trigger] = response
