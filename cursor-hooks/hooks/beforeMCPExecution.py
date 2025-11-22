#!/usr/bin/env python3
"""
beforeMCPExecution Hook
在 Agent 执行 MCP 工具前触发
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from agent_hook_handler import PermissionHook


class BeforeMCPExecutionHook(PermissionHook):
    """MCP 工具执行前的权限检查"""
    
    def __init__(self):
        super().__init__("beforeMCPExecution")
    
    # 需要审核的敏感 MCP 工具
    SENSITIVE_TOOLS = [
        'delete_file',
        'delete_directory',
        'execute_command',
        'write_file',
        'database_query',
    ]
    
    def make_decision(self) -> tuple[str, str, str]:
        """决定是否允许执行 MCP 工具"""
        tool_name = self.input_data.get("tool_name", "")
        tool_input = self.input_data.get("tool_input", "")
        
        if not tool_name:
            return ("allow", None, None)
        
        # 检查敏感工具
        if tool_name in self.SENSITIVE_TOOLS:
            self.send_to_ortensia(
                f"Agent 要使用工具：{tool_name}，需要确认",
                emotion="surprised"
            )
            
            return (
                "ask",
                f"⚠️  MCP 工具需要确认：{tool_name}",
                None
            )
        
        # 普通工具
        self.send_to_ortensia(
            f"Agent 正在使用工具：{tool_name}",
            emotion="neutral"
        )
        
        return ("allow", None, None)


if __name__ == "__main__":
    hook = BeforeMCPExecutionHook()
    sys.exit(hook.run())

