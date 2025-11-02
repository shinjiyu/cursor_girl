#!/usr/bin/env python3
"""
beforeSubmitPrompt Hook
在用户提交 Prompt 前触发，可以审核或阻止提交
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from agent_hook_handler import AgentHookHandler


class BeforeSubmitPromptHook(AgentHookHandler):
    """Prompt 提交前的审核"""
    
    def __init__(self):
        super().__init__("beforeSubmitPrompt")
    
    # 敏感信息模式
    SENSITIVE_PATTERNS = [
        (r'\b[A-Za-z0-9]{20,}\b', 'API Key'),  # 可能的 API Key
        (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', 'IP 地址'),  # IP 地址
        (r'password\s*[:=]\s*[^\s]+', '密码'),  # 密码
        (r'token\s*[:=]\s*[^\s]+', 'Token'),  # Token
    ]
    
    def process(self) -> dict:
        """处理 Prompt 提交"""
        prompt = self.input_data.get("prompt", "")
        attachments = self.input_data.get("attachments", [])
        
        if not prompt:
            return {"continue": True}
        
        # 检查是否包含敏感信息
        for pattern, name in self.SENSITIVE_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                self.send_to_ortensia(
                    f"检测到 Prompt 中可能包含{name}，请注意安全！",
                    emotion="surprised"
                )
        
        # 通知オルテンシア
        # 获取 Prompt 的前几个词
        words = prompt.split()[:10]
        preview = ' '.join(words) + ('...' if len(words) >= 10 else '')
        
        self.send_to_ortensia(
            f"开始新的 Agent 任务：{preview}",
            emotion="happy"
        )
        
        return {"continue": True}


if __name__ == "__main__":
    hook = BeforeSubmitPromptHook()
    sys.exit(hook.run())

