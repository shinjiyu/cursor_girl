#!/usr/bin/env python3
"""
Cursor Agent Hooks 处理器
用于处理 Cursor AI Agent 生命周期中的各种事件
"""

import sys
import json
import logging
import asyncio
import time
import hashlib
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# 设置日志
log_file = Path("/tmp/cursor-agent-hooks.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr)  # 错误输出到 stderr
    ]
)
logger = logging.getLogger(__name__)


class AgentHookHandler:
    """Agent Hook 处理器基类"""
    
    def __init__(self, hook_name: str):
        self.hook_name = hook_name
        self.input_data: Dict[str, Any] = {}
        self.logger = logger  # 让子类可以使用 self.logger
        
        # オルテンシア WebSocket 配置
        self.ws_server = "ws://localhost:8765"
        
        logger.info(f"🎣 [{hook_name}] Agent Hook 启动")
    
    def read_input(self) -> Dict[str, Any]:
        """从 stdin 读取 JSON 输入"""
        try:
            input_text = sys.stdin.read()
            
            # 详细日志记录
            logger.info("=" * 70)
            logger.info(f"📥 [{self.hook_name}] 接收到 Cursor 调用")
            logger.info("=" * 70)
            logger.debug(f"原始输入: {input_text[:500]}...")  # 截断长输入
            
            if not input_text.strip():
                logger.warning("⚠️  输入为空")
                return {}
            
            self.input_data = json.loads(input_text)
            
            # 格式化输出关键信息
            logger.info(f"📋 输入数据摘要:")
            for key, value in self.input_data.items():
                if isinstance(value, str) and len(value) > 100:
                    logger.info(f"   • {key}: {value[:100]}...")
                else:
                    logger.info(f"   • {key}: {value}")
            
            logger.info(f"✅ 输入数据解析成功")
            return self.input_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 解析失败: {e}")
            logger.error(f"   输入内容: {input_text}")
            return {}
        except Exception as e:
            logger.error(f"❌ 读取输入失败: {e}")
            return {}
    
    def write_output(self, output: Dict[str, Any]) -> None:
        """输出 JSON 到 stdout"""
        try:
            output_text = json.dumps(output, ensure_ascii=False)
            print(output_text, flush=True)
            
            # 详细日志
            logger.info("📤 输出响应给 Cursor:")
            for key, value in output.items():
                if isinstance(value, str) and len(value) > 100:
                    logger.info(f"   • {key}: {value[:100]}...")
                else:
                    logger.info(f"   • {key}: {value}")
            
        except Exception as e:
            logger.error(f"❌ 输出响应失败: {e}")
    
    def send_to_ortensia(
        self, 
        text: str, 
        emotion: str = "neutral",
        event_type: Optional[str] = None
    ) -> None:
        """发送消息到オルテンシア（使用 Ortensia 协议）"""
        try:
            import websockets
            
            # ============================================================
            # 获取对应的 inject ID（从环境变量）
            # ============================================================
            # inject 在启动时设置 ORTENSIA_INJECT_ID 环境变量
            # hook 从环境变量直接读取，无需通过 workspace 推测
            inject_id = os.getenv('ORTENSIA_INJECT_ID', '')
            
            if not inject_id:
                logger.warning("⚠️  未找到 ORTENSIA_INJECT_ID 环境变量")
                logger.warning("   inject 可能未正确设置环境变量")
                logger.warning("   将使用 workspace hash 作为备用方案")
            
            # ============================================================
            # 生成 hook 的客户端 ID
            # ============================================================
            workspace = self.input_data.get('workspace_roots', ['unknown'])[0] if self.input_data.get('workspace_roots') else 'unknown'
            conversation_id = self.input_data.get('conversation_id', 'default')
            
            # 计算哈希
            workspace_hash = hashlib.md5(workspace.encode()).hexdigest()[:4]
            conversation_hash = hashlib.md5(conversation_id.encode()).hexdigest()[:4]
            client_id = f"hook-{workspace_hash}-{conversation_hash}"
            
            # 提取 workspace 名称（用于日志）
            workspace_name = Path(workspace).name if workspace != 'unknown' else 'unknown'
            
            # 详细日志
            logger.info("💬 准备发送消息到オルテンシア:")
            logger.info(f"   • Workspace: {workspace_name}")
            logger.info(f"   • Hook ID: {client_id}")
            if inject_id:
                logger.info(f"   • Inject ID: {inject_id} ✅")
            else:
                logger.info(f"   • Inject ID: (未找到) ⚠️")
            logger.info(f"   • 文本: {text}")
            logger.info(f"   • 情绪: {emotion}")
            logger.info(f"   • 事件类型: {event_type or self.hook_name}")
            logger.info(f"   • WebSocket: {self.ws_server}")
            
            # 使用 asyncio.run 来运行异步代码，带超时机制
            async def send_message():
                # 添加 3 秒连接超时
                async with asyncio.timeout(3):
                    async with websockets.connect(
                        self.ws_server,
                        open_timeout=2,  # 连接超时 2 秒
                        close_timeout=1   # 关闭超时 1 秒
                    ) as websocket:
                        # 1. 发送注册消息（符合 Ortensia 协议格式）
                        register_msg = {
                            "type": "register",
                            "from": client_id,
                            "to": None,
                            "timestamp": int(time.time() * 1000),  # 毫秒时间戳（顶层必须字段）
                            "payload": {
                                "client_type": "agent_hook"
                            }
                        }
                        await websocket.send(json.dumps(register_msg))
                        logger.debug(f"已发送注册消息: {json.dumps(register_msg)}")
                        
                        # 接收注册确认（1秒超时）
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        logger.debug(f"注册响应: {response}")
                        
                        # 2. 发送 AITuber 消息（使用 AITUBER_RECEIVE_TEXT 类型，符合 Ortensia 协议）
                        message_data = {
                            "type": "aituber_receive_text",
                            "from": client_id,
                            "to": "aituber",  # 发送给 AITuber 客户端
                            "timestamp": int(time.time() * 1000),  # 毫秒时间戳（顶层必须字段）
                            "payload": {
                                "text": text,
                                "emotion": emotion,
                                "source": "hook",
                                "hook_name": self.hook_name,
                                "event_type": event_type or self.hook_name,
                                # 添加 Cursor 会话信息
                                "workspace": workspace,
                                "workspace_name": workspace_name,
                                "conversation_id": conversation_id,
                                # ✅ 关键：直接包含 inject ID（从环境变量读取）
                                "inject_id": inject_id if inject_id else None
                            }
                        }
                        
                        # 添加输入数据的摘要（避免发送过多数据）
                        if self.input_data:
                            message_data["payload"]["event_summary"] = self._summarize_input()
                        
                        await websocket.send(json.dumps(message_data))
                        logger.info(f"✅ 消息已发送到オルテンシア")
            
            asyncio.run(send_message())
            
        except Exception as e:
            logger.error(f"❌ 发送到オルテンシア失败: {e}")
            logger.debug(f"详细错误信息: {e}", exc_info=True)
    
    def _summarize_input(self) -> Dict[str, Any]:
        """生成输入数据的摘要（避免发送过大数据）"""
        summary = {}
        
        # 只保留关键字段
        for key in ['conversation_id', 'generation_id', 'hook_event_name', 
                    'workspace_roots', 'command', 'file_path', 'tool_name',
                    'status', 'loop_count']:
            if key in self.input_data:
                value = self.input_data[key]
                # 截断长字符串
                if isinstance(value, str) and len(value) > 100:
                    summary[key] = value[:100] + "..."
                else:
                    summary[key] = value
        
        return summary
    
    def process(self) -> Dict[str, Any]:
        """
        处理 hook 逻辑（子类需要实现）
        
        Returns:
            输出数据（将被写入 stdout）
        """
        raise NotImplementedError("子类需要实现 process() 方法")
    
    def run(self) -> int:
        """
        运行 hook
        
        Returns:
            退出码（0 表示成功）
        """
        start_time = datetime.now()
        
        try:
            # 读取输入
            logger.info(f"⏳ 步骤 1/3: 读取输入数据...")
            self.read_input()
            
            # 处理
            logger.info(f"⏳ 步骤 2/3: 执行 Hook 逻辑...")
            output = self.process()
            
            # 输出响应
            logger.info(f"⏳ 步骤 3/3: 输出响应...")
            if output:
                self.write_output(output)
            else:
                logger.info("   ℹ️  无需返回响应（审计类 hook）")
            
            # 执行总结
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info("=" * 70)
            logger.info(f"✅ [{self.hook_name}] Hook 执行成功")
            logger.info(f"⏱️  执行耗时: {elapsed:.3f} 秒")
            logger.info("=" * 70)
            logger.info("")  # 空行分隔
            
            return 0
            
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.error("=" * 70)
            logger.error(f"❌ [{self.hook_name}] Hook 执行失败")
            logger.error(f"⏱️  执行耗时: {elapsed:.3f} 秒")
            logger.error(f"错误: {e}")
            logger.exception("详细错误信息:")
            logger.error("=" * 70)
            logger.error("")  # 空行分隔
            return 1


