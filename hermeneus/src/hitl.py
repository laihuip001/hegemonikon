# PROOF: [L2/インフラ] <- hermeneus/src/ HITL コントローラー
"""
Hermēneus HITL — Human-in-the-Loop 制御

高リスク操作や重要な判断ポイントで
人間の承認を要求するメカニズム。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime


# =============================================================================
# HITL Types
# =============================================================================

class InterruptType(Enum):
    """割り込みタイプ"""
    BEFORE = "before"           # ノード実行前
    AFTER = "after"             # ノード実行後
    ON_CONDITION = "condition"  # 条件付き


class HITLCommand(Enum):
    """HITL コマンド"""
    PROCEED = "proceed"         # 続行
    ROLLBACK = "rollback"       # ロールバック
    MODIFY = "modify"           # 状態修正
    ABORT = "abort"             # 中止
    RETRY = "retry"             # リトライ


@dataclass
class InterruptPoint:
    """割り込みポイント"""
    node_id: str
    type: InterruptType
    reason: str = ""
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None


@dataclass
class HITLRequest:
    """HITL リクエスト"""
    request_id: str
    thread_id: str
    node_id: str
    interrupt_type: InterruptType
    state: Dict[str, Any]
    reason: str
    created_at: datetime = field(default_factory=datetime.now)
    options: List[HITLCommand] = field(default_factory=lambda: list(HITLCommand))


@dataclass
class HITLResponse:
    """HITL レスポンス"""
    request_id: str
    command: HITLCommand
    user_input: Optional[str] = None
    state_modifications: Optional[Dict[str, Any]] = None
    responded_at: datetime = field(default_factory=datetime.now)


# =============================================================================
# HITL Controller
# =============================================================================

class HITLController:
    """Human-in-the-Loop コントローラー
    
    ワークフロー実行中に人間の介入を可能にする。
    """
    
    # PURPOSE: Initialize instance
    def __init__(self):
        self._interrupt_points: Dict[str, List[InterruptPoint]] = {}
        self._pending_requests: Dict[str, HITLRequest] = {}
        self._callbacks: Dict[str, Callable[[HITLRequest], HITLResponse]] = {}
        self._request_counter = 0
    
    # PURPOSE: リクエスト ID を生成
    def _generate_request_id(self) -> str:
        """リクエスト ID を生成"""
        self._request_counter += 1
        return f"hitl_{self._request_counter:06d}"
    
    # PURPOSE: 割り込みポイントを登録
    def register_interrupt(
        self,
        node_id: str,
        interrupt_type: InterruptType = InterruptType.BEFORE,
        reason: str = "",
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    ):
        """割り込みポイントを登録"""
        if node_id not in self._interrupt_points:
            self._interrupt_points[node_id] = []
        
        self._interrupt_points[node_id].append(InterruptPoint(
            node_id=node_id,
            type=interrupt_type,
            reason=reason,
            condition=condition
        ))
    
    # PURPOSE: コールバックを登録
    def register_callback(
        self,
        name: str,
        callback: Callable[[HITLRequest], HITLResponse]
    ):
        """コールバックを登録"""
        self._callbacks[name] = callback
    
    # PURPOSE: 割り込みが必要かチェック
    def should_interrupt(
        self,
        node_id: str,
        interrupt_type: InterruptType,
        state: Dict[str, Any]
    ) -> Optional[InterruptPoint]:
        """割り込みが必要かチェック"""
        if node_id not in self._interrupt_points:
            return None
        
        for point in self._interrupt_points[node_id]:
            if point.type != interrupt_type:
                continue
            
            if point.condition is None:
                return point
            
            if point.condition(state):
                return point
        
        return None
    
    # PURPOSE: HITL リクエストを作成
    def create_request(
        self,
        thread_id: str,
        point: InterruptPoint,
        state: Dict[str, Any]
    ) -> HITLRequest:
        """HITL リクエストを作成"""
        request = HITLRequest(
            request_id=self._generate_request_id(),
            thread_id=thread_id,
            node_id=point.node_id,
            interrupt_type=point.type,
            state=state.copy(),
            reason=point.reason
        )
        
        self._pending_requests[request.request_id] = request
        return request
    
    # PURPOSE: 保留中のリクエストを取得
    def get_pending_request(self, request_id: str) -> Optional[HITLRequest]:
        """保留中のリクエストを取得"""
        return self._pending_requests.get(request_id)
    
    # PURPOSE: 保留中のリクエストをリスト
    def list_pending_requests(self, thread_id: Optional[str] = None) -> List[HITLRequest]:
        """保留中のリクエストをリスト"""
        requests = list(self._pending_requests.values())
        if thread_id:
            requests = [r for r in requests if r.thread_id == thread_id]
        return sorted(requests, key=lambda r: r.created_at)
    
    # PURPOSE: リクエストに応答
    def respond(
        self,
        request_id: str,
        command: HITLCommand,
        user_input: Optional[str] = None,
        state_modifications: Optional[Dict[str, Any]] = None
    ) -> HITLResponse:
        """リクエストに応答"""
        if request_id not in self._pending_requests:
            raise ValueError(f"Request not found: {request_id}")
        
        response = HITLResponse(
            request_id=request_id,
            command=command,
            user_input=user_input,
            state_modifications=state_modifications
        )
        
        # リクエストを削除
        del self._pending_requests[request_id]
        
        return response
    
    # PURPOSE: レスポンスを状態に適用
    def apply_response(
        self,
        response: HITLResponse,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """レスポンスを状態に適用"""
        new_state = state.copy()
        
        if response.command == HITLCommand.MODIFY and response.state_modifications:
            new_state.update(response.state_modifications)
        
        if response.user_input:
            if "user_inputs" not in new_state:
                new_state["user_inputs"] = []
            new_state["user_inputs"].append(response.user_input)
        
        return new_state
    
    # PURPOSE: 応答を待機 (同期)
    def wait_for_response(
        self,
        request: HITLRequest,
        callback_name: str = "default",
        timeout: Optional[float] = None
    ) -> HITLResponse:
        """応答を待機 (同期)"""
        if callback_name in self._callbacks:
            return self._callbacks[callback_name](request)
        
        # デフォルト: 標準入力から読み取り
        return self._default_prompt(request)
    
    # PURPOSE: デフォルトのコンソールプロンプト
    def _default_prompt(self, request: HITLRequest) -> HITLResponse:
        """デフォルトのコンソールプロンプト"""
        print(f"\n{'='*60}")
        print(f"HITL 承認要求: {request.request_id}")
        print(f"ノード: {request.node_id}")
        print(f"理由: {request.reason}")
        print(f"{'='*60}")
        print("\nオプション:")
        for cmd in HITLCommand:
            print(f"  {cmd.value}: {cmd.name}")
        
        choice = input("\nコマンドを選択 (proceed/rollback/modify/abort/retry): ").strip().lower()
        
        try:
            command = HITLCommand(choice)
        except ValueError:
            command = HITLCommand.PROCEED
        
        user_input = None
        state_mods = None
        
        if command == HITLCommand.MODIFY:
            user_input = input("追加入力 (任意): ").strip() or None
        
        return self.respond(
            request.request_id,
            command,
            user_input=user_input,
            state_modifications=state_mods
        )


# =============================================================================
# Decorator for HITL
# =============================================================================

# PURPOSE: HITL 承認を要求するデコレータ
def requires_approval(
    reason: str = "承認が必要です",
    before: bool = True,
    after: bool = False,
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
):
    """HITL 承認を要求するデコレータ"""
    # PURPOSE: Decorator
    def decorator(func: Callable) -> Callable:
        func._hitl_config = {
            "reason": reason,
            "before": before,
            "after": after,
            "condition": condition
        }
        return func
    return decorator


# =============================================================================
# Convenience Functions
# =============================================================================

# PURPOSE: HITL コントローラーを作成
def create_hitl_controller() -> HITLController:
    """HITL コントローラーを作成"""
    return HITLController()


# PURPOSE: 高リスクノードを一括登録
def register_high_risk_nodes(
    controller: HITLController,
    node_ids: List[str],
    reason: str = "高リスク操作: 承認が必要です"
):
    """高リスクノードを一括登録"""
    for node_id in node_ids:
        controller.register_interrupt(
            node_id,
            InterruptType.BEFORE,
            reason=reason
        )
