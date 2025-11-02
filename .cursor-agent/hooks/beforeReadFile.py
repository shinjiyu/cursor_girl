#!/usr/bin/env python3
"""
beforeReadFile Hook
在 Agent 读取文件前触发，可以过滤敏感信息或控制访问
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from agent_hook_handler import PermissionHook


class BeforeReadFileHook(PermissionHook):
    """文件读取前的权限检查"""
    
    def __init__(self):
        super().__init__("beforeReadFile")
    
    # 敏感文件模式
    SENSITIVE_PATTERNS = [
        r'\.env',
        r'\.env\..*',
        r'id_rsa',
        r'\.pem$',
        r'\.key$',
        r'password',
        r'secret',
        r'token',
        r'credentials',
        r'\.ssh/',
        r'\.aws/',
        r'\.kube/config',
    ]
    
    def make_decision(self) -> tuple[str, str, str]:
        """决定是否允许读取文件"""
        file_path = self.input_data.get("file_path", "")
        
        if not file_path:
            return ("allow", None, None)
        
        # 检查是否是敏感文件
        file_name = Path(file_path).name
        file_path_lower = file_path.lower()
        
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, file_path_lower):
                # 敏感文件需要确认
                self.send_to_ortensia(
                    f"Agent 要读取敏感文件：{file_name}，需要确认",
                    emotion="surprised"
                )
                
                return (
                    "ask",
                    f"⚠️  Agent 要读取敏感文件：{file_name}\n是否允许？",
                    None
                )
        
        # 普通文件
        # 只对重要操作发送通知
        if any(keyword in file_path_lower for keyword in ['config', 'setting']):
            self.send_to_ortensia(
                f"Agent 正在读取配置：{file_name}",
                emotion="neutral"
            )
        
        return ("allow", None, None)


if __name__ == "__main__":
    hook = BeforeReadFileHook()
    sys.exit(hook.run())

