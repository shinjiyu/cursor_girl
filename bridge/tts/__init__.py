"""
TTS 模块

统一的 TTS 接口，支持多种 TTS 引擎
"""

from typing import Optional, Dict, Any
from .base import TTSBase
from .macos_tts import MacOSTTS
from .placeholder_tts import ChatTTS, PaddleSpeechTTS, EdgeTTS, AzureTTS


# TTS 引擎映射
TTS_ENGINES = {
    "macos": MacOSTTS,
    "chattts": ChatTTS,
    "paddlespeech": PaddleSpeechTTS,
    "edge": EdgeTTS,
    "azure": AzureTTS,
}


class TTSFactory:
    """TTS 工厂类"""
    
    @staticmethod
    def create(
        engine: str = "macos",
        config: Optional[Dict[str, Any]] = None
    ) -> TTSBase:
        """
        创建 TTS 实例
        
        Args:
            engine: TTS 引擎名称（macos, chattts, paddlespeech, edge, azure）
            config: TTS 配置
            
        Returns:
            TTS 实例
            
        Raises:
            ValueError: 如果引擎名称无效
        """
        engine = engine.lower()
        
        if engine not in TTS_ENGINES:
            available = ", ".join(TTS_ENGINES.keys())
            raise ValueError(
                f"未知的 TTS 引擎: {engine}。可用引擎: {available}"
            )
        
        tts_class = TTS_ENGINES[engine]
        return tts_class(config)
    
    @staticmethod
    def get_available_engines() -> list:
        """获取所有可用的 TTS 引擎"""
        return list(TTS_ENGINES.keys())


# 导出
__all__ = [
    "TTSBase",
    "TTSFactory",
    "MacOSTTS",
    "ChatTTS",
    "PaddleSpeechTTS",
    "EdgeTTS",
    "AzureTTS",
]

