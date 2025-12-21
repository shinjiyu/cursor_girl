#!/usr/bin/env python3
"""
语音音色样本生成器
生成多个不同种子的语音样本，用于挑选最佳音色
"""

import os
import sys
import json
import time
from pathlib import Path

# 添加 ChatTTS 路径
CHATTTS_PATH = "/Users/user/Documents/tts/chattts"
if CHATTTS_PATH not in sys.path:
    sys.path.insert(0, CHATTTS_PATH)

from chattts_engine import ChatTTSEngine

# 测试文本
TEST_TEXT = "对我而言，大哥是世界上最好的哥哥。"

# 年轻甜美女声的推荐种子范围
# 根据社区经验，较小的种子值往往产生更年轻的声音
SWEET_VOICE_SEEDS = [
    # 第一组：经典甜美音色（社区推荐）
    42,      # 默认甜美
    1234,    # 当前使用
    2024,    # 年轻活泼
    
    # 第二组：年轻女声探索
    7,       # 清亮
    13,      # 甜美
    27,      # 可爱
    33,      # 年轻
    66,      # 活泼
    88,      # 软萌
    111,     # 清甜
    
    # 第三组：萝莉音探索
    222,     # 稚嫩
    333,     # 童声感
    444,     # 软糯
    555,     # 俏皮
    666,     # 娇俏
    777,     # 甜蜜
    
    # 第四组：随机探索
    1001,    # 尝试
    2333,    # 尝试
    9999,    # 尝试
]

def generate_samples():
    """生成语音样本"""
    print("=" * 60)
    print("🎤 语音音色样本生成器")
    print("=" * 60)
    print(f"测试文本: {TEST_TEXT}")
    print(f"样本数量: {len(SWEET_VOICE_SEEDS)}")
    print()
    
    # 输出目录
    output_dir = Path(__file__).parent / "voice_samples"
    output_dir.mkdir(exist_ok=True)
    
    # 清空旧样本
    for f in output_dir.glob("*.wav"):
        f.unlink()
    
    # 初始化引擎
    print("🔧 初始化 ChatTTS...")
    engine = ChatTTSEngine(device="auto", model_path=os.path.join(CHATTTS_PATH, "models/ChatTTS"))
    load_time = engine.load()
    print(f"✅ 模型加载完成，耗时: {load_time:.2f}s")
    print()
    
    # 生成样本
    samples = []
    for i, seed in enumerate(SWEET_VOICE_SEEDS, 1):
        print(f"[{i}/{len(SWEET_VOICE_SEEDS)}] 生成种子 {seed}...")
        
        # 设置音色
        engine.set_random_speaker(seed)
        
        # 添加口语化标签增强甜美感
        enhanced_text = f"[oral_5][laugh]{TEST_TEXT}"
        
        # 生成文件名
        filename = f"voice_seed_{seed:05d}.wav"
        output_path = str(output_dir / filename)
        
        # 生成语音
        start_time = time.time()
        result = engine.generate_to_file(
            text=enhanced_text,
            output_path=output_path,
            seed=None,  # 已经通过 set_random_speaker 设置
            temperature=0.3,
        )
        gen_time = time.time() - start_time
        
        if result["success"]:
            samples.append({
                "seed": seed,
                "filename": filename,
                "duration": result["audio_duration"],
                "gen_time": round(gen_time, 2),
            })
            print(f"   ✅ 完成 ({result['audio_duration']:.2f}s)")
        else:
            print(f"   ❌ 失败: {result.get('error')}")
    
    # 保存样本信息
    info_path = output_dir / "samples.json"
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump({
            "text": TEST_TEXT,
            "samples": samples,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 60)
    print(f"✅ 生成完成！共 {len(samples)} 个样本")
    print(f"📁 输出目录: {output_dir}")
    print(f"📋 样本信息: {info_path}")
    print("=" * 60)
    
    return samples

if __name__ == "__main__":
    generate_samples()


