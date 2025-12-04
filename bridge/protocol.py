#!/usr/bin/env python3
"""
Ortensia WebSocket 消息协议定义

定义了中央Server与各 Client 之间通信的消息格式和数据类型。
参考文档: docs/WEBSOCKET_PROTOCOL.md
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import time
import json


# ============================================================================
# 枚举类型定义
# ============================================================================

class ClientType(str, Enum):
    """客户端类型"""
    CURSOR_HOOK = "cursor_hook"
    COMMAND_CLIENT = "command_client"
    AITUBER_CLIENT = "aituber_client"


class AgentStatus(str, Enum):
    """Agent 状态"""
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    COMPLETED = "completed"


class TaskResult(str, Enum):
    """任务执行结果"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class Platform(str, Enum):
    """操作系统平台"""
    DARWIN = "darwin"
    WIN32 = "win32"
    LINUX = "linux"


class Capability(str, Enum):
    """Cursor 支持的能力"""
    COMPOSER = "composer"
    EDITOR = "editor"
    TERMINAL = "terminal"
    GIT = "git"


class DisconnectReason(str, Enum):
    """断开连接原因"""
    USER_QUIT = "user_quit"
    RESTART = "restart"
    ERROR = "error"


class MessageType(str, Enum):
    """消息类型"""
    # 连接管理
    REGISTER = "register"
    REGISTER_ACK = "register_ack"
    HEARTBEAT = "heartbeat"
    HEARTBEAT_ACK = "heartbeat_ack"
    DISCONNECT = "disconnect"
    
    # Composer 操作（底层）
    COMPOSER_SEND_PROMPT = "composer_send_prompt"
    COMPOSER_SEND_PROMPT_RESULT = "composer_send_prompt_result"
    COMPOSER_QUERY_STATUS = "composer_query_status"
    COMPOSER_STATUS_RESULT = "composer_status_result"
    
    # Agent 操作（高层次语义）
    AGENT_EXECUTE_PROMPT = "agent_execute_prompt"
    AGENT_EXECUTE_PROMPT_RESULT = "agent_execute_prompt_result"
    AGENT_STOP_EXECUTION = "agent_stop_execution"
    AGENT_STOP_EXECUTION_RESULT = "agent_stop_execution_result"
    
    # 事件通知
    AGENT_STATUS_CHANGED = "agent_status_changed"
    AGENT_COMPLETED = "agent_completed"
    AGENT_ERROR = "agent_error"
    
    # AITuber 操作
    AITUBER_SPEAK = "aituber_speak"              # AITuber 说话/显示文本
    AITUBER_RECEIVE_TEXT = "aituber_receive_text"  # 发送文本给 AITuber
    AITUBER_EMOTION = "aituber_emotion"          # AITuber 情绪变化
    AITUBER_STATUS = "aituber_status"            # AITuber 状态更新
    
    # V10: Conversation ID 操作
    GET_CONVERSATION_ID = "get_conversation_id"  # 查询 inject 的 conversation_id
    GET_CONVERSATION_ID_RESULT = "get_conversation_id_result"  # conversation_id 查询结果
    
    # Cursor 输入操作
    CURSOR_INPUT_TEXT = "cursor_input_text"  # 向 Cursor 输入文本（不执行）
    CURSOR_INPUT_TEXT_RESULT = "cursor_input_text_result"  # 输入文本结果
    
    # 通用 JavaScript 执行（inject 专用）
    EXECUTE_JS = "execute_js"  # 在 Cursor 中执行 JavaScript 代码
    EXECUTE_JS_RESULT = "execute_js_result"  # JavaScript 执行结果


# ============================================================================
# Payload 数据类定义
# ============================================================================

@dataclass
class RegisterPayload:
    """注册消息的 Payload（支持多角色）"""
    platform: Platform
    pid: int
    
    # 🆕 多角色支持（推荐使用）
    client_types: Optional[List[str]] = None  # 角色列表，如 ["aituber", "command_client"]
    
    # 向后兼容：单角色（如果 client_types 为空，使用此字段）
    client_type: Optional[ClientType] = None
    
    # Cursor Hook 专用字段
    cursor_id: Optional[str] = None
    workspace: Optional[str] = None
    ws_port: Optional[int] = None
    capabilities: Optional[List[Capability]] = None


