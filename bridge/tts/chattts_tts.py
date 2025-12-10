"""
ChatTTS 实现

基于 ChatTTS 的高质量中文语音合成，支持情感控制
"""

import sys
import os
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path

# 添加 ChatTTS 路径到 sys.path
CHATTTS_PATH = "/Users/user/Documents/tts/chattts"
if CHATTTS_PATH not in sys.path:
    sys.path.insert(0, CHATTTS_PATH)

from chattts_engine import ChatTTSEngine, EMOTION_EXAMPLES
from .base import TTSBase


class ChatTTS(TTSBase):
    """ChatTTS 实现 - 高质量中文语音合成"""
    
    # 情感到 ChatTTS 标签的映射
    EMOTION_MAPPING = {
        "neutral": "",  # 中性，不添加特殊标签
        "happy": "[laugh]",  # 开心 - 添加笑声
        "excited": "[laugh][speed_7]",  # 兴奋 - 笑声 + 快速
        "sad": "[uv_break][speed_3]",  # 悲伤 - 停顿 + 慢速
        "calm": "[speed_4]",  # 平静 - 慢速
        "angry": "[speed_6][oral_7]",  # 生气 - 快速 + 口语化
        "surprised": "[uv_break][speed_7]",  # 惊讶 - 停顿 + 快速
        "relaxed": "[speed_3]",  # 放松 - 慢速
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 ChatTTS
        
        Config 参数:
            model_path: 模型路径（默认使用本地路径）
            device: 设备类型 ("auto", "cpu", "mps", "cuda")
            temperature: 温度参数（默认 0.3）
            seed: 固定音色种子（默认 42）
            output_dir: 输出目录（默认 "tts_output"）
        """
        super().__init__(config)
        
        # 获取配置
        model_path = self.config.get("model_path", "auto")
        if model_path == "auto":
            model_path = os.path.join(CHATTTS_PATH, "models/ChatTTS")
        
        device = self.config.get("device", "auto")
        self.temperature = self.config.get("temperature", 0.3)
        self.default_seed = self.config.get("seed", 42)
        
        # 初始化引擎
        try:
            self.engine = ChatTTSEngine(device=device, model_path=model_path)
            print(f"✅ ChatTTS 初始化完成")
            print(f"   模型路径: {model_path}")
            print(f"   设备: {self.engine.device}")
            print(f"   温度: {self.temperature}")
            print(f"   默认音色种子: {self.default_seed}")
            
            # 预加载模型
            print("   正在加载模型...")
            load_time = self.engine.load()
            print(f"   ✅ 模型加载完成，耗时: {load_time:.2f} 秒")
            
            # 设置默认音色
            self.engine.set_random_speaker(self.default_seed)
            
        except Exception as e:
            print(f"❌ ChatTTS 初始化失败: {e}")
            raise
    
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
            **kwargs: 其他参数
                - seed: 音色种子
                - temperature: 温度参数
        
        Returns:
            生成的音频文件路径
        """
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        # 生成文件名
        if output_filename is None:
            filename = hashlib.md5(text.encode()).hexdigest()
            output_filename = f"{filename}.wav"
        
        # 确保文件名以 .wav 结尾
        if not output_filename.endswith('.wav'):
            output_filename += '.wav'
        
        output_path = str(self.output_dir / output_filename)
        
        # 获取参数
        # 🔧 不传入 seed，使用初始化时固定的 speaker（避免每次重新采样）
        # seed = kwargs.get("seed", self.default_seed)  
        temperature = kwargs.get("temperature", self.temperature)
        
        # 生成语音
        try:
            result = self.engine.generate_to_file(
                text=text,
                output_path=output_path,
                seed=None,  # ✅ 不传入 seed，保持音色一致
                temperature=temperature,
            )
            
            if result["success"]:
                print(f"   ✅ 生成音频: {Path(output_path).name}")
                print(f"      耗时: {result['synthesis_time']}s, 时长: {result['audio_duration']}s, RTF: {result['rtf']}")
                return output_path
            else:
                raise RuntimeError(f"语音合成失败: {result.get('error')}")
                
        except Exception as e:
            raise RuntimeError(f"ChatTTS 生成失败: {e}")
    
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
        # 🎀 根据情绪选择口语化级别（增强萝莉音效果）
        oral_levels = {
            "neutral": "[oral_4]",   # 中性 - 适度口语化
            "happy": "[oral_6]",     # 开心 - 较强口语化
            "excited": "[oral_7]",   # 兴奋 - 强口语化
            "sad": "[oral_3]",       # 悲伤 - 轻度口语化
            "calm": "[oral_4]",      # 平静 - 适度口语化
            "angry": "[oral_5]",     # 生气 - 适度口语化
            "surprised": "[oral_6]", # 惊讶 - 较强口语化
            "relaxed": "[oral_3]",   # 放松 - 轻度口语化
        }
        
        # 获取情感标签
        emotion_tag = self.EMOTION_MAPPING.get(emotion.lower(), "")
        
        # 获取口语化标签（社区推荐，增强萝莉音）
        oral_tag = oral_levels.get(emotion.lower(), "[oral_5]")
        
        # 组合标签：口语化 + 情感
        if emotion_tag:
            # 口语化标签在最前面，情感标签跟在后面
            enhanced_text = f"{oral_tag}{emotion_tag}{text}"
        else:
            enhanced_text = f"{oral_tag}{text}"
        
        print(f"   情绪: {emotion} -> 标签: {oral_tag}{emotion_tag}")
        
        return self.generate(enhanced_text, output_filename=output_filename, **kwargs)
    
    def get_available_voices(self) -> list:
        """
        获取可用的音色列表
        
        注意: ChatTTS 使用种子生成音色，理论上有无限多种音色
        这里返回一些预设的种子值
        """
        return [
            "seed_42 (默认)",
            "seed_123",
            "seed_456",
            "seed_789",
            "seed_2024",
            "random (随机音色)",
        ]
    
    def get_name(self) -> str:
        """获取 TTS 引擎名称"""
        return "ChatTTS"
    
    def set_speaker(self, seed: Optional[int] = None):
        """
        设置音色
        
        Args:
            seed: 音色种子，None 表示随机
        """
        actual_seed = self.engine.set_random_speaker(seed)
        print(f"   🎤 音色已切换，种子: {actual_seed}")
        return actual_seed
    
    def cleanup(self):
        """清理资源"""
        self.engine = None


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("🎤 ChatTTS 测试")
    print("=" * 60)
    
    # 创建实例
    config = {
        "temperature": 0.3,
        "seed": 42,
        "output_dir": "tts_output"
    }
    tts = ChatTTS(config)
    
    # 测试 1: 基础生成
    print("\n测试 1: 基础生成")
    file1 = tts.generate("你好，我是オルテンシア！")
    print(f"✅ 生成: {file1}")
    
    # 测试 2: 带情绪生成
    print("\n测试 2: 带情绪生成（开心）")
    file2 = tts.generate_with_emotion("太棒了！今天真是个好日子！", emotion="happy")
    print(f"✅ 生成: {file2}")
    
    # 测试 3: 不同情绪
    print("\n测试 3: 不同情绪")
    emotions = ["sad", "excited", "calm", "angry"]
    for emotion in emotions:
        text = f"这是{emotion}情绪的测试"
        file = tts.generate_with_emotion(text, emotion=emotion)
        print(f"✅ {emotion}: {file}")
    
    # 测试 4: 切换音色
    print("\n测试 4: 切换音色")
    tts.set_speaker(123)
    file3 = tts.generate("我换了一个音色")
    print(f"✅ 生成: {file3}")
    
    # 获取可用音色
    print("\n可用音色:")
    for voice in tts.get_available_voices():
        print(f"  - {voice}")
    
    print("\n" + "=" * 60)
    print(f"✅ 测试完成！TTS 引擎: {tts.get_name()}")
    print("=" * 60)


