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


if __name__ == "__main__":
    hook = StopAgentHook()
    sys.exit(hook.run())

