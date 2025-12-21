#!/usr/bin/env python3
"""
测试 TTS 音色是否稳定一致
生成同一段文本 3 次，检查音频是否相同
"""

import sys
import os
sys.path.insert(0, '/Users/user/Documents/tts/chattts')

from chattts_engine import ChatTTSEngine
import time

def test_voice_consistency():
    """测试音色一致性"""
    
    print("=" * 70)
    print("🎤 测试 ChatTTS 音色一致性")
    print("=" * 70)
    print()
    
    # 初始化引擎
    print("🔧 初始化 ChatTTS...")
    engine = ChatTTSEngine(
        device="auto",
        model_path="/Users/user/Documents/tts/chattts/models/ChatTTS"
    )
    
    print("📦 加载模型...")
    load_time = engine.load()
    print(f"✅ 模型加载完成，耗时: {load_time:.2f} 秒")
    print()
    
    # 设置固定音色
    print("🎨 设置固定音色 (seed=1234)...")
    engine.set_random_speaker(1234)
    print("✅ 音色已固定")
    print()
    
    # 测试文本
    test_text = "你好，我是Ortensia。"
    
    print(f"📝 测试文本: {test_text}")
    print()
    
    # 生成 3 次
    results = []
    for i in range(3):
        print(f"🔄 第 {i+1} 次生成...")
        
        # ✅ 关键：不传入 seed 参数！
        result = engine.generate_to_file(
            text=test_text,
            output_path=f"test_consistency_{i+1}.wav",
            seed=None,  # ✅ 不传入 seed，使用已固定的 speaker
            temperature=0.3,
        )
        
        if result["success"]:
            print(f"   ✅ 生成成功")
            print(f"      文件: {result['output_path']}")
            print(f"      时长: {result['audio_duration']:.2f}s")
            print(f"      耗时: {result['synthesis_time']:.2f}s")
            results.append(result)
        else:
            print(f"   ❌ 生成失败: {result.get('error')}")
        
        print()
        time.sleep(0.5)
    
    print("=" * 70)
    print("📊 结果分析")
    print("=" * 70)
    print()
    
    if len(results) == 3:
        # 比较音频时长（音色一致的话时长应该非常接近）
        durations = [r["audio_duration"] for r in results]
        avg_duration = sum(durations) / len(durations)
        max_diff = max(abs(d - avg_duration) for d in durations)
        
        print(f"音频时长对比:")
        for i, dur in enumerate(durations, 1):
            print(f"  第 {i} 次: {dur:.3f}s")
        
        print()
        print(f"平均时长: {avg_duration:.3f}s")
        print(f"最大偏差: {max_diff:.3f}s")
        print()
        
        if max_diff < 0.05:  # 50ms 以内认为一致
            print("✅ 音色稳定一致！")
        else:
            print("⚠️  音色可能不一致（时长差异较大）")
    
    print()
    print("=" * 70)
    print("💡 提示:")
    print("   - 如果音色一致，3 个音频文件应该听起来完全一样")
    print("   - 播放测试: afplay test_consistency_1.wav")
    print("=" * 70)

if __name__ == "__main__":
    test_voice_consistency()





















