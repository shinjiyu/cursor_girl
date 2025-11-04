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
    
    # Composer 操作
    COMPOSER_SEND_PROMPT = "composer_send_prompt"
    COMPOSER_SEND_PROMPT_RESULT = "composer_send_prompt_result"
    COMPOSER_QUERY_STATUS = "composer_query_status"
    COMPOSER_STATUS_RESULT = "composer_status_result"
    
    # 事件通知
    AGENT_STATUS_CHANGED = "agent_status_changed"
    AGENT_COMPLETED = "agent_completed"
    AGENT_ERROR = "agent_error"


# ============================================================================
# Payload 数据类定义
# ============================================================================

@dataclass
class RegisterPayload:
    """注册消息的 Payload"""
    client_type: ClientType
    platform: Platform
    pid: int
    
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
        client_type: ClientType,
        platform: Platform,
        pid: int,
        **kwargs
    ) -> Message:
        """创建注册消息"""
        payload = RegisterPayload(
            client_type=client_type,
            platform=platform,
            pid=pid,
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

