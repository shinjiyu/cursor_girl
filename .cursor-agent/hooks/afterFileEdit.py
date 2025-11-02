#!/usr/bin/env python3
"""
afterFileEdit Hook
在 Agent 编辑文件后触发，可以用于格式化或审计
"""

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from agent_hook_handler import AuditHook


class AfterFileEditHook(AuditHook):
    """文件编辑后的处理"""
    
    def __init__(self):
        super().__init__("afterFileEdit")
    
    # 支持格式化的文件类型
    FORMATTERS = {
        '.py': ['black', '--quiet'],
        '.js': ['prettier', '--write'],
        '.ts': ['prettier', '--write'],
        '.tsx': ['prettier', '--write'],
        '.jsx': ['prettier', '--write'],
        '.json': ['prettier', '--write'],
        '.css': ['prettier', '--write'],
        '.md': ['prettier', '--write'],
    }
    
    def audit(self) -> None:
        """审计并格式化文件"""
        file_path = self.input_data.get("file_path", "")
        edits = self.input_data.get("edits", [])
        
        if not file_path:
            return
        
        # 获取文件扩展名
        ext = Path(file_path).suffix
        
        # 通知オルテンシア
        self.send_to_ortensia(
            f"Agent 编辑了文件：{Path(file_path).name}",
            emotion="neutral"
        )
        
        # 尝试格式化
        if ext in self.FORMATTERS and Path(file_path).exists():
            try:
                formatter = self.FORMATTERS[ext]
                cmd = formatter + [file_path]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    self.send_to_ortensia(
                        f"文件已自动格式化：{Path(file_path).name}",
                        emotion="happy"
                    )
                
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # 格式化工具不存在或超时，忽略
                pass
            except Exception as e:
                self.logger.warning(f"格式化失败: {e}")


if __name__ == "__main__":
    hook = AfterFileEditHook()
    sys.exit(hook.run())

