# Sakura 打包与使用指南

> **创建时间**: 2025-11-22  
> **状态**: 规划中  
> **目标**: 将 Sakura 打包为可复用的 Python 库

---

## 📋 目录

- [打包目标](#打包目标)
- [对外接口设计](#对外接口设计)
- [打包配置](#打包配置)
- [使用示例](#使用示例)
- [安装方式](#安装方式)

---

## 打包目标

### 核心需求

```
将 matou_sakura 打包为标准 Python 包，支持:
  ✅ pip 安装
  ✅ 清晰的公共 API
  ✅ 最小依赖
  ✅ 易于集成
```

### 包结构

```
matou_sakura/                    # 源代码包
├── __init__.py                  # 包入口，导出公共 API
├── persona/                     # 核心模块
│   ├── __init__.py
│   ├── knowledge_graph_agent.py
│   ├── working_memory.py
│   ├── operators.py
│   ├── graph_constants.py
│   ├── influence_propagator.py
│   └── interfaces.py
├── config/                      # 配置文件
│   ├── knowledge_graph.json
│   └── simplified_knowledge_graph.json
└── utils/                       # 工具模块
    └── ...

docs/                            # 文档（不打包）
examples/                        # 示例（不打包）
tests/                          # 测试（不打包）
setup.py 或 pyproject.toml       # 打包配置
README.md                        # 使用说明
```

---

## 对外接口设计

### 公共 API 原则

```
原则:
  ✅ 只导出必要的类和函数
  ✅ 隐藏内部实现细节
  ✅ 保持接口稳定
  ✅ 清晰的文档和类型提示
```

### 顶层 API (`matou_sakura/__init__.py`)

```python
# matou_sakura/__init__.py
"""
Sakura - 基于概念图谱的 AI Agent 认知系统

核心组件:
  - ConceptGraph: 概念图谱
  - RuntimeState: 概念实例集合
  - ConceptOperator: 概念处理器基类

基本用法:
    >>> from matou_sakura import ConceptGraph, RuntimeState
    >>> graph = ConceptGraph.from_config("config.json")
    >>> state = RuntimeState(graph)
    >>> state.set_concept_value("test", 1.0)
    >>> print(state.get_concept_value("test"))
"""

__version__ = "0.1.0"
__author__ = "Your Name"

# ============ 核心类 ============

# 概念图谱
from .persona.knowledge_graph_agent import (
    ConceptGraph,
    RuntimeState,
    ConceptDefinition,
    ConceptRelation,
)

# 处理器基类
from .persona.interfaces import ConceptOperator

# 工作记忆
from .persona.working_memory import WorkingMemory

# ============ 常量 ============

from .persona.graph_constants import (
    ConceptType,
    RelationType,
    ConstraintKey,
    PropertyKey,
)

# ============ 导出列表 ============

__all__ = [
    # 版本信息
    "__version__",
    
    # 核心类
    "ConceptGraph",
    "RuntimeState",
    "ConceptDefinition",
    "ConceptRelation",
    "ConceptOperator",
    "WorkingMemory",
    
    # 常量
    "ConceptType",
    "RelationType",
    "ConstraintKey",
    "PropertyKey",
]
```

### 核心使用流程

```python
from matou_sakura import ConceptGraph, RuntimeState, ConceptOperator

# 1. 加载概念图谱
graph = ConceptGraph.from_config("path/to/knowledge_graph.json")

# 2. 创建运行时状态
state = RuntimeState(graph)

# 3. 读写概念
state.set_concept_value("cursor_state", {"status": "idle"})
cursor_state = state.get_concept_value("cursor_state")

# 4. 创建自定义处理器
class MyProcessor(ConceptOperator):
    def execute(self, runtime_state: RuntimeState):
        # 读取概念
        value = runtime_state.get_concept_value("input_concept")
        
        # 处理逻辑
        result = self.process(value)
        
        # 写入概念
        runtime_state.set_concept_value("output_concept", result)

# 5. 执行处理器
processor = MyProcessor()
processor.execute(state)
```

---

## 打包配置

### 方案 A: `setup.py` (传统方式)

```python
# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="matou-sakura",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="基于概念图谱的 AI Agent 认知系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/matou_sakura",
    packages=find_packages(exclude=["tests", "docs", "examples"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "matou_sakura": [
            "config/*.json",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
)
```

### 方案 B: `pyproject.toml` (现代方式，推荐)

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "matou-sakura"
version = "0.1.0"
description = "基于概念图谱的 AI Agent 认知系统"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["ai", "agent", "cognitive-architecture", "concept-graph"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

dependencies = [
    "openai>=1.0.0",
    "anthropic>=0.7.0",
    "numpy>=1.24.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]
all = [
    "aiohttp>=3.8.0",
    "websockets>=11.0.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/matou_sakura"
Documentation = "https://matou-sakura.readthedocs.io"
Repository = "https://github.com/yourusername/matou_sakura"
"Bug Tracker" = "https://github.com/yourusername/matou_sakura/issues"

[tool.setuptools]
packages = ["matou_sakura", "matou_sakura.persona", "matou_sakura.utils"]

[tool.setuptools.package-data]
matou_sakura = ["config/*.json"]
```

### `MANIFEST.in` (包含额外文件)

```
# MANIFEST.in
include README.md
include LICENSE
include requirements.txt
recursive-include matou_sakura/config *.json
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
```

### `requirements.txt` (依赖列表)

```
# requirements.txt
# 核心依赖（最小化）
openai>=1.0.0
anthropic>=0.7.0
numpy>=1.24.0
pydantic>=2.0.0

# 可选依赖
# aiohttp>=3.8.0
# websockets>=11.0.0
```

---

## 使用示例

### 示例 1: 基础使用

```python
# examples/basic_usage.py
"""
基础使用示例：加载概念图谱，读写概念
"""
from matou_sakura import ConceptGraph, RuntimeState

def main():
    # 1. 加载概念图谱
    graph = ConceptGraph.from_config("path/to/knowledge_graph.json")
    print(f"Loaded {len(graph.concepts)} concepts")
    
    # 2. 创建运行时状态
    state = RuntimeState(graph)
    
    # 3. 设置概念值
    state.set_concept_value("emotion_happiness", 0.8)
    state.set_concept_value("cursor_state", {
        "status": "idle",
        "open_files": ["main.py", "utils.py"]
    })
    
    # 4. 读取概念值
    happiness = state.get_concept_value("emotion_happiness")
    print(f"Happiness: {happiness}")
    
    cursor_state = state.get_concept_value("cursor_state")
    print(f"Cursor state: {cursor_state}")
    
    # 5. 影响传播（自动）
    # 设置一个概念可能会影响其他相关概念
    state.set_concept_value("task_difficulty", 0.9)
    stress = state.get_concept_value("emotion_stress")
    print(f"Stress (after task difficulty): {stress}")

if __name__ == "__main__":
    main()
```

### 示例 2: 自定义处理器

```python
# examples/custom_processor.py
"""
自定义处理器示例
"""
from matou_sakura import ConceptGraph, RuntimeState, ConceptOperator

class CursorAnalyzer(ConceptOperator):
    """分析 Cursor 状态的处理器"""
    
    def execute(self, runtime_state: RuntimeState):
        # 读取 Cursor 状态
        cursor_state = runtime_state.get_concept_value("cursor_state")
        
        if not cursor_state:
            return
        
        # 分析文件数量
        num_files = len(cursor_state.get("open_files", []))
        
        # 根据文件数量设置认知负载
        if num_files > 10:
            cognitive_load = 0.8
        elif num_files > 5:
            cognitive_load = 0.5
        else:
            cognitive_load = 0.2
        
        # 写入分析结果
        runtime_state.set_concept_value("cognitive_load", cognitive_load)
        print(f"Analyzed: {num_files} files -> cognitive load: {cognitive_load}")

def main():
    # 加载图谱
    graph = ConceptGraph.from_config("path/to/knowledge_graph.json")
    state = RuntimeState(graph)
    
    # 设置 Cursor 状态
    state.set_concept_value("cursor_state", {
        "status": "editing",
        "open_files": ["file1.py", "file2.py", "file3.py"] * 5  # 15 个文件
    })
    
    # 执行处理器
    analyzer = CursorAnalyzer()
    analyzer.execute(state)
    
    # 检查结果
    cognitive_load = state.get_concept_value("cognitive_load")
    print(f"Final cognitive load: {cognitive_load}")

if __name__ == "__main__":
    main()
```

### 示例 3: 处理循环

```python
# examples/processing_loop.py
"""
处理循环示例：持续运行多个处理器
"""
import asyncio
from matou_sakura import ConceptGraph, RuntimeState, ConceptOperator

class InputProcessor(ConceptOperator):
    """模拟输入处理"""
    def execute(self, runtime_state: RuntimeState):
        # 模拟外部输入
        import random
        value = random.random()
        runtime_state.set_concept_value("sensor_input", value)
        print(f"Input: {value}")

class LogicProcessor(ConceptOperator):
    """业务逻辑处理"""
    def execute(self, runtime_state: RuntimeState):
        sensor_input = runtime_state.get_concept_value("sensor_input")
        if sensor_input is None:
            return
        
        # 简单的处理逻辑
        result = sensor_input * 2
        runtime_state.set_concept_value("processed_output", result)
        print(f"Processed: {sensor_input} -> {result}")

class OutputProcessor(ConceptOperator):
    """输出处理"""
    def execute(self, runtime_state: RuntimeState):
        output = runtime_state.get_concept_value("processed_output")
        if output is not None:
            print(f"Output: {output}")
            # 清空已处理的输出
            runtime_state.set_concept_value("processed_output", None)

async def main():
    # 初始化
    graph = ConceptGraph.from_config("path/to/knowledge_graph.json")
    state = RuntimeState(graph)
    
    # 创建处理器
    processors = [
        InputProcessor(),
        LogicProcessor(),
        OutputProcessor(),
    ]
    
    # 主循环
    print("Starting processing loop...")
    for i in range(10):
        print(f"\n--- Cycle {i+1} ---")
        for processor in processors:
            processor.execute(state)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
```

### 示例 4: 集成到第三方项目

```python
# third_party_project/my_agent.py
"""
第三方项目集成示例
"""
from matou_sakura import ConceptGraph, RuntimeState, ConceptOperator
import openai

class MyAIAgent:
    """自定义 AI Agent，使用 Sakura 作为认知核心"""
    
    def __init__(self, config_path: str):
        # 加载 Sakura 概念系统
        self.concept_graph = ConceptGraph.from_config(config_path)
        self.state = RuntimeState(self.concept_graph)
        
        # 注册自定义处理器
        self.processors = [
            TaskAnalyzer(),
            DecisionMaker(),
            ActionGenerator(),
        ]
        
        print("AI Agent initialized with Sakura cognitive system")
    
    def process_input(self, user_input: str):
        """处理用户输入"""
        # 写入概念
        self.state.set_concept_value("user_input", user_input)
        
        # 执行处理器
        for processor in self.processors:
            processor.execute(self.state)
        
        # 获取输出
        action = self.state.get_concept_value("next_action")
        return action
    
    def get_state_summary(self):
        """获取当前状态摘要"""
        return {
            "emotion": self.state.get_concept_value("emotion_happiness"),
            "cognitive_load": self.state.get_concept_value("cognitive_load"),
            "current_task": self.state.get_concept_value("current_task"),
        }

class TaskAnalyzer(ConceptOperator):
    """任务分析器"""
    def execute(self, runtime_state: RuntimeState):
        user_input = runtime_state.get_concept_value("user_input")
        if not user_input:
            return
        
        # 简单的任务识别
        if "help" in user_input.lower():
            runtime_state.set_concept_value("current_task", "provide_help")
        elif "code" in user_input.lower():
            runtime_state.set_concept_value("current_task", "write_code")
        else:
            runtime_state.set_concept_value("current_task", "general_chat")

class DecisionMaker(ConceptOperator):
    """决策器"""
    def execute(self, runtime_state: RuntimeState):
        task = runtime_state.get_concept_value("current_task")
        if not task:
            return
        
        # 根据任务类型决策
        decisions = {
            "provide_help": "show_documentation",
            "write_code": "generate_code",
            "general_chat": "generate_response",
        }
        
        decision = decisions.get(task, "default_action")
        runtime_state.set_concept_value("decision", decision)

class ActionGenerator(ConceptOperator):
    """动作生成器"""
    def execute(self, runtime_state: RuntimeState):
        decision = runtime_state.get_concept_value("decision")
        if not decision:
            return
        
        # 生成具体动作
        actions = {
            "show_documentation": {"type": "display", "content": "docs"},
            "generate_code": {"type": "code", "language": "python"},
            "generate_response": {"type": "text", "tone": "friendly"},
        }
        
        action = actions.get(decision, {"type": "none"})
        runtime_state.set_concept_value("next_action", action)

# 使用示例
if __name__ == "__main__":
    agent = MyAIAgent("config/knowledge_graph.json")
    
    # 处理用户输入
    action = agent.process_input("Can you help me write some code?")
    print(f"Action: {action}")
    
    # 查看状态
    summary = agent.get_state_summary()
    print(f"State: {summary}")
```

---

## 安装方式

### 开发安装（本地开发）

```bash
# 1. 克隆或复制项目
cd matou_sakura

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装（可编辑模式）
pip install -e .

# 4. 安装开发依赖
pip install -e ".[dev]"
```

### 从源码安装

```bash
# 1. 构建分发包
python setup.py sdist bdist_wheel

# 2. 安装
pip install dist/matou_sakura-0.1.0-py3-none-any.whl
```

### 从 Git 仓库安装

```bash
# 直接从 GitHub 安装
pip install git+https://github.com/yourusername/matou_sakura.git

# 安装特定分支
pip install git+https://github.com/yourusername/matou_sakura.git@main

# 安装特定版本
pip install git+https://github.com/yourusername/matou_sakura.git@v0.1.0
```

### 发布到 PyPI（可选）

```bash
# 1. 注册 PyPI 账号 (https://pypi.org)

# 2. 安装发布工具
pip install twine

# 3. 构建分发包
python setup.py sdist bdist_wheel

# 4. 检查包
twine check dist/*

# 5. 上传到 TestPyPI (测试)
twine upload --repository testpypi dist/*

# 6. 测试安装
pip install --index-url https://test.pypi.org/simple/ matou-sakura

# 7. 上传到 PyPI (正式)
twine upload dist/*

# 8. 安装
pip install matou-sakura
```

---

## 最小化示例

### 最简使用（5 行代码）

```python
from matou_sakura import ConceptGraph, RuntimeState

graph = ConceptGraph.from_config("config.json")
state = RuntimeState(graph)
state.set_concept_value("test", 1.0)
print(state.get_concept_value("test"))  # 输出: 1.0
```

---

## 目录结构重组（打包前）

```bash
cursorgirl/
├── matou_sakura/                # 重命名或整理
│   ├── __init__.py              # 添加公共 API
│   ├── persona/
│   ├── config/
│   └── utils/
├── examples/                    # 新增：使用示例
│   ├── basic_usage.py
│   ├── custom_processor.py
│   └── processing_loop.py
├── tests/                       # 已有：测试
├── docs/                        # 文档
├── setup.py                     # 或 pyproject.toml
├── MANIFEST.in
├── requirements.txt
├── README.md                    # 用户文档
└── LICENSE                      # 许可证
```

---

## 下一步行动

### 立即执行

```bash
# 1. 整理目录结构
cd /Users/user/Documents/cursorgirl/matou_sakura

# 2. 创建 __init__.py（导出公共 API）
cat > __init__.py << 'EOF'
# 公共 API
__version__ = "0.1.0"

from .persona.knowledge_graph_agent import (
    ConceptGraph,
    RuntimeState,
    ConceptDefinition,
)
from .persona.interfaces import ConceptOperator
from .persona.graph_constants import ConceptType, RelationType

__all__ = [
    "__version__",
    "ConceptGraph",
    "RuntimeState",
    "ConceptDefinition",
    "ConceptOperator",
    "ConceptType",
    "RelationType",
]
EOF

# 3. 创建 pyproject.toml
# (参考上面的配置)

# 4. 创建 README.md
# (包含安装和使用说明)

# 5. 测试安装
pip install -e .

# 6. 测试导入
python -c "from matou_sakura import ConceptGraph; print('Success!')"
```

---

## 相关文档

- `SAKURA_REFACTOR_ROADMAP.md` - 内部重构计划（后续优化）
- `CONCEPT_COMPILER_DESIGN.md` - 概念编译器设计（长期）
- `OPTIMIZATION_COMPLETE.md` - 已完成的优化

---

**文档版本**: 1.0  
**最后更新**: 2025-11-22  
**状态**: 待实施

