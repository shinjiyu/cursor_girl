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
        
        # 分析响应内容
        text_lower = text.lower()
        
        # 检测响应类型
        if any(word in text_lower for word in ['完成', 'done', 'finished', 'success']):
            self.send_to_ortensia(
                "Agent 完成任务了！干得漂亮！",
                emotion="happy"
            )
        elif any(word in text_lower for word in ['错误', 'error', 'failed', '失败']):
            self.send_to_ortensia(
                "Agent 遇到问题了...我们一起解决吧",
                emotion="sad"
            )
        elif any(word in text_lower for word in ['开始', 'starting', '正在']):
            self.send_to_ortensia(
                "Agent 正在工作中...",
                emotion="neutral"
            )
        else:
            # 普通响应，只记录日志，不发送到オルテンシア
            pass


if __name__ == "__main__":
    hook = AfterAgentResponseHook()
    sys.exit(hook.run())

