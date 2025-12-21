#!/usr/bin/env python3
"""
寻找最萌的萝莉音色
测试不同的 seed 值，找出最适合的二次元日系萝莉音
"""

import sys
sys.path.insert(0, '/Users/user/Documents/tts/chattts')

from chattts_engine import ChatTTSEngine
from pathlib import Path


def test_voice_seeds():
    """测试不同的音色种子"""
    
    print("=" * 60)
    print("🎀 寻找最萌的二次元萝莉音色")
    print("=" * 60)
    print()
    
    # 初始化引擎
    engine = ChatTTSEngine(
        device="auto",
        model_path="/Users/user/Documents/tts/chattts/models/ChatTTS"
    )
    
    print("⏳ 正在加载模型...")
    engine.load()
    print("✅ 模型加载完成")
    print()
    
    # 测试文本 - 典型的萝莉台词
    test_texts = [
        "欧尼酱，我回来啦！今天也要加油哦！",
        "嘿嘿，发现了好玩的东西呢！",
        "嗯嗯，我知道了！交给我吧！",
    ]
    
    # 推荐的萝莉音 seed 范围
    # 根据经验，某些范围的 seed 更容易产生高音甜美的声音
    candidate_seeds = [
        42,      # 默认
        1234,    # 甜美系
        2468,    # 活泼系  
        3456,    # 软萌系
        5678,    # 清纯系
        7890,    # 元气系
        9999,    # 可爱系
        11111,   # 温柔系
        88888,   # 特别系
        100000,  # 高音系
    ]
    
    output_dir = Path("tts_output/voice_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🎤 开始测试 {len(candidate_seeds)} 个音色种子...")
    print(f"   测试文本: \"{test_texts[0]}\"")
    print()
    
    results = []
    
    for i, seed in enumerate(candidate_seeds, 1):
        print(f"[{i}/{len(candidate_seeds)}] 测试 seed={seed}")
        
        # 使用第一个测试文本
        text = test_texts[0]
        output_path = str(output_dir / f"voice_seed_{seed}.wav")
        
        try:
            result = engine.generate_to_file(
                text=text,
                output_path=output_path,
                seed=seed,
                temperature=0.3,  # 保持稳定
            )
            
            if result["success"]:
                print(f"   ✅ 生成成功: {result['audio_duration']:.2f}s")
                results.append({
                    'seed': seed,
                    'file': output_path,
                    'duration': result['audio_duration']
                })
            else:
                print(f"   ❌ 生成失败")
                
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        
        print()
    
    print("=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print()
    print("📁 生成的音频文件:")
    print(f"   {output_dir}/")
    print()
    print("🎧 试听方法:")
    print("   逐个播放所有音色:")
    for r in results:
        print(f"   afplay {r['file']}")
    print()
    print("💡 选择你最喜欢的音色，记下对应的 seed 值！")
    print()
    
    # 推荐说明
    print("🎀 音色特点参考:")
    print("   seed=1234  : 甜美可爱型")
    print("   seed=2468  : 活泼元气型")
    print("   seed=3456  : 软萌治愈型")
    print("   seed=5678  : 清纯自然型")
    print("   seed=7890  : 元气少女型")
    print()
    print("💫 找到喜欢的 seed 后，运行:")
    print("   python set_voice_seed.py <seed>")
    print()


if __name__ == "__main__":
    test_voice_seeds()






















