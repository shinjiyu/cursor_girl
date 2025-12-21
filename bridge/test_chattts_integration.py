#!/usr/bin/env python3
"""
测试 ChatTTS 集成

验证 ChatTTS 是否正确集成到 TTS 管理器中
"""

import sys
from pathlib import Path

# 添加 bridge 目录到 sys.path
BRIDGE_DIR = Path(__file__).parent
sys.path.insert(0, str(BRIDGE_DIR))

from tts_manager import TTSManager


def test_chattts_integration():
    """测试 ChatTTS 集成"""
    print("=" * 60)
    print("🎤 ChatTTS 集成测试")
    print("=" * 60)
    
    # 创建 TTS 管理器
    print("\n1. 创建 TTS 管理器...")
    manager = TTSManager(config_path="tts_config.json")
    
    # 初始化 ChatTTS 引擎
    print("\n2. 初始化 ChatTTS 引擎...")
    try:
        tts = manager.initialize("chattts")
        print(f"✅ 引擎初始化成功: {tts.get_name()}")
    except Exception as e:
        print(f"❌ 引擎初始化失败: {e}")
        return False
    
    # 获取引擎信息
    print("\n3. 获取引擎信息...")
    info = manager.get_info()
    print(f"   引擎: {info['engine']}")
    print(f"   名称: {info['name']}")
    print(f"   可用音色: {', '.join(info['available_voices'][:3])}...")
    
    # 测试基础生成
    print("\n4. 测试基础生成...")
    try:
        file1 = manager.generate("你好，我是オルテンシア！这是一个 ChatTTS 测试。")
        print(f"✅ 生成成功: {file1}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return False
    
    # 测试情绪生成
    print("\n5. 测试情绪生成...")
    emotions_to_test = ["happy", "sad", "excited"]
    
    for emotion in emotions_to_test:
        try:
            text = f"这是{emotion}情绪的测试"
            file = manager.generate_with_emotion(text, emotion=emotion)
            print(f"✅ {emotion}: {Path(file).name}")
        except Exception as e:
            print(f"❌ {emotion} 失败: {e}")
            return False
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    
    return True


def test_compare_engines():
    """比较 macOS TTS 和 ChatTTS"""
    print("\n" + "=" * 60)
    print("🔄 对比测试: macOS TTS vs ChatTTS")
    print("=" * 60)
    
    manager = TTSManager(config_path="tts_config.json")
    test_text = "这是一个对比测试。"
    
    # 测试 macOS TTS
    print("\n测试 macOS TTS...")
    try:
        manager.initialize("macos")
        file1 = manager.generate(test_text)
        print(f"✅ macOS TTS: {Path(file1).name}")
    except Exception as e:
        print(f"❌ macOS TTS 失败: {e}")
    
    # 测试 ChatTTS
    print("\n测试 ChatTTS...")
    try:
        manager.switch_engine("chattts")
        file2 = manager.generate(test_text)
        print(f"✅ ChatTTS: {Path(file2).name}")
    except Exception as e:
        print(f"❌ ChatTTS 失败: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # 主测试
    success = test_chattts_integration()
    
    if success:
        # 如果主测试通过，运行对比测试
        test_compare_engines()
    else:
        print("\n❌ 集成测试失败，跳过对比测试")
        sys.exit(1)




















