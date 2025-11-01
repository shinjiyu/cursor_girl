"""
TTS 管理器

负责加载配置和创建 TTS 实例
"""

import json
from pathlib import Path
from typing import Optional
from tts import TTSFactory, TTSBase


class TTSManager:
    """TTS 管理器"""
    
    def __init__(self, config_path: str = "tts_config.json"):
        """
        初始化 TTS 管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.tts: Optional[TTSBase] = None
        self.current_engine = None
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if not self.config_path.exists():
            print(f"⚠️  配置文件不存在: {self.config_path}")
            print("   使用默认配置")
            return {
                "engine": "macos",
                "macos": {
                    "voice": "meijia",
                    "rate": 220,
                    "output_dir": "tts_output"
                }
            }
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"✅ 加载配置文件: {self.config_path}")
                return config
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            print("   使用默认配置")
            return {
                "engine": "macos",
                "macos": {
                    "voice": "meijia",
                    "rate": 220,
                    "output_dir": "tts_output"
                }
            }
    
    def initialize(self, engine: Optional[str] = None) -> TTSBase:
        """
        初始化 TTS 实例
        
        Args:
            engine: TTS 引擎名称（如果为 None，则使用配置文件中的引擎）
            
        Returns:
            TTS 实例
        """
        # 确定使用的引擎
        engine = engine or self.config.get("engine", "macos")
        
        # 获取引擎配置
        engine_config = self.config.get(engine, {})
        
        # 创建 TTS 实例
        try:
            self.tts = TTSFactory.create(engine, engine_config)
            self.current_engine = engine
            print(f"✅ TTS 引擎初始化成功: {self.tts.get_name()}")
            return self.tts
        except Exception as e:
            print(f"❌ TTS 引擎初始化失败: {e}")
            raise
    
    def switch_engine(self, engine: str) -> TTSBase:
        """
        切换 TTS 引擎
        
        Args:
            engine: 新的 TTS 引擎名称
            
        Returns:
            新的 TTS 实例
        """
        print(f"\n🔄 切换 TTS 引擎: {self.current_engine} -> {engine}")
        
        # 清理旧实例
        if self.tts:
            self.tts.cleanup()
        
        # 初始化新实例
        return self.initialize(engine)
    
    def generate(self, text: str, **kwargs) -> str:
        """
        生成语音（使用当前引擎）
        
        Args:
            text: 要合成的文本
            **kwargs: 其他参数
            
        Returns:
            音频文件路径
        """
        if not self.tts:
            raise RuntimeError("TTS 未初始化，请先调用 initialize()")
        
        return self.tts.generate(text, **kwargs)
    
    def generate_with_emotion(self, text: str, emotion: str = "neutral", **kwargs) -> str:
        """
        根据情绪生成语音
        
        Args:
            text: 要合成的文本
            emotion: 情绪
            **kwargs: 其他参数
            
        Returns:
            音频文件路径
        """
        if not self.tts:
            raise RuntimeError("TTS 未初始化，请先调用 initialize()")
        
        return self.tts.generate_with_emotion(text, emotion, **kwargs)
    
    def get_info(self) -> dict:
        """获取当前 TTS 信息"""
        if not self.tts:
            return {
                "engine": None,
                "name": "未初始化",
                "available_voices": []
            }
        
        return {
            "engine": self.current_engine,
            "name": self.tts.get_name(),
            "available_voices": self.tts.get_available_voices()
        }


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("🎤 TTS 管理器测试")
    print("=" * 60)
    
    # 创建管理器
    manager = TTSManager()
    
    # 初始化（使用配置文件中的引擎）
    print("\n测试 1: 初始化 TTS")
    manager.initialize()
    
    # 生成语音
    print("\n测试 2: 生成语音")
    file1 = manager.generate("你好，我是オルテンシア！")
    print(f"✅ 生成: {file1}")
    
    # 带情绪生成
    print("\n测试 3: 带情绪生成")
    file2 = manager.generate_with_emotion("太棒了！", emotion="happy")
    print(f"✅ 生成: {file2}")
    
    # 获取信息
    print("\n测试 4: 获取 TTS 信息")
    info = manager.get_info()
    print(f"   引擎: {info['engine']}")
    print(f"   名称: {info['name']}")
    print(f"   可用音色: {', '.join(info['available_voices'])}")
    
    # 测试切换引擎（会失败，因为其他引擎未实现）
    print("\n测试 5: 尝试切换引擎（预期失败）")
    try:
        manager.switch_engine("chattts")
    except NotImplementedError as e:
        print(f"   ⚠️  预期错误: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)

