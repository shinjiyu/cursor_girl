#!/usr/bin/env python3
"""
afterMCPExecution Hook  
在 Agent 执行 MCP 工具后触发
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from agent_hook_handler import AuditHook


class AfterMCPExecutionHook(AuditHook):
    """MCP 工具执行后的审计"""
    
    def __init__(self):
        super().__init__("afterMCPExecution")
    
    def audit(self) -> None:
        """审计 MCP 工具执行"""
        tool_name = self.input_data.get("tool_name", "")
        result_json = self.input_data.get("result_json", "")
        
        if not tool_name:
            return
        
        # 检查结果中的错误
        has_error = '"error"' in result_json or '"success": false' in result_json
        
        if has_error:
            self.send_to_ortensia(
                f"工具失败：{tool_name}",
                emotion="sad"
            )
        else:
            # 成功 - 所有工具都通知
            self.send_to_ortensia(
                f"工具完成：{tool_name}",
                emotion="happy"
            )


if __name__ == "__main__":
    hook = AfterMCPExecutionHook()
    sys.exit(hook.run())

