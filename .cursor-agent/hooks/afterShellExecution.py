#!/usr/bin/env python3
"""
afterShellExecution Hook
在 Agent 执行 Shell 命令后触发，用于审计和收集指标
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from agent_hook_handler import AuditHook


class AfterShellExecutionHook(AuditHook):
    """Shell 命令执行后的审计"""
    
    def __init__(self):
        super().__init__("afterShellExecution")
    
    def audit(self) -> None:
        """审计命令执行"""
        command = self.input_data.get("command", "")
        output = self.input_data.get("output", "")
        exit_code = self.input_data.get("exit_code", 0)
        
        if not command:
            return
        
        # 生成简洁的命令预览
        cmd_preview = command[:30] + "..." if len(command) > 30 else command
        
        # 检查输出中的错误
        has_error = exit_code != 0 or any(
            keyword in output.lower() 
            for keyword in ['error', 'failed', 'exception', 'traceback']
        )
        
        if has_error:
            # 命令执行失败
            self.send_to_ortensia(
                f"命令失败：{cmd_preview}",
                emotion="sad"
            )
        else:
            # 命令执行成功（所有命令都通知）
            self.send_to_ortensia(
                f"命令完成：{cmd_preview}",
                emotion="happy"
            )


if __name__ == "__main__":
    hook = AfterShellExecutionHook()
    sys.exit(hook.run())

