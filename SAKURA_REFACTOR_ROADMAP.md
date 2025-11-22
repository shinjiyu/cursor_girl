# Sakura 项目改造路线图 V2

> **创建时间**: 2025-11-22  
> **状态**: 规划中  
> **目标**: 将 Sakura 改造为简洁、可复用的核心库

---

## 📋 目录

- [核心理念](#核心理念)
- [已完成工作](#已完成工作)
- [待改造清单](#待改造清单)
- [实施优先级](#实施优先级)

---

## 核心理念

### Persona 的本质

```
Persona Core = 概念实例集合 + Processors 列表
```

**就这么简单！**

```python
class PersonaCore:
    def __init__(self):
        # 核心组件 1: 概念实例集合 (RuntimeState)
        self.runtime_state = RuntimeState()
        
        # 核心组件 2: Processors 列表
        self.processors = []
    
    # 基本接口
    def get_concept(self, name: str) -> Any:
        return self.runtime_state.get_concept_value(name)
    
    def set_concept(self, name: str, value: Any):
        self.runtime_state.set_concept_value(name, value)
    
    def register_processor(self, processor: ConceptProcessor):
        self.processors.append(processor)
    
    def update(self):
        """执行一次处理循环"""
        for processor in self.processors:
            if processor.should_execute(self.runtime_state):
                processor.execute(self.runtime_state)
```

### 架构层次

```
┌─────────────────────────────────────────┐
│         Persona Core (核心)             │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │   RuntimeState (概念实例集合)     │  │
│  │   - 概念名 -> 概念值              │  │
│  │   - 影响传播                      │  │
│  │   - 约束验证                      │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │   Processors (处理器列表)         │  │
│  │   - CursorCommandGenerator        │  │
│  │   - ConversationHandler           │  │
│  │   - ReflectionProcessor           │  │
│  │   - ...                           │  │
│  └───────────────────────────────────┘  │
│                                         │
│  接口:                                  │
│  • get_concept(name)                    │
│  • set_concept(name, value)             │
│  • register_processor(processor)        │
│  • update()  # 执行一轮处理             │
└─────────────────────────────────────────┘
                    ↕
        外部通过读写概念来交互
                    ↕
┌─────────────────────────────────────────┐
│      应用层 (event_driven_main.py)      │
│                                         │
│  • 创建 PersonaCore                     │
│  • 注册 Processors                      │
│  • Input 循环: 外部数据 → set_concept() │
│  • Output 循环: get_concept() → 执行动作│
│  • 主循环: 定期调用 persona.update()    │
└─────────────────────────────────────────┘
```

**关键设计原则**：

```
✅ 核心简洁: PersonaCore 只管理概念和 Processors
✅ 职责清晰: I/O 适配在应用层完成
✅ 不过度设计: 不需要复杂的插件系统
✅ 声明式接口: Processors 声明输入/输出概念
```

---

## 已完成工作

### ✅ Phase 0: 基础优化 (已完成)

```
1. 冗余清理
   ✅ 删除 22 个冗余文件
   ✅ 代码量减少 50%

2. 常量规范化
   ✅ 新增 70+ 个常量
   ✅ 消除 150+ 处硬编码
   ✅ 创建 graph_constants.py

3. 职责分离
   ✅ RuntimeState → 纯数据容器
   ✅ InfluencePropagator → 影响传播逻辑

4. 配置验证
   ✅ ConfigValidator 自动验证
   ✅ 类型安全检查

文档: OPTIMIZATION_COMPLETE.md
```

---

## 待改造清单

### 🔴 Phase 1: Processor 开发规范 (P0)

#### 目标

建立声明式的 Processor 接口，让 Processor 的行为透明化。

#### 1.1 新的 Processor 基类

**文件**: `persona/processor_interface.py`

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Any

class ConceptProcessor(ABC):
    """
    概念处理器基类
    
    使用声明式接口描述 Processor 的行为
    """
    
    # ============ 元数据声明 ============
    
    @property
    def name(self) -> str:
        """处理器名称"""
        return self.__class__.__name__
    
    @property
    def required_concepts(self) -> List[str]:
        """
        必需的概念（不存在会报错）
        
        返回:
            概念名列表，例如: ["cursor_state", "current_task"]
        """
        return []
    
    @property
    def input_concepts(self) -> List[str]:
        """
        会读取的概念
        
        返回:
            概念名列表，例如: ["cursor_state", "user_input"]
        
        用途:
            - 依赖分析
            - 数据流可视化
            - 调度优化
        """
        return []
    
    @property
    def output_concepts(self) -> List[str]:
        """
        会修改的概念
        
        返回:
            概念名列表，例如: ["cursor_command", "next_action"]
        
        用途:
            - 冲突检测（多个 Processor 修改同一概念）
            - 数据流可视化
            - 影响分析
        """
        return []
    
    @property
    def trigger_condition(self) -> Optional[Callable[[Any], bool]]:
        """
        可选：触发条件
        
        返回:
            接受 RuntimeState，返回 bool 的函数
            返回 True 时才执行此 Processor
        
        示例:
            lambda state: state.get_concept_value("user_input") is not None
        """
        return None
    
    @property
    def priority(self) -> int:
        """
        执行优先级（数字越小越优先）
        
        返回:
            优先级数字，默认 100
        
        说明:
            - 0-49: 高优先级（输入处理、状态同步）
            - 50-149: 普通优先级（业务逻辑）
            - 150-199: 低优先级（反思、日志）
        """
        return 100
    
    # ============ 执行接口 ============
    
    @abstractmethod
    def execute(self, runtime_state):
        """
        执行处理逻辑
        
        参数:
            runtime_state: RuntimeState 实例
        
        应该:
            1. 使用 runtime_state.get_concept_value() 读取概念
            2. 执行处理逻辑（LLM 调用、计算等）
            3. 使用 runtime_state.set_concept_value() 更新概念
        
        注意:
            - 不要在这里做 I/O 适配（那是应用层的事）
            - 只处理概念级的信息
        """
        pass
    
    # ============ 辅助方法 ============
    
    def validate_concepts(self, runtime_state) -> bool:
        """验证所需概念是否存在"""
        for concept_name in self.required_concepts:
            if not runtime_state.has_concept(concept_name):
                logging.warning(
                    f"{self.name}: Required concept '{concept_name}' not found"
                )
                return False
        return True
    
    def should_execute(self, runtime_state) -> bool:
        """判断是否应该执行"""
        # 1. 验证必需概念存在
        if not self.validate_concepts(runtime_state):
            return False
        
        # 2. 检查触发条件
        if self.trigger_condition:
            try:
                return self.trigger_condition(runtime_state)
            except Exception as e:
                logging.error(f"{self.name}: Trigger condition failed: {e}")
                return False
        
        return True
    
    def get_metadata(self) -> dict:
        """获取 Processor 元数据（用于可视化、调试）"""
        return {
            "name": self.name,
            "required_concepts": self.required_concepts,
            "input_concepts": self.input_concepts,
            "output_concepts": self.output_concepts,
            "priority": self.priority,
            "has_trigger": self.trigger_condition is not None,
        }
```

#### 1.2 Processor 示例

**示例 1: Cursor 命令生成器**

```python
# processors/cursor_command_generator.py
class CursorCommandGenerator(ConceptProcessor):
    """根据当前任务生成 Cursor IDE 控制指令"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    @property
    def required_concepts(self):
        return ["cursor_state"]
    
    @property
    def input_concepts(self):
        return ["cursor_state", "current_task", "working_memory"]
    
    @property
    def output_concepts(self):
        return ["cursor_command"]
    
    @property
    def trigger_condition(self):
        # 只有当有任务且当前没有命令时才生成
        def check(state):
            has_task = state.get_concept_value("current_task") is not None
            no_command = state.get_concept_value("cursor_command") is None
            return has_task and no_command
        return check
    
    @property
    def priority(self):
        return 60  # 普通优先级
    
    def execute(self, runtime_state):
        # 读取概念
        cursor_state = runtime_state.get_concept_value("cursor_state")
        task = runtime_state.get_concept_value("current_task")
        memory = runtime_state.get_concept_value("working_memory")
        
        # 生成命令（调用 LLM）
        prompt = self._build_prompt(cursor_state, task, memory)
        command = self.llm.generate(prompt)
        
        # 写入概念
        runtime_state.set_concept_value("cursor_command", command)
        
        logging.info(f"Generated cursor command: {command}")
    
    def _build_prompt(self, cursor_state, task, memory):
        # ... 构建 prompt
        pass
```

**示例 2: 反思处理器**

```python
# processors/reflection_processor.py
class ReflectionProcessor(ConceptProcessor):
    """定期反思，分析行为模式"""
    
    def __init__(self, reflection_interval=300):
        self.reflection_interval = reflection_interval
        self.last_reflection_time = 0
    
    @property
    def input_concepts(self):
        return ["working_memory", "recent_actions", "concept_statistics"]
    
    @property
    def output_concepts(self):
        return ["reflection_result", "self_adjustment"]
    
    @property
    def trigger_condition(self):
        # 每 N 秒触发一次
        def check(state):
            import time
            current_time = time.time()
            if current_time - self.last_reflection_time > self.reflection_interval:
                self.last_reflection_time = current_time
                return True
            return False
        return check
    
    @property
    def priority(self):
        return 150  # 低优先级
    
    def execute(self, runtime_state):
        # 读取最近的记忆和行为
        memory = runtime_state.get_concept_value("working_memory")
        actions = runtime_state.get_concept_value("recent_actions")
        
        # 生成反思
        reflection = self._analyze_behavior(memory, actions)
        
        # 写入结果
        runtime_state.set_concept_value("reflection_result", reflection)
        
        # 如果需要调整，设置调整指令
        if reflection.needs_adjustment:
            runtime_state.set_concept_value("self_adjustment", reflection.adjustment)
    
    def _analyze_behavior(self, memory, actions):
        # ... 分析逻辑
        pass
```

#### 1.3 改造现有 Processors

**任务清单**：

- [ ] 创建 `persona/processor_interface.py`
- [ ] 重构 `ConceptOperator` → `ConceptProcessor`
- [ ] 为所有现有 Processor 添加元数据声明
  - [ ] `CursorCommandGenerator`
  - [ ] `ConversationHandler`
  - [ ] `ReflectionProcessor`
  - [ ] `GoalProcessor`
  - [ ] 其他...

---

### 🔴 Phase 2: PersonaCore 标准化 (P0)

#### 目标

创建清晰、简洁的 PersonaCore 类，封装核心逻辑。

#### 2.1 PersonaCore 实现

**文件**: `persona/core.py`

```python
import logging
from typing import List, Dict, Any, Optional
from .processor_interface import ConceptProcessor
from .knowledge_graph_agent import RuntimeState, ConceptGraph

class PersonaCore:
    """
    Persona 核心
    
    组成:
        - RuntimeState: 概念实例集合
        - Processors: 处理器列表
    
    职责:
        - 管理概念的读写
        - 管理 Processors 的注册和执行
        - 提供统一的处理循环
    """
    
    def __init__(self, concept_graph: ConceptGraph):
        """
        初始化 PersonaCore
        
        参数:
            concept_graph: 概念图谱（包含概念定义和关系）
        """
        self.concept_graph = concept_graph
        self.runtime_state = RuntimeState(concept_graph)
        self.processors: List[ConceptProcessor] = []
        self._sorted_processors: Optional[List[ConceptProcessor]] = None
        
        logging.info("PersonaCore initialized")
    
    # ============ 概念访问接口 ============
    
    def get_concept(self, name: str, default: Any = None) -> Any:
        """
        获取概念值
        
        参数:
            name: 概念名
            default: 概念不存在时的默认值
        
        返回:
            概念值，或 default
        """
        try:
            return self.runtime_state.get_concept_value(name)
        except KeyError:
            return default
    
    def set_concept(self, name: str, value: Any):
        """
        设置概念值（会触发影响传播）
        
        参数:
            name: 概念名
            value: 新值
        """
        self.runtime_state.set_concept_value(name, value)
    
    def has_concept(self, name: str) -> bool:
        """检查概念是否存在"""
        return self.runtime_state.has_concept(name)
    
    # ============ Processor 管理 ============
    
    def register_processor(self, processor: ConceptProcessor):
        """
        注册 Processor
        
        参数:
            processor: ConceptProcessor 实例
        """
        self.processors.append(processor)
        self._sorted_processors = None  # 失效排序缓存
        
        logging.info(
            f"Registered processor: {processor.name} "
            f"(priority={processor.priority})"
        )
    
    def unregister_processor(self, processor_name: str):
        """移除 Processor"""
        self.processors = [
            p for p in self.processors 
            if p.name != processor_name
        ]
        self._sorted_processors = None
        
        logging.info(f"Unregistered processor: {processor_name}")
    
    def get_processor(self, name: str) -> Optional[ConceptProcessor]:
        """根据名称获取 Processor"""
        for processor in self.processors:
            if processor.name == name:
                return processor
        return None
    
    def list_processors(self) -> List[Dict[str, Any]]:
        """列出所有 Processors 的元数据"""
        return [p.get_metadata() for p in self.processors]
    
    # ============ 处理循环 ============
    
    def update(self):
        """
        执行一次处理循环
        
        流程:
            1. 按优先级排序 Processors
            2. 依次执行满足触发条件的 Processors
            3. 每个 Processor 可能修改概念（触发影响传播）
        """
        # 排序（使用缓存）
        if self._sorted_processors is None:
            self._sorted_processors = sorted(
                self.processors,
                key=lambda p: p.priority
            )
        
        # 执行
        for processor in self._sorted_processors:
            if processor.should_execute(self.runtime_state):
                try:
                    processor.execute(self.runtime_state)
                except Exception as e:
                    logging.error(
                        f"Processor {processor.name} failed: {e}",
                        exc_info=True
                    )
    
    # ============ 调试和反射 ============
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息（用于反思和调试）"""
        return {
            "num_processors": len(self.processors),
            "num_concepts": len(self.runtime_state._concepts),
            "active_concepts": sum(
                1 for v in self.runtime_state._concepts.values()
                if v is not None
            ),
            "processors": self.list_processors(),
        }
    
    def visualize_dataflow(self) -> Dict[str, Any]:
        """可视化数据流（概念 -> Processors -> 概念）"""
        nodes = []
        edges = []
        
        # 概念节点
        for concept_name in self.runtime_state._concepts.keys():
            nodes.append({"id": concept_name, "type": "concept"})
        
        # Processor 节点和边
        for processor in self.processors:
            proc_name = processor.name
            nodes.append({"id": proc_name, "type": "processor"})
            
            # 输入边
            for concept in processor.input_concepts:
                edges.append({"from": concept, "to": proc_name})
            
            # 输出边
            for concept in processor.output_concepts:
                edges.append({"from": proc_name, "to": concept})
        
        return {"nodes": nodes, "edges": edges}
```

#### 2.2 应用层简化

**目标**: 重写 `event_driven_main.py` → `main.py`

```python
# main.py
import asyncio
import logging
from persona.core import PersonaCore
from persona.knowledge_graph_agent import ConceptGraph
from processors.cursor_command_generator import CursorCommandGenerator
from processors.conversation_handler import ConversationHandler
from processors.reflection_processor import ReflectionProcessor
# ... 其他 imports

async def main():
    # 1. 加载概念图谱
    concept_graph = ConceptGraph.from_config("config/knowledge_graph.json")
    
    # 2. 创建 PersonaCore
    persona = PersonaCore(concept_graph)
    
    # 3. 注册 Processors
    persona.register_processor(CursorCommandGenerator(llm_client))
    persona.register_processor(ConversationHandler(llm_client))
    persona.register_processor(ReflectionProcessor())
    # ... 其他 processors
    
    # 4. 启动输入循环（从外部系统读取数据 → 写入概念）
    asyncio.create_task(cursor_input_loop(persona, ortensia_client))
    asyncio.create_task(user_input_loop(persona, web_interface))
    
    # 5. 启动输出循环（读取概念 → 执行外部动作）
    asyncio.create_task(cursor_output_loop(persona, ortensia_client))
    asyncio.create_task(speech_output_loop(persona, tts_engine))
    
    # 6. 主处理循环
    while True:
        persona.update()
        await asyncio.sleep(0.1)  # 100ms 一次

# ============ 输入适配器 ============

async def cursor_input_loop(persona: PersonaCore, client):
    """从 Cursor 读取状态 → 写入概念"""
    while True:
        try:
            state = await client.get_cursor_state()
            persona.set_concept("cursor_state", state)
        except Exception as e:
            logging.error(f"Cursor input error: {e}")
        await asyncio.sleep(0.5)

async def user_input_loop(persona: PersonaCore, web_interface):
    """从 Web UI 读取用户输入 → 写入概念"""
    async for message in web_interface.message_stream():
        persona.set_concept("user_input", message)

# ============ 输出适配器 ============

async def cursor_output_loop(persona: PersonaCore, client):
    """读取概念 → 执行 Cursor 命令"""
    last_command = None
    while True:
        command = persona.get_concept("cursor_command")
        if command and command != last_command:
            await client.execute_command(command)
            last_command = command
            # 清空命令（已执行）
            persona.set_concept("cursor_command", None)
        await asyncio.sleep(0.1)

async def speech_output_loop(persona: PersonaCore, tts):
    """读取概念 → 语音合成"""
    last_speech = None
    while True:
        speech = persona.get_concept("speech_output")
        if speech and speech != last_speech:
            await tts.speak(speech)
            last_speech = speech
            persona.set_concept("speech_output", None)
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
```

#### 2.3 改造任务

- [ ] 创建 `persona/core.py` - PersonaCore 类
- [ ] 重写 `main.py`（简化版）
- [ ] 重构 `event_driven_main.py` 中的逻辑，提取为：
  - [ ] Input 适配器函数
  - [ ] Output 适配器函数
  - [ ] Processor 注册逻辑
- [ ] 测试端到端流程

---

### 🟡 Phase 3: 概念管理增强 (P1)

#### 3.1 概念注册中心

**目标**: 统一管理概念定义

**文件**: `persona/concept_registry.py`

```python
class ConceptRegistry:
    """概念注册中心"""
    
    def __init__(self):
        self.definitions = {}  # name -> ConceptDefinition
        self.categories = {}   # category -> [concept_names]
    
    def register_concept(self, definition: ConceptDefinition):
        """注册概念定义"""
        self.definitions[definition.name] = definition
        
        # 按类别索引
        category = definition.category
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(definition.name)
    
    def get_definition(self, name: str) -> ConceptDefinition:
        """获取概念定义"""
        return self.definitions.get(name)
    
    def list_concepts(self, category: str = None) -> List[ConceptDefinition]:
        """列出概念"""
        if category:
            names = self.categories.get(category, [])
            return [self.definitions[name] for name in names]
        return list(self.definitions.values())
    
    def find_concepts_by_type(self, concept_type: str) -> List[ConceptDefinition]:
        """按类型查找概念"""
        return [
            d for d in self.definitions.values()
            if d.type == concept_type
        ]
```

#### 3.2 改造任务

- [ ] 创建 `persona/concept_registry.py`
- [ ] 将 `ConceptGraph` 集成 `ConceptRegistry`
- [ ] 实现概念查询 API

---

### 🟢 Phase 4: 反射能力 (P2)

#### 4.1 概念历史追踪

**文件**: `persona/concept_history.py`

```python
@dataclass
class ConceptChange:
    concept_name: str
    old_value: Any
    new_value: Any
    timestamp: float
    source: str  # 哪个 Processor 修改的

class ConceptHistory:
    """追踪概念变化历史"""
    
    def __init__(self, max_history=1000):
        self.history: List[ConceptChange] = []
        self.max_history = max_history
    
    def record(self, change: ConceptChange):
        self.history.append(change)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_changes(self, concept_name: str, limit: int = 100):
        return [
            c for c in self.history[-limit:]
            if c.concept_name == concept_name
        ]
    
    def analyze_frequency(self, concept_name: str) -> float:
        """分析变化频率"""
        changes = self.get_changes(concept_name)
        if len(changes) < 2:
            return 0.0
        time_span = changes[-1].timestamp - changes[0].timestamp
        return len(changes) / max(time_span, 1.0)
```

#### 4.2 改造任务

- [ ] 创建 `persona/concept_history.py`
- [ ] 在 `RuntimeState.set_concept_value` 中记录历史
- [ ] 集成到 `PersonaCore`

---

## 实施优先级

### 🔥 P0: 必须完成（2-3 周）

```
Phase 1: Processor 开发规范         [1 周]
  - 设计 ConceptProcessor 接口
  - 重构现有 Processors
  - 添加元数据声明

Phase 2: PersonaCore 标准化         [1-2 周]
  - 实现 PersonaCore 类
  - 简化应用层代码
  - 端到端测试

验收标准:
  ✅ PersonaCore 接口清晰
  ✅ Processors 可声明输入/输出
  ✅ 应用层代码简化 50%
  ✅ 所有功能正常工作
```

### ⚡ P1: 重要（1-2 周）

```
Phase 3: 概念管理增强              [1 周]
  - 概念注册中心
  - 概念查询 API

验收标准:
  ✅ 概念定义统一管理
  ✅ 可以方便地查询概念
```

### 🌟 P2: 长期优化（按需）

```
Phase 4: 反射能力                  [1 周]
  - 概念历史追踪
  - 增强反思 Processor

验收标准:
  ✅ 可以追踪概念变化历史
  ✅ 反思能力增强
```

---

## 设计对比

### 之前的设计（过度复杂）

```
❌ 复杂的插件系统
❌ Input/Output Bus
❌ PluginSandbox
❌ 多层适配器
❌ 大量抽象层
```

### 现在的设计（简洁）

```
✅ 核心: RuntimeState + Processors
✅ 声明式接口: Processor 声明输入/输出
✅ 应用层负责: I/O 适配
✅ 最小抽象: 只在必要时抽象
```

---

## 相关文档

- `CONCEPT_COMPILER_DESIGN.md` - 概念编译器设计（长期）
- `OPTIMIZATION_COMPLETE.md` - 已完成的优化
- `FINAL_ARCHITECTURE_V2.md` - 整体架构设计

---

**文档版本**: 2.0  
**最后更新**: 2025-11-22  
**状态**: 规划中，待执行