@dataclass
class RegisterAckPayload:
    """注册确认消息的 Payload"""
    success: bool
    assigned_id: Optional[str] = None
    server_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class ComposerSendPromptPayload:
    """发送提示词的 Payload"""
    agent_id: str
    prompt: str
    wait_for_start: bool = False


@dataclass
class ComposerSendPromptResultPayload:
    """提示词发送结果的 Payload"""
    success: bool
    agent_id: str
    message: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ComposerQueryStatusPayload:
    """查询 Agent 状态的 Payload"""
    agent_id: str


@dataclass
class ComposerStatusResultPayload:
    """Agent 状态查询结果的 Payload"""
    success: bool
    agent_id: str
    status: Optional[AgentStatus] = None
    error: Optional[str] = None


# ============================================================================
# 高层次语义操作 Payload（Agent 操作）
# ============================================================================

@dataclass
class AgentExecutePromptPayload:
    """执行提示词的 Payload（高层次语义操作）
    
    这是一个完整的语义操作，包括：
    1. 输入提示词
    2. 提交执行
    3. 可选：等待完成
    """
    agent_id: str
    prompt: str
    wait_for_completion: bool = False  # 是否等待执行完成
    timeout: int = 300000              # 超时时间（ms），默认 5 分钟
    clear_first: bool = True           # 是否先清空输入框


@dataclass
class AgentExecutePromptResultPayload:
    """执行提示词结果的 Payload"""
    success: bool
    agent_id: str
    phase: str                          # 执行到哪个阶段: input, submit, executing, completed
    message: Optional[str] = None
    error: Optional[str] = None
    input_completed: bool = False       # 输入是否完成
    submit_completed: bool = False      # 提交是否完成
    execution_time: Optional[int] = None  # 执行时间（ms）
    status: Optional[AgentStatus] = None  # 最终状态


@dataclass
class AgentStopExecutionPayload:
    """停止 Agent 执行的 Payload"""
    agent_id: str
    reason: Optional[str] = None        # 停止原因


@dataclass
class AgentStopExecutionResultPayload:
    """停止执行结果的 Payload"""
    success: bool
    agent_id: str
    message: Optional[str] = None
    error: Optional[str] = None


@dataclass
class AgentStatusChangedPayload:
    """Agent 状态变化事件的 Payload"""
    agent_id: str
    old_status: AgentStatus
    new_status: AgentStatus
    task_description: Optional[str] = None


@dataclass
class AgentCompletedPayload:
    """Agent 任务完成事件的 Payload"""
    agent_id: str
    result: TaskResult
    files_modified: List[str] = field(default_factory=list)
    summary: Optional[str] = None


@dataclass
class AgentErrorPayload:
    """Agent 错误事件的 Payload"""
    agent_id: str
    error_type: str
    error_message: str
    can_retry: bool = False


@dataclass
class HeartbeatAckPayload:
    """心跳响应的 Payload"""
    server_time: int


@dataclass
class DisconnectPayload:
    """断开连接的 Payload"""
    reason: DisconnectReason


@dataclass
class GetConversationIdPayload:
    """查询 conversation_id 的 Payload (V10)"""
    pass  # 无需额外参数


@dataclass
class GetConversationIdResultPayload:
    """conversation_id 查询结果的 Payload (V10)"""
    success: bool
    conversation_id: Optional[str] = None
    inject_id: Optional[str] = None  # 返回 inject 自己的 ID
    error: Optional[str] = None


@dataclass
class CursorInputTextPayload:
    """向 Cursor 输入文本的 Payload"""
    text: str  # 要输入的文本
    conversation_id: Optional[str] = None  # 目标对话ID（可选）
    execute: bool = False  # 是否立即执行（按 Enter 键）