class PermissionHook(AgentHookHandler):
    """
    需要返回权限决策的 Hook 基类
    (beforeShellExecution, beforeMCPExecution, beforeReadFile)
    """
    
    def make_decision(self) -> tuple[str, Optional[str], Optional[str]]:
        """
        做出权限决策（子类需要实现）
        
        Returns:
            (permission, user_message, agent_message)
            - permission: "allow" | "deny" | "ask"
            - user_message: 显示给用户的消息
            - agent_message: 发送给 Agent 的消息
        """
        raise NotImplementedError("子类需要实现 make_decision() 方法")
    
    def process(self) -> Dict[str, Any]:
        """处理权限检查"""
        logger.info("🔐 执行权限检查...")
        
        permission, user_msg, agent_msg = self.make_decision()
        
        # 详细日志
        logger.info(f"🔐 权限决策结果:")
        logger.info(f"   • 决策: {permission}")
        if user_msg:
            logger.info(f"   • 用户消息: {user_msg}")
        if agent_msg:
            logger.info(f"   • Agent 消息: {agent_msg}")
        
        output = {"permission": permission}
        
        if user_msg:
            output["user_message"] = user_msg
        
        if agent_msg:
            output["agent_message"] = agent_msg
        
        return output


class AuditHook(AgentHookHandler):
    """
    审计类 Hook 基类
    (afterShellExecution, afterMCPExecution, afterFileEdit, afterAgentResponse)
    
    这些 hook 通常不需要返回数据，只需要记录和通知
    """
    
    def audit(self) -> None:
        """执行审计逻辑（子类需要实现）"""
        raise NotImplementedError("子类需要实现 audit() 方法")
    
    def process(self) -> Dict[str, Any]:
        """处理审计"""
        logger.info("📊 执行审计逻辑...")
        self.audit()
        logger.info("📊 审计完成")
        return {}  # 审计 hooks 通常不需要返回数据


