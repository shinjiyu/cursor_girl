"""
占位符 TTS 实现

为未来的 TTS 引擎预留接口：
- ChatTTS
- PaddleSpeech
- Edge TTS
- Azure TTS
- 讯飞 TTS
等等
"""

from typing import Optional, Dict, Any
from .base import TTSBase


class ChatTTS(TTSBase):
    """ChatTTS 实现（待实现）"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        print("⚠️  ChatTTS 尚未实现，请等待 Python 3.10/3.11 环境")
    
    def generate(self, text: str, output_filename: Optional[str] = None, **kwargs) -> str:
        raise NotImplementedError("ChatTTS 尚未实现")
    
    def generate_with_emotion(self, text: str, emotion: str = "neutral", output_filename: Optional[str] = None, **kwargs) -> str:
        raise NotImplementedError("ChatTTS 尚未实现")
    
    def get_available_voices(self) -> list:
        return []
    
    def get_name(self) -> str:
        return "ChatTTS (未实现)"


class PaddleSpeechTTS(TTSBase):
    """PaddleSpeech TTS 实现（待实现）"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        print("⚠️  PaddleSpeech TTS 尚未实现，需要兼容的 Python 环境")
    
    def generate(self, text: str, output_filename: Optional[str] = None, **kwargs) -> str:
        raise NotImplementedError("PaddleSpeech TTS 尚未实现")
    
    def generate_with_emotion(self, text: str, emotion: str = "neutral", output_filename: Optional[str] = None, **kwargs) -> str:
        raise NotImplementedError("PaddleSpeech TTS 尚未实现")
    
    def get_available_voices(self) -> list:
        return []
    
    def get_name(self) -> str:
        return "PaddleSpeech (未实现)"


class EdgeTTS(TTSBase):
    """Edge TTS 实现（待实现）"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        print("⚠️  Edge TTS 尚未实现，需要稳定的网络连接")
    
    def generate(self, text: str, output_filename: Optional[str] = None, **kwargs) -> str:
        raise NotImplementedError("Edge TTS 尚未实现")
    
    def generate_with_emotion(self, text: str, emotion: str = "neutral", output_filename: Optional[str] = None, **kwargs) -> str:
        raise NotImplementedError("Edge TTS 尚未实现")
    
    def get_available_voices(self) -> list:
        return []
    
    def get_name(self) -> str:
        return "Edge TTS (未实现)"


class AzureTTS(TTSBase):
    """Azure TTS 实现（待实现）"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        print("⚠️  Azure TTS 尚未实现，需要 API 密钥")
    
    def generate(self, text: str, output_filename: Optional[str] = None, **kwargs) -> str:
        raise NotImplementedError("Azure TTS 尚未实现")
    
    def generate_with_emotion(self, text: str, emotion: str = "neutral", output_filename: Optional[str] = None, **kwargs) -> str:
        raise NotImplementedError("Azure TTS 尚未实现")
    
    def get_available_voices(self) -> list:
        return []
    
    def get_name(self) -> str:
        return "Azure TTS (未实现)"

