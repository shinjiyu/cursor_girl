#!/usr/bin/env python3
"""
stop Hook
在 Agent 循环结束时触发，可以自动提交后续消息以继续循环
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from agent_hook_handler import StopHook


class StopAgentHook(StopHook):
    """Agent 循环结束处理"""
    
    def __init__(self):
        super().__init__("stop")
    
    # 最大自动循环次数
    MAX_AUTO_LOOPS = 5
    
    def should_continue(self) -> str:
        """决定是否继续循环"""
        status = self.input_data.get("status", "")
        loop_count = self.input_data.get("loop_count", 0)
        
        # 通知オルテンシア Agent 状态
        if status == "completed":
            self.send_to_ortensia(
                "Agent 任务完成了！太棒了！🎉",
                emotion="excited"
            )
            # 🆕 发送 AGENT_COMPLETED 事件（用于触发自动任务检查）
            self.send_agent_completed_event()
        elif status == "aborted":
            self.send_to_ortensia(
                "Agent 任务被中止了",
                emotion="neutral"
            )
        elif status == "error":
            self.send_to_ortensia(
                "Agent 遇到错误了...别担心，我们可以再试试",
                emotion="sad"
            )
        
        # 目前不自动继续循环（可以根据需要启用）
        # 如果需要自动继续，可以返回一个后续消息
        
        # 示例：自动继续（已注释）
        # if status == "completed" and loop_count < self.MAX_AUTO_LOOPS:
        #     return "继续优化代码"
        
        return None  # 不继续
    
    def send_agent_completed_event(self) -> None:
        """发送 AGENT_COMPLETED 事件到中央服务器（独立连接，避免 TTS 阻塞）"""
        try:
            import websockets
            import asyncio
            import time
            import json
            
            conversation_id = self.input_data.get('conversation_id', 'unknown')
            client_id = f"hook-{conversation_id}"
            
            async def send_event():
                try:
                    # 🔧 使用更长的超时时间（5秒），因为服务器可能在处理 TTS
                    async with websockets.connect(
                        self.ws_server, 
                        open_timeout=5,  # 连接超时 5 秒
                        close_timeout=2   # 关闭超时 2 秒
                    ) as websocket:
                        # 1. 注册
                        register_msg = {
                            "type": "register",
                            "from": client_id,
                            "to": None,
                            "timestamp": int(time.time() * 1000),
                            "payload": {"client_type": "agent_hook"}
                        }
                        await websocket.send(json.dumps(register_msg))
                        
                        # 🔧 增加超时到 5 秒（服务器可能因 TTS 生成而阻塞）
                        await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        
                        # 2. 发送 AGENT_COMPLETED 事件
                        event_msg = {
                            "type": "agent_completed",
                            "from": client_id,
                            "to": "",  # 广播
                            "timestamp": int(time.time() * 1000),
                            "payload": {
                                "agent_id": "default",
                                "result": "success",
                                "conversation_id": conversation_id,  # 🆕 添加 conversation_id
                                "summary": "任务已完成"
                            }
                        }
                        await websocket.send(json.dumps(event_msg))
                        self.logger.info(f"✅ AGENT_COMPLETED 事件已发送 (conv: {conversation_id})")
                except asyncio.TimeoutError:
                    self.logger.error("❌ WebSocket 连接超时（服务器可能繁忙）")
                except Exception as e:
                    self.logger.error(f"❌ WebSocket 连接失败: {e}")
            
            asyncio.run(send_event())
        except Exception as e:
            self.logger.error(f"❌ 发送 AGENT_COMPLETED 事件失败: {e}")


if __name__ == "__main__":
    hook = StopAgentHook()
    sys.exit(hook.run())

