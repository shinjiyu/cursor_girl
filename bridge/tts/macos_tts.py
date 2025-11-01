"""
macOS 系统 TTS 实现
"""

import subprocess
import os
from typing import Optional, Dict, Any
from pathlib import Path
from .base import TTSBase


class MacOSTTS(TTSBase):
    """macOS 系统 TTS 实现"""
    
    # 推荐的年轻少女音色
    YOUNG_GIRL_VOICES = {
        "meijia": "Meijia",
        "sinji": "Sinji",
        "flo": "Flo (中文（中国大陆）)",
        "sandy": "Sandy (中文（中国大陆）)",
        "tingting": "Tingting",
        "shelley": "Shelley (中文（中国大陆）)",
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 macOS TTS
        
        Config 参数:
            voice: 音色名称（默认 "meijia"）
            rate: 语速（默认 220）
            output_dir: 输出目录（默认 "tts_output"）
        """
        super().__init__(config)
        
        self.voice = self.config.get("voice", "meijia")
        self.rate = self.config.get("rate", 220)
        
        # 获取实际的音色名称
        self.voice_name = self.YOUNG_GIRL_VOICES.get(
            self.voice.lower(), 
            self.YOUNG_GIRL_VOICES["meijia"]
        )
        
        print(f"✅ macOS TTS 初始化完成")
        print(f"   音色: {self.voice_name}")
        print(f"   语速: {self.rate}")
    
    def generate(
        self, 
        text: str, 
        output_filename: Optional[str] = None,
        **kwargs
    ) -> str:
        """生成语音文件（输出 WAV 格式，浏览器兼容）"""
        # 生成文件名
        if output_filename is None:
            import hashlib
            filename = hashlib.md5(text.encode()).hexdigest()
            output_filename = f"{filename}.wav"  # WAV 格式
        
        wav_path = self.output_dir / output_filename
        # 先生成 AIFF 临时文件
        aiff_path = self.output_dir / output_filename.replace('.wav', '.aiff')
        
        # 使用自定义参数或默认参数
        rate = kwargs.get("rate", self.rate)
        voice = kwargs.get("voice", self.voice_name)
        
        # 构建命令（macOS say 只支持输出 AIFF 格式）
        cmd = [
            "say", 
            "-v", voice, 
            "-r", str(rate), 
            "-o", str(aiff_path),  # 先输出为 AIFF
            text
        ]
        
        # 执行命令生成 AIFF
        try:
            # 步骤 1: 生成 AIFF 文件
            subprocess.run(cmd, check=True, capture_output=True)
            
            # 步骤 2: 使用 ffmpeg 转换为 WAV
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", str(aiff_path),  # 输入文件
                "-y",  # 覆盖已存在的文件
                "-ar", "44100",  # 采样率 44.1kHz
                "-ac", "2",  # 双声道
                str(wav_path)  # 输出文件
            ]
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            
            # 步骤 3: 删除临时 AIFF 文件
            if aiff_path.exists():
                aiff_path.unlink()
            
            print(f"   ✅ 生成 WAV 音频: {wav_path.name}")
            return str(wav_path)
        except subprocess.CalledProcessError as e:
            # 清理临时文件
            if aiff_path.exists():
                aiff_path.unlink()
            raise RuntimeError(f"TTS 生成或转换失败: {e.stderr.decode() if e.stderr else str(e)}")
        except Exception as e:
            # 如果出错，清理临时文件
            if aiff_path.exists():
                aiff_path.unlink()
            raise RuntimeError(f"音频处理失败: {e}")
    
    def generate_with_emotion(
        self,
        text: str,
        emotion: str = "neutral",
        output_filename: Optional[str] = None,
        **kwargs
    ) -> str:
        """根据情绪生成语音"""
        # 根据情绪调整参数
        emotion_params = {
            "neutral": {"rate": 220},
            "happy": {"rate": 240},
            "excited": {"rate": 250},
            "sad": {"rate": 180},
            "calm": {"rate": 200},
            "angry": {"rate": 230},
            "surprised": {"rate": 240},
            "relaxed": {"rate": 200},
        }
        
        params = emotion_params.get(emotion.lower(), emotion_params["neutral"])
        
        # 合并自定义参数
        merged_kwargs = {**params, **kwargs}
        
        return self.generate(text, output_filename=output_filename, **merged_kwargs)
    
    def get_available_voices(self) -> list:
        """获取可用的音色列表"""
        return list(self.YOUNG_GIRL_VOICES.keys())
    
    def get_name(self) -> str:
        """获取 TTS 引擎名称"""
        return "macOS System TTS"


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("🎤 macOS TTS 测试")
    print("=" * 60)
    
    # 使用默认配置
    tts = MacOSTTS()
    
    # 生成语音
    print("\n测试 1: 基础生成")
    file1 = tts.generate("你好，我是オルテンシア！")
    print(f"✅ 生成: {file1}")
    
    # 带情绪生成
    print("\n测试 2: 带情绪生成")
    file2 = tts.generate_with_emotion("太棒了！", emotion="happy")
    print(f"✅ 生成: {file2}")
    
    # 自定义音色
    print("\n测试 3: 自定义音色")
    tts2 = MacOSTTS(config={"voice": "sinji", "rate": 230})
    file3 = tts2.generate("我是善怡！")
    print(f"✅ 生成: {file3}")
    
    # 获取可用音色
    print("\n可用音色:")
    for voice in tts.get_available_voices():
        print(f"  - {voice}")
    
    print("\n" + "=" * 60)
    print(f"✅ 测试完成！TTS 引擎: {tts.get_name()}")
    print("=" * 60)

