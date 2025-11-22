"""
最小化示例：展示 Sakura 的核心功能（无需配置文件）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from matou_sakura import (
    ConceptGraph,
    RuntimeState,
    ConceptDefinition,
    ConceptType,
)


def main():
    print("=" * 60)
    print("Sakura 最小化示例")
    print("=" * 60)
    
    # 1. 创建概念图谱
    print("\n[1] 创建概念图谱...")
    graph = ConceptGraph()
    
    # 2. 注册概念定义
    print("\n[2] 注册概念定义...")
    
    # 注册情绪概念
    happiness_concept = ConceptDefinition(
        name="emotion_happiness",
        type=ConceptType.FLOAT,
        description="幸福感",
        properties={"baseline": 0.5},
        constraints={"range": {"min": 0.0, "max": 1.0}},
        metadata={"category": "internal"}
    )
    graph.register_concept(happiness_concept)
    print(f"  ✓ 注册概念: emotion_happiness")
    
    stress_concept = ConceptDefinition(
        name="emotion_stress",
        type=ConceptType.FLOAT,
        description="压力",
        properties={"baseline": 0.3},
        constraints={"range": {"min": 0.0, "max": 1.0}},
        metadata={"category": "internal"}
    )
    graph.register_concept(stress_concept)
    print(f"  ✓ 注册概念: emotion_stress")
    
    # 3. 创建运行时状态
    print("\n[3] 创建运行时状态...")
    state = RuntimeState(graph)
    print(f"  ✓ RuntimeState 已创建")
    
    # 4. 设置概念值
    print("\n[4] 设置概念值...")
    state.set_concept_value("emotion_happiness", 0.8)
    print(f"  - emotion_happiness = 0.8")
    
    state.set_concept_value("emotion_stress", 0.3)
    print(f"  - emotion_stress = 0.3")
    
    # 5. 读取概念值
    print("\n[5] 读取概念值...")
    happiness = state.get_concept_value("emotion_happiness")
    stress = state.get_concept_value("emotion_stress")
    
    print(f"  - emotion_happiness = {happiness}")
    print(f"  - emotion_stress = {stress}")
    
    # 6. 修改概念值
    print("\n[6] 修改概念值...")
    state.set_concept_value("emotion_happiness", 0.9)
    new_happiness = state.get_concept_value("emotion_happiness")
    print(f"  - emotion_happiness 更新为: {new_happiness}")
    
    # 7. 总结
    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)
    print("\n核心 API:")
    print("  1. ConceptGraph() - 创建概念图谱")
    print("  2. graph.register_concept(concept_def) - 注册概念")
    print("  3. RuntimeState(graph) - 创建运行时状态")
    print("  4. state.set_concept_value(name, value) - 设置概念值")
    print("  5. state.get_concept_value(name) - 获取概念值")


if __name__ == "__main__":
    main()