@dataclass
class CursorInputTextResultPayload:
    """Cursor 输入文本结果的 Payload"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ExecuteJsPayload:
    """执行 JavaScript 的 Payload"""
    code: str  # JavaScript 代码
    request_id: Optional[str] = None  # 请求 ID（用于匹配响应）


@dataclass
class ExecuteJsResultPayload:
    """JavaScript 执行结果的 Payload"""
    success: bool
    result: Optional[Any] = None  # 执行结果
    error: Optional[str] = None
    request_id: Optional[str] = None


# ============================================================================
# 消息基础类
# ============================================================================

@dataclass
class Message:
    """
    WebSocket 消息基础类
    
    所有消息都包含这些基础字段
    """
    type: MessageType
    from_: str  # 使用 from_ 避免与 Python 关键字冲突
    timestamp: int
    payload: Dict[str, Any]
    to: Optional[str] = None  # None 或 "" 表示广播
    
    def __post_init__(self):
        """自动设置时间戳"""
        if self.timestamp == 0:
            self.timestamp = int(time.time())
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        data = {
            "type": self.type.value if isinstance(self.type, Enum) else self.type,
            "from": self.from_,
            "to": self.to or "",
            "timestamp": self.timestamp,
            "payload": self.payload
        }
        return json.dumps(data, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """从 JSON 字符串创建消息"""
        data = json.loads(json_str)
        return cls(
            type=MessageType(data["type"]),
            from_=data["from"],
            to=data.get("to") or None,
            timestamp=data["timestamp"],
            payload=data["payload"]
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """从字典创建消息"""
        return cls(
            type=MessageType(data["type"]),
            from_=data["from"],
            to=data.get("to") or None,
            timestamp=data["timestamp"],
            payload=data["payload"]
        )


# ============================================================================
# 消息构建器
# ============================================================================

class MessageBuilder:
    """消息构建器，提供便捷的消息创建方法"""
    
    @staticmethod
    def register(
        from_id: str,
        platform: Platform,
        pid: int,
        client_type: ClientType = None,  # 🆕 单角色（向后兼容）
        client_types: List[str] = None,  # 🆕 多角色（推荐）
        **kwargs
    ) -> Message:
        """
        创建注册消息（支持多角色）
        
        Args:
            from_id: 客户端 ID
            platform: 平台类型
            pid: 进程 ID
            client_type: 单角色（旧协议，向后兼容）
            client_types: 多角色列表（新协议，推荐）
            **kwargs: 其他字段
        
        Examples:
            # 单角色（旧方式）
            MessageBuilder.register("client-1", Platform.DARWIN, 1234, 
                                   client_type=ClientType.AITUBER_CLIENT)
            
            # 多角色（新方式）
            MessageBuilder.register("client-1", Platform.DARWIN, 1234,
                                   client_types=["aituber_client", "command_client"])
        """
        # 优先使用 client_types，如果没有则使用 client_type
        if client_types:
            types_to_use = client_types
            type_to_use = None
        elif client_type:
            types_to_use = None
            type_to_use = client_type
        else:
            # 都没有，默认 unknown
            types_to_use = None
            type_to_use = ClientType.CURSOR_HOOK  # 使用一个默认值
        
        payload = RegisterPayload(
            platform=platform,
            pid=pid,
            client_type=type_to_use,
            client_types=types_to_use,
            cursor_id=kwargs.get('cursor_id'),
            workspace=kwargs.get('workspace'),
            ws_port=kwargs.get('ws_port'),
            capabilities=kwargs.get('capabilities')
        )
        
        return Message(
            type=MessageType.REGISTER,
            from_=from_id,
            to="server",
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    @staticmethod
    def register_ack(
        to_id: str,
        success: bool,
        assigned_id: Optional[str] = None,
        server_info: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> Message:
        """创建注册确认消息"""
        payload = RegisterAckPayload(
            success=success,
            assigned_id=assigned_id,
            server_info=server_info,
            error=error
        )
        
        return Message(
            type=MessageType.REGISTER_ACK,
            from_="server",
            to=to_id,
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    @staticmethod
    def composer_send_prompt(
        from_id: str,
        to_id: str,
        agent_id: str,
        prompt: str,
        wait_for_start: bool = False
    ) -> Message:
        """创建发送提示词消息"""
        payload = ComposerSendPromptPayload(
            agent_id=agent_id,
            prompt=prompt,
            wait_for_start=wait_for_start
        )
        
        return Message(
            type=MessageType.COMPOSER_SEND_PROMPT,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    @staticmethod
    def composer_send_prompt_result(
        from_id: str,
        to_id: str,
        success: bool,
        agent_id: str,
        message: Optional[str] = None,
        error: Optional[str] = None
    ) -> Message:
        """创建提示词发送结果消息"""
        payload = ComposerSendPromptResultPayload(
            success=success,
            agent_id=agent_id,
            message=message,
            error=error
        )
        
        return Message(
            type=MessageType.COMPOSER_SEND_PROMPT_RESULT,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    @staticmethod
    def composer_query_status(
        from_id: str,
        to_id: str,
        agent_id: str
    ) -> Message:
        """创建查询状态消息"""
        payload = ComposerQueryStatusPayload(agent_id=agent_id)
        
        return Message(
            type=MessageType.COMPOSER_QUERY_STATUS,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    @staticmethod
    def composer_status_result(
        from_id: str,
        to_id: str,
        success: bool,
        agent_id: str,
        status: Optional[AgentStatus] = None,
        error: Optional[str] = None
    ) -> Message:
        """创建状态查询结果消息"""
        payload_dict = {
            "success": success,
            "agent_id": agent_id,
            "status": status.value if status else None,
            "error": error
        }
        
        return Message(
            type=MessageType.COMPOSER_STATUS_RESULT,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload=payload_dict
        )
    
    @staticmethod
    def agent_status_changed(
        from_id: str,
        agent_id: str,
        old_status: AgentStatus,
        new_status: AgentStatus,
        task_description: Optional[str] = None
    ) -> Message:
        """创建 Agent 状态变化事件"""
        payload_dict = {
            "agent_id": agent_id,
            "old_status": old_status.value,
            "new_status": new_status.value,
            "task_description": task_description
        }
        
        return Message(
            type=MessageType.AGENT_STATUS_CHANGED,
            from_=from_id,
            to="",  # 广播
            timestamp=int(time.time()),
            payload=payload_dict
        )
    
    @staticmethod
    def agent_completed(
        from_id: str,
        agent_id: str,
        result: TaskResult,
        files_modified: List[str] = None,
        summary: Optional[str] = None
    ) -> Message:
        """创建 Agent 完成事件"""
        payload = AgentCompletedPayload(
            agent_id=agent_id,
            result=result,
            files_modified=files_modified or [],
            summary=summary
        )
        
        payload_dict = asdict(payload)
        payload_dict['result'] = result.value
        
        return Message(
            type=MessageType.AGENT_COMPLETED,
            from_=from_id,
            to="",  # 广播
            timestamp=int(time.time()),
            payload=payload_dict
        )
    
    @staticmethod
    def agent_error(
        from_id: str,
        agent_id: str,
        error_type: str,
        error_message: str,
        can_retry: bool = False
    ) -> Message:
        """创建 Agent 错误事件"""
        payload = AgentErrorPayload(
            agent_id=agent_id,
            error_type=error_type,
            error_message=error_message,
            can_retry=can_retry
        )
        
        return Message(
            type=MessageType.AGENT_ERROR,
            from_=from_id,
            to="",  # 广播
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    @staticmethod
    def heartbeat(from_id: str) -> Message:
        """创建心跳消息"""
        return Message(
            type=MessageType.HEARTBEAT,
            from_=from_id,
            to="server",
            timestamp=int(time.time()),
            payload={}
        )
    
    @staticmethod
    def heartbeat_ack(to_id: str) -> Message:
        """创建心跳响应消息"""
        payload = HeartbeatAckPayload(server_time=int(time.time()))
        
        return Message(
            type=MessageType.HEARTBEAT_ACK,
            from_="server",
            to=to_id,
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    @staticmethod
    def disconnect(from_id: str, reason: DisconnectReason) -> Message:
        """创建断开连接消息"""
        payload = DisconnectPayload(reason=reason)
        
        payload_dict = asdict(payload)
        payload_dict['reason'] = reason.value
        
        return Message(
            type=MessageType.DISCONNECT,
            from_=from_id,
            to="server",
            timestamp=int(time.time()),
            payload=payload_dict
        )
    
    # ========================================================================
    # 高层次语义操作消息
    # ========================================================================
    
    @staticmethod
    def agent_execute_prompt(
        from_id: str,
        to_id: str,
        agent_id: str,
        prompt: str,
        wait_for_completion: bool = False,
        timeout: int = 300000,
        clear_first: bool = True
    ) -> Message:
        """创建 Agent 执行提示词消息（高层次语义操作）"""
        payload = AgentExecutePromptPayload(
            agent_id=agent_id,
            prompt=prompt,
            wait_for_completion=wait_for_completion,
            timeout=timeout,
            clear_first=clear_first
        )
        
        return Message(
            type=MessageType.AGENT_EXECUTE_PROMPT,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    @staticmethod
    def agent_execute_prompt_result(
        from_id: str,
        to_id: str,
        agent_id: str,
        success: bool,
        phase: str,
        message: Optional[str] = None,
        error: Optional[str] = None,
        input_completed: bool = False,
        submit_completed: bool = False,
        execution_time: Optional[int] = None,
        status: Optional[AgentStatus] = None
    ) -> Message:
        """创建 Agent 执行提示词结果消息"""
        payload = AgentExecutePromptResultPayload(
            success=success,
            agent_id=agent_id,
            phase=phase,
            message=message,
            error=error,
            input_completed=input_completed,
            submit_completed=submit_completed,
            execution_time=execution_time,
            status=status
        )
        
        payload_dict = asdict(payload)
        if status:
            payload_dict['status'] = status.value
        
        return Message(
            type=MessageType.AGENT_EXECUTE_PROMPT_RESULT,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload=payload_dict
        )
    
    @staticmethod
    def agent_stop_execution(
        from_id: str,
        to_id: str,
        agent_id: str,
        reason: Optional[str] = None
    ) -> Message:
        """创建停止 Agent 执行消息"""
        payload = AgentStopExecutionPayload(
            agent_id=agent_id,
            reason=reason
        )
        
        return Message(
            type=MessageType.AGENT_STOP_EXECUTION,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    @staticmethod
    def agent_stop_execution_result(
        from_id: str,
        to_id: str,
        agent_id: str,
        success: bool,
        message: Optional[str] = None,
        error: Optional[str] = None
    ) -> Message:
        """创建停止执行结果消息"""
        payload = AgentStopExecutionResultPayload(
            success=success,
            agent_id=agent_id,
            message=message,
            error=error
        )
        
        return Message(
            type=MessageType.AGENT_STOP_EXECUTION_RESULT,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    # ========================================================================
    # V10: Conversation ID 查询
    # ========================================================================
    
    @staticmethod
    def get_conversation_id(
        from_id: str,
        to_id: str
    ) -> Message:
        """创建查询 conversation_id 消息 (V10)"""
        return Message(
            type=MessageType.GET_CONVERSATION_ID,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload={}
        )
    
    @staticmethod
    def get_conversation_id_result(
        from_id: str,
        to_id: str,
        success: bool,
        conversation_id: Optional[str] = None,
        inject_id: Optional[str] = None,
        error: Optional[str] = None
    ) -> Message:
        """创建 conversation_id 查询结果消息 (V10)"""
        payload = GetConversationIdResultPayload(
            success=success,
            conversation_id=conversation_id,
            inject_id=inject_id,
            error=error
        )
        
        return Message(
            type=MessageType.GET_CONVERSATION_ID_RESULT,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    # ========================================================================
    # Cursor 输入操作
    # ========================================================================
    
    @staticmethod
    def cursor_input_text(
        from_id: str,
        to_id: str,
        text: str,
        conversation_id: Optional[str] = None,
        execute: bool = False
    ) -> Message:
        """创建向 Cursor 输入文本消息
        
        Args:
            execute: 是否立即执行（按 Enter 键）
        """
        payload = CursorInputTextPayload(
            text=text,
            conversation_id=conversation_id,
            execute=execute
        )
        
        return Message(
            type=MessageType.CURSOR_INPUT_TEXT,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    @staticmethod
    def cursor_input_text_result(
        from_id: str,
        to_id: str,
        success: bool,
        message: Optional[str] = None,
        error: Optional[str] = None
    ) -> Message:
        """创建 Cursor 输入文本结果消息"""
        payload = CursorInputTextResultPayload(
            success=success,
            message=message,
            error=error
        )
        
        return Message(
            type=MessageType.CURSOR_INPUT_TEXT_RESULT,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    # ========================================================================
    # 通用 JavaScript 执行
    # ========================================================================
    
    @staticmethod
    def execute_js(
        from_id: str,
        to_id: str,
        code: str,
        request_id: Optional[str] = None
    ) -> Message:
        """创建执行 JavaScript 消息"""
        payload = ExecuteJsPayload(
            code=code,
            request_id=request_id
        )
        
        return Message(
            type=MessageType.EXECUTE_JS,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload=asdict(payload)
        )
    
    @staticmethod
    def execute_js_result(
        from_id: str,
        to_id: str,
        success: bool,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Message:
        """创建 JavaScript 执行结果消息"""
        payload = ExecuteJsResultPayload(
            success=success,
            result=result,
            error=error,
            request_id=request_id
        )
        
        return Message(
            type=MessageType.EXECUTE_JS_RESULT,
            from_=from_id,
            to=to_id,
            timestamp=int(time.time()),
            payload=asdict(payload)
        )


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    """测试消息构建和序列化"""
    
    # 示例 1: 创建注册消息
    print("=" * 70)
    print("示例 1: Cursor Hook 注册")
    print("=" * 70)
    
    register_msg = MessageBuilder.register(
        from_id="cursor-abc123",
        client_type=ClientType.CURSOR_HOOK,
        platform=Platform.DARWIN,
        pid=12345,
        cursor_id="cursor-abc123",
        workspace="/Users/user/projects/myapp",
        ws_port=9876,
        capabilities=[Capability.COMPOSER, Capability.EDITOR]
    )
    
    print(register_msg.to_json())
    print()
    
    # 示例 2: 创建注册确认
    print("=" * 70)
    print("示例 2: 注册确认")
    print("=" * 70)
    
    register_ack_msg = MessageBuilder.register_ack(
        to_id="cursor-abc123",
        success=True,
        assigned_id="cursor-abc123",
        server_info={"version": "1.0.0"}
    )
    
    print(register_ack_msg.to_json())
    print()
    
    # 示例 3: 发送提示词
    print("=" * 70)
    print("示例 3: 发送提示词")
    print("=" * 70)
    
    prompt_msg = MessageBuilder.composer_send_prompt(
        from_id="cc-001",
        to_id="cursor-abc123",
        agent_id="default",
        prompt="写一个快速排序的 Python 实现"
    )
    
    print(prompt_msg.to_json())
    print()
    
    # 示例 4: Agent 状态变化事件
    print("=" * 70)
    print("示例 4: Agent 状态变化")
    print("=" * 70)
    
    status_change_msg = MessageBuilder.agent_status_changed(
        from_id="cursor-abc123",
        agent_id="default",
        old_status=AgentStatus.THINKING,
        new_status=AgentStatus.WORKING,
        task_description="生成快速排序代码中..."
    )
    
    print(status_change_msg.to_json())
    print()
    
    # 示例 5: Agent 完成事件
    print("=" * 70)
    print("示例 5: Agent 完成")
    print("=" * 70)
    
    completed_msg = MessageBuilder.agent_completed(
        from_id="cursor-abc123",
        agent_id="default",
        result=TaskResult.SUCCESS,
        files_modified=["main.py", "test_main.py"],
        summary="已生成快速排序实现及单元测试"
    )
    
    print(completed_msg.to_json())
    print()
    
    # 示例 6: 从 JSON 解析消息
    print("=" * 70)
    print("示例 6: 从 JSON 解析")
    print("=" * 70)
    
    json_str = register_msg.to_json()
    parsed_msg = Message.from_json(json_str)
    print(f"类型: {parsed_msg.type}")
    print(f"发送者: {parsed_msg.from_}")
    print(f"接收者: {parsed_msg.to}")
    print(f"时间戳: {parsed_msg.timestamp}")
    print(f"Payload: {parsed_msg.payload}")

