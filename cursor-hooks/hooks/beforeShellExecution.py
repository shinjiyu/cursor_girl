#!/usr/bin/env python3
"""
beforeShellExecution Hook
在 Agent 执行 Shell 命令前触发，可以阻止危险命令
"""

import sys
import re
from pathlib import Path

# 添加 lib 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from agent_hook_handler import PermissionHook


class BeforeShellExecutionHook(PermissionHook):
    """Shell 命令执行前的权限检查"""
    
    # 危险命令模式列表
    DANGEROUS_PATTERNS = [
        r'rm\s+-rf\s+/',  # rm -rf /
        r'rm\s+-rf\s+\*',  # rm -rf *
        r':\(\)\{.*;\};',  # Fork bomb
        r'>\s*/dev/sd[a-z]',  # 直接写入磁盘
        r'dd\s+if=.*of=/dev/',  # dd 写入磁盘
        r'mkfs\.',  # 格式化文件系统
        r'chmod\s+-R\s+777\s+/',  # 递归修改根目录权限
        r'curl.*\|\s*sh',  # 管道执行远程脚本
        r'wget.*\|\s*sh',  # 管道执行远程脚本
    ]
    
    # 需要确认的命令模式
    RISKY_PATTERNS = [
        r'rm\s+-rf',  # rm -rf
        r'DROP\s+DATABASE',  # SQL: DROP DATABASE
        r'DROP\s+TABLE',  # SQL: DROP TABLE
        r'DELETE\s+FROM.*WHERE\s+1=1',  # SQL: 删除所有数据
        r'git\s+push\s+.*--force',  # Git force push
        r'npm\s+publish',  # npm 发布
        r'docker\s+rm\s+-f',  # 强制删除容器
    ]
    
    def __init__(self):
        super().__init__("beforeShellExecution")
        self.command = ""
        self.cwd = ""
    
    def make_decision(self) -> tuple[str, str, str]:
        """决定是否允许执行命令"""
        # 获取命令和工作目录
        self.command = self.input_data.get("command", "")
        self.cwd = self.input_data.get("cwd", "")
        
        self.logger.info(f"🔍 检查命令: {self.command}")
        self.logger.info(f"📁 工作目录: {self.cwd}")
        
        if not self.command:
            self.logger.warning("⚠️  命令为空，允许执行")
            return ("allow", None, None)
        
        # 检查危险命令
        self.logger.info("🔍 步骤 1/3: 检查危险命令模式...")
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, self.command, re.IGNORECASE):
                self.logger.warning(f"🚨 匹配到危险命令模式: {pattern}")
                self.logger.warning(f"🚫 拒绝执行命令: {self.command}")
                
                # 发送警告到オルテンシア
                self.send_to_ortensia(
                    f"检测到危险命令！已阻止：{self.command[:50]}...",
                    emotion="angry"
                )
                
                return (
                    "deny",
                    f"🚫 危险命令已被阻止：{self.command}",
                    f"命令 '{self.command}' 被安全策略阻止"
                )
        
        self.logger.info("✅ 未检测到危险命令")
        
        # 检查风险命令
        self.logger.info("🔍 步骤 2/3: 检查风险命令模式...")
        for pattern in self.RISKY_PATTERNS:
            if re.search(pattern, self.command, re.IGNORECASE):
                self.logger.warning(f"⚠️  匹配到风险命令模式: {pattern}")
                self.logger.warning(f"❓ 需要用户确认: {self.command}")
                
                # 发送警告到オルテンシア
                self.send_to_ortensia(
                    f"检测到风险命令，需要确认：{self.command[:50]}...",
                    emotion="surprised"
                )
                
                return (
                    "ask",
                    f"⚠️  风险命令需要确认：{self.command}",
                    None
                )
        
        self.logger.info("✅ 未检测到风险命令")
        
        # 普通命令 - 通知オルテンシア（所有命令都通知）
        self.logger.info("🔍 步骤 3/3: 发送命令通知...")
        
        # 生成简洁的消息
        cmd_preview = self.command[:40] + "..." if len(self.command) > 40 else self.command
        
        self.logger.info(f"💬 发送命令通知: {cmd_preview}")
        self.send_to_ortensia(
            f"执行命令：{cmd_preview}",
            emotion="neutral"
        )
        
        self.logger.info("✅ 允许执行命令")
        return ("allow", None, None)


if __name__ == "__main__":
    hook = BeforeShellExecutionHook()
    sys.exit(hook.run())

