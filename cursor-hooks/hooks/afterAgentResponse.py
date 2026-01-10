#!/usr/bin/env python3
"""
afterAgentResponse Hook
在 Agent 完成响应后触发
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from agent_hook_handler import AuditHook


class AfterAgentResponseHook(AuditHook):
    """Agent 响应后的审计"""
    
    def __init__(self):
        super().__init__("afterAgentResponse")
    
    def audit(self) -> None:
        """审计 Agent 响应"""
        text = self.input_data.get("text", "")
        
        if not text:
            return

        # ✅ 设计调整：
        # afterAgentResponse 的原始输出全部转发给 AITuber，由 AITuber 端做停止/渲染判断。
        # 这样可以适配 Cursor 行为变化，避免服务端规则导致漏判或重复循环。
        self.send_to_ortensia(
            text,
            emotion="neutral",
            event_type="afterAgentResponse"
        )


if __name__ == "__main__":
    hook = AfterAgentResponseHook()
    sys.exit(hook.run())