class StopHook(AgentHookHandler):
    """
    Stop Hook（Agent 循环结束）
    可以返回 followup_message 以继续循环
    """
    
    def should_continue(self) -> Optional[str]:
        """
        决定是否继续循环（子类需要实现）
        
        Returns:
            followup_message: 如果返回非空字符串，Agent 会继续执行
        """
        raise NotImplementedError("子类需要实现 should_continue() 方法")
    
    def process(self) -> Dict[str, Any]:
        """处理 stop hook"""
        followup = self.should_continue()
        
        if followup:
            return {"followup_message": followup}
        
        return {}


def create_simple_hook(
    hook_name: str,
    permission: str = "allow",
    message: str = "",
    emotion: str = "neutral"
) -> int:
    """
    创建一个简单的 hook（用于快速测试）
    
    Args:
        hook_name: Hook 名称
        permission: 权限决策（对于权限类 hooks）
        message: 发送给オルテンシア的消息
        emotion: 情绪
    """
    
    class SimpleHook(AgentHookHandler):
        def process(self) -> Dict[str, Any]:
            # 发送到オルテンシア
            if message:
                self.send_to_ortensia(message, emotion)
            
            # 如果是权限类 hook，返回权限决策
            if hook_name in ['beforeShellExecution', 'beforeMCPExecution', 
                            'beforeReadFile', 'beforeSubmitPrompt']:
                return {"permission": permission}
            
            return {}
    
    hook = SimpleHook(hook_name)
    return hook.run()


if __name__ == "__main__":
    # 测试代码
    if len(sys.argv) > 1:
        hook_name = sys.argv[1]
        sys.exit(create_simple_hook(hook_name))
    else:
        logger.error("Usage: agent_hook_handler.py <hook_name>")
        sys.exit(1)
