"""
基础使用示例：演示 Sakura 的核心功能

展示内容:
1. 加载概念图谱
2. 创建运行时状态
3. 设置和读取概念值
4. 自动影响传播
"""

import sys
import os

# 添加父目录到 path (开发模式)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from matou_sakura import ConceptGraph, RuntimeState


def main():
    print("=" * 60)
    print("Sakura 基础使用示例")
    print("=" * 60)
    
    # 1. 加载概念图谱
    print("\n[1] 加载概念图谱...")
    config_path = os.path.join(
        os.path.dirname(__file__),
        "../matou_sakura/config/simplified_knowledge_graph.json"
    )
    
    graph = ConceptGraph.from_config(config_path)
    print(f"✓ 已加载 {len(graph.concepts)} 个概念定义")
    
    # 2. 创建运行时状态
    print("\n[2] 创建运行时状态...")
    state = RuntimeState(graph)
    print(f"✓ RuntimeState 已创建")
    
    # 3. 设置概念值
    print("\n[3] 设置概念值...")
    
    # 设置情绪
    state.set_concept_value("emotion_happiness", 0.8)
    print(f"  - emotion_happiness = 0.8")
    
    state.set_concept_value("emotion_stress", 0.3)
    print(f"  - emotion_stress = 0.3")
    
    # 设置工作记忆
    state.set_concept_value("working_memory_capacity", 0.9)
    print(f"  - working_memory_capacity = 0.9")
    
    # 4. 读取概念值
    print("\n[4] 读取概念值...")
    
    happiness = state.get_concept_value("emotion_happiness")
    print(f"  - emotion_happiness = {happiness}")
    
    stress = state.get_concept_value("emotion_stress")
    print(f"  - emotion_stress = {stress}")
    
    capacity = state.get_concept_value("working_memory_capacity")
    print(f"  - working_memory_capacity = {capacity}")
    
    # 5. 演示影响传播
    print("\n[5] 演示影响传播...")
    print("  设置 task_difficulty = 0.9（高难度任务）")
    
    # 记录之前的压力值
    stress_before = state.get_concept_value("emotion_stress")
    print(f"  - emotion_stress (之前) = {stress_before}")
    
    # 设置任务难度（会影响压力）
    state.set_concept_value("task_difficulty", 0.9)
    
    # 读取影响后的压力值
    stress_after = state.get_concept_value("emotion_stress")
    print(f"  - emotion_stress (之后) = {stress_after}")
    
    if stress_after != stress_before:
        print(f"  ✓ 影响传播成功！压力增加了 {stress_after - stress_before:.2f}")
    else:
        print(f"  注意: 如果概念图谱中定义了关系，压力应该会增加")
    
    # 6. 总结
    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)
    print("\n核心要点:")
    print("  1. ConceptGraph.from_config() - 加载概念定义")
    print("  2. RuntimeState(graph) - 创建运行时状态")
    print("  3. state.set_concept_value() - 设置概念值")
    print("  4. state.get_concept_value() - 读取概念值")
    print("  5. 影响会自动传播（如果定义了关系）")


if __name__ == "__main__":
    main()

