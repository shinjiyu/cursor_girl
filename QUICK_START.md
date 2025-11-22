# Sakura 快速开始

> 🎉 **项目已清理完成！只保留核心认知库**

## 📦 核心结构

✅ **纯粹的核心认知库！**

```
matou_sakura/                   # 核心包
├── __init__.py                 # ✅ 公共 API
├── pyproject.toml              # ✅ 打包配置
├── persona/                    # ✅ 核心认知模块 (19 个文件)
├── config/                     # ✅ 配置文件
└── utils/                      # ✅ 工具模块

examples/                       # 使用示例
├── minimal_example.py          # ✅ 运行成功！
└── basic_usage.py

文档:
├── QUICK_START.md              # 本文档
├── SAKURA_PACKAGING_GUIDE.md   # 打包指南
├── SAKURA_REFACTOR_ROADMAP.md  # 重构路线图
└── CLEANUP_SUMMARY.md          # 清理总结
```

---

## 🚀 快速使用

### 1. 导入测试（无需安装）

```bash
cd "/Users/user/Documents/ cursorgirl"
PYTHONPATH="$PWD:$PYTHONPATH" python3 -c "from matou_sakura import ConceptGraph, RuntimeState; print('✅ 导入成功!')"
```

**输出**: `✅ 导入成功!`

### 2. 运行示例

```bash
cd "/Users/user/Documents/ cursorgirl"
PYTHONPATH="$PWD:$PYTHONPATH" python3 examples/minimal_example.py
```

### 3. 在第三方项目中使用

```python
# 方式 1: 添加到 PYTHONPATH（开发模式）
import sys
sys.path.insert(0, '/Users/user/Documents/ cursorgirl')

from matou_sakura import ConceptGraph, RuntimeState, ConceptDefinition, ConceptType

# 创建概念图谱
graph = ConceptGraph()

# 注册概念
concept = ConceptDefinition(
    name="test_concept",
    type=ConceptType.FLOAT,
    description="测试概念",
    properties={"baseline": 0.5},
    constraints={"range": {"min": 0.0, "max": 1.0}}
)
graph.register_concept(concept)

# 创建运行时状态
state = RuntimeState(graph)

# 使用
state.set_concept_value("test_concept", 0.8)
value = state.get_concept_value("test_concept")
print(f"值: {value}")  # 输出: 值: 0.8
```

---

## 📚 核心 API

### ConceptGraph

概念图谱，管理概念定义和关系。

```python
from matou_sakura import ConceptGraph, ConceptDefinition, ConceptType

graph = ConceptGraph()
concept = ConceptDefinition(
    name="my_concept",
    type=ConceptType.FLOAT,
    description="我的概念",
)
graph.register_concept(concept)
```

### RuntimeState

运行时状态，存储概念实例值。

```python
from matou_sakura import RuntimeState

state = RuntimeState(graph)
state.set_concept_value("my_concept", 0.5)
value = state.get_concept_value("my_concept")
```

### ConceptOperator

自定义处理器基类。

```python
from matou_sakura import ConceptOperator, RuntimeState

class MyProcessor(ConceptOperator):
    def execute(self, runtime_state: RuntimeState):
        # 读取
        input_val = runtime_state.get_concept_value("input")
        # 处理
        result = input_val * 2
        # 写入
        runtime_state.set_concept_value("output", result)

# 使用
processor = MyProcessor()
state.set_concept_value("input", 5)
processor.execute(state)
print(state.get_concept_value("output"))  # 输出: 10
```

---

## 🔄 典型使用模式

### 模式 1: 简单的状态管理

```python
from matou_sakura import ConceptGraph, RuntimeState, ConceptDefinition, ConceptType

# 初始化
graph = ConceptGraph()
graph.register_concept(ConceptDefinition(
    name="score", type=ConceptType.FLOAT, description="分数"
))
state = RuntimeState(graph)

# 使用
state.set_concept_value("score", 85.5)
score = state.get_concept_value("score")
```

### 模式 2: 处理循环

```python
import asyncio

async def main():
    # 创建状态
    graph = ConceptGraph()
    state = RuntimeState(graph)
    
    # 创建处理器
    processors = [
        InputProcessor(),
        LogicProcessor(),
        OutputProcessor(),
    ]
    
    # 主循环
    while True:
        for p in processors:
            p.execute(state)
        await asyncio.sleep(0.1)

asyncio.run(main())
```

### 模式 3: 集成到现有项目

```python
class MyAgent:
    def __init__(self):
        self.graph = ConceptGraph()
        self.state = RuntimeState(self.graph)
        # 注册你的概念...
    
    def process(self, input_data):
        # 写入输入概念
        self.state.set_concept_value("input", input_data)
        
        # 执行处理器
        for processor in self.processors:
            processor.execute(self.state)
        
        # 读取输出概念
        return self.state.get_concept_value("output")
```

---

## 📖 完整文档

- [打包与使用指南](SAKURA_PACKAGING_GUIDE.md) - 完整的打包和使用文档
- [架构设计](FINAL_ARCHITECTURE_V2.md) - 整体架构说明
- [重构路线图](SAKURA_REFACTOR_ROADMAP.md) - 内部优化计划（可选）
- [概念编译器](CONCEPT_COMPILER_DESIGN.md) - 长期优化方案（可选）

---

## ✅ 当前状态

```
打包配置:         ✅ 完成
核心 API:         ✅ 可用
导入测试:         ✅ 通过
示例程序:         ✅ 运行成功
文档:             ✅ 完整

可以开始在第三方项目中使用！
```

---

## 🎯 使用建议

1. **开发阶段**: 使用 PYTHONPATH 直接引用
2. **测试阶段**: 在虚拟环境中安装测试
3. **生产阶段**: 考虑发布到私有 PyPI 或 Git 仓库

---

**最后更新**: 2025-11-22  
**版本**: 0.1.0  
**状态**: ✅ 可用
