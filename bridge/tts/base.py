"""
TTS 基础接口

定义 TTS 的抽象接口，所有 TTS 实现都需要继承这个基类
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path


class TTSBase(ABC):
    """TTS 抽象基类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 TTS
        
        Args:
            config: TTS 配置字典
        """
        self.config = config or {}
        self.output_dir = Path(self.config.get("output_dir", "tts_output"))
        self.output_dir.mkdir(exist_ok=True)
    
    @abstractmethod
    def generate(
        self, 
        text: str, 
        output_filename: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        生成语音文件
        
        Args:
            text: 要合成的文本
            output_filename: 输出文件名（可选）
            **kwargs: 其他参数（由具体实现定义）
            
        Returns:
            生成的音频文件路径
        """
        pass
    
    @abstractmethod
    def generate_with_emotion(
        self,
        text: str,
        emotion: str = "neutral",
        output_filename: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        根据情绪生成语音
        
        Args:
            text: 要合成的文本
            emotion: 情绪（neutral, happy, sad, angry, etc.）
            output_filename: 输出文件名
            **kwargs: 其他参数
            
        Returns:
            生成的音频文件路径
        """
        pass
    
    @abstractmethod
    def get_available_voices(self) -> list:
        """
        获取可用的音色列表
        
        Returns:
            音色列表
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        获取 TTS 引擎名称
        
        Returns:
            TTS 引擎名称
        """
        pass
    
    def cleanup(self):
        """
        清理资源（可选实现）
        """
        pass

