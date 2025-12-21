# 项目文档索引

> 所有文档的快速导航和说明

## 📚 核心文档

### 架构与设计

| 文档 | 说明 | 位置 |
|------|------|------|
| [AITuber 架构详解](./AITUBER_ARCHITECTURE_GUIDE.md) | 完整的系统架构、模块说明和时序图 | `docs/` |
| [Ortensia 集成说明](../ORTENSIA_INTEGRATION.md) | Ortensia 协议和集成方式 | 根目录 |
| [项目状态](../PROJECT_STATUS.md) | 项目整体状态和进度 | 根目录 |

### 功能模块

| 文档 | 说明 | 位置 |
|------|------|------|
| [VRM 动画系统](./VRM_ANIMATION_QUICKSTART.md) | VRM 动画加载和使用 | `docs/` |
| [ChatTTS 集成](../bridge/CHATTTS_USAGE.md) | ChatTTS TTS 引擎使用指南 | `bridge/` |
| [多角色支持](../bridge/MULTIROLE_GUIDE.md) | 多角色切换和管理 | `bridge/` |

### 开发指南

| 文档 | 说明 | 位置 |
|------|------|------|
| [快速开始](../QUICK_START.md) | 项目快速启动指南 | 根目录 |
| [Cursor Injector](../cursor-injector/QUICK_START.md) | Cursor 注入器使用 | `cursor-injector/` |
| [Agent Hooks](../cursor-hooks/QUICKSTART.md) | Agent 钩子开发 | `cursor-hooks/` |

---

## 🔧 技术文档

### WebSocket 通信

| 文档 | 说明 |
|------|------|
| [WebSocket 协议](../archive/WEBSOCKET_PROTOCOL_IMPLEMENTATION.md) | 消息格式和协议定义 |
| [对话 ID 协议](../CONVERSATION_ID_PROTOCOL.md) | 对话 ID 管理策略 |

### 前端架构

| 文档 | 说明 |
|------|------|
| [AITuber 架构详解](./AITUBER_ARCHITECTURE_GUIDE.md) | ⭐ 核心架构文档 |
| [动画系统设计](./ANIMATION_ACTION_DESIGN.md) | 动画系统实现 |

### 后端架构

| 文档 | 说明 |
|------|------|
| [Bridge 服务说明](../bridge/README.md) | Python 后端服务 |
| [TTS 管理器](../TTS_README.md) | TTS 引擎管理 |

---

## 🐛 问题修复记录

| 文档 | 说明 | 日期 |
|------|------|------|
| [AITuber 发现修复](../AITUBER_DISCOVERY_FIX.md) | 对话发现和 React Strict Mode 问题 | 2025-12-08 |
| [自动检查最终修复](../AUTO_CHECK_FINAL_FIX.md) | 自动任务检查功能修复 | 2025-12-08 |
| [Ortensia Manager 方案](../ORTENSIA_MANAGER_SOLUTION.md) | 中央协调器设计 | 2025-12-08 |
| [ChatTTS 集成总结](../CHATTTS_INTEGRATION_SUMMARY.md) | TTS 引擎切换 | 2025-12-07 |
| [萝莉音优化](../LOLI_VOICE_OPTIMIZATION_SUMMARY.md) | 语音参数调优 | 2025-12-07 |

---

## 📦 配置文档

### 安装和配置

| 文档 | 说明 |
|------|------|
| [环境配置](../cursor-injector/CONFIG.md) | 环境变量和配置项 |
| [窗口模式](../cursor-injector/WINDOW_MODES.md) | Cursor 窗口管理 |
| [安装脚本](../cursor-injector/install-v10.sh) | V10 安装脚本 |

### TTS 配置

| 文件 | 说明 |
|------|------|
| `bridge/tts_config.json` | TTS 引擎配置 |
| `bridge/CHATTTS_USAGE.md` | ChatTTS 使用说明 |
| `bridge/VOICE_GUIDE.md` | 语音选择指南 |

---

## 🧪 测试文档

### 测试脚本

| 脚本 | 说明 | 位置 |
|------|------|------|
| `test_agent_completed.py` | AGENT_COMPLETED 事件测试 | 根目录 |
| `bridge/test_chattts_integration.py` | ChatTTS 集成测试 | `bridge/` |
| `cursor-hooks/test_stop_hook.py` | Stop Hook 测试 | `cursor-hooks/` |

### 测试指南

| 文档 | 说明 |
|------|------|
| [中央服务器测试](../reports/CENTRAL_SERVER_TEST_GUIDE.md) | 完整功能测试流程 |
| [自动检查故障排查](../AUTO_CHECK_TROUBLESHOOTING.md) | 自动检查问题诊断 |

---

## 📊 项目报告

### 完成报告

| 报告 | 说明 | 日期 |
|------|------|------|
| [V9 完成报告](../reports/V9_COMPLETION_REPORT.md) | V9 版本功能总结 | 2024-11 |
| [项目最终总结](../reports/PROJECT_FINAL_SUMMARY.md) | 项目整体总结 | 2024-11 |
| [中央服务器成功报告](../reports/CENTRAL_SERVER_SUCCESS_REPORT.md) | 中央服务器架构 | 2024-11 |

### 实施总结

| 文档 | 说明 |
|------|------|
| [V10 实施总结](../V10_IMPLEMENTATION_SUMMARY.md) | V10 版本更新 |
| [Inject 状态总结](../INJECT_STATUS_SUMMARY.md) | Cursor Inject 状态 |

---

## 🎯 快速导航

### 我想...

- **开始使用项目** → [快速开始](../QUICK_START.md)
- **了解架构** → [AITuber 架构详解](./AITUBER_ARCHITECTURE_GUIDE.md) ⭐
- **配置 TTS** → [ChatTTS 使用指南](../bridge/CHATTTS_USAGE.md)
- **开发 Hook** → [Agent Hooks 快速开始](../cursor-hooks/QUICKSTART.md)
- **调试问题** → [故障排查](#-问题修复记录)
- **了解协议** → [WebSocket 协议](../archive/WEBSOCKET_PROTOCOL_IMPLEMENTATION.md)

### 常见问题

| 问题 | 文档 |
|------|------|
| 消息被处理多次 | [AITuber 架构详解 - 故障排查](./AITUBER_ARCHITECTURE_GUIDE.md#故障排查指南) |
| 自动检查不工作 | [自动检查最终修复](../AUTO_CHECK_FINAL_FIX.md) |
| VRM 加载错误 | [AITuber 架构详解 - 问题3](./AITUBER_ARCHITECTURE_GUIDE.md#问题-3vrm-加载错误) |
| 对话无法发现 | [AITuber 发现修复](../AITUBER_DISCOVERY_FIX.md) |
| TTS 不工作 | [ChatTTS 使用指南](../bridge/CHATTTS_USAGE.md) |

---

## 🗂️ 文档分类

### 按类型分类

**架构设计** (6 篇)
- AITuber 架构详解
- Ortensia 集成说明
- 动画系统设计
- WebSocket 协议
- 对话 ID 协议
- Ortensia Manager 方案

**使用指南** (8 篇)
- 快速开始
- ChatTTS 使用
- VRM 动画快速开始
- Agent Hooks 快速开始
- Cursor Injector 快速开始
- 窗口模式
- 语音选择指南
- 多角色指南

**问题修复** (5 篇)
- AITuber 发现修复
- 自动检查最终修复
- 萝莉音优化
- ChatTTS 集成总结
- 故障排查文档

**项目报告** (6 篇)
- V9 完成报告
- V10 实施总结
- 中央服务器报告
- 项目最终总结
- 项目状态
- Inject 状态总结

### 按受众分类

**开发者**
- [AITuber 架构详解](./AITUBER_ARCHITECTURE_GUIDE.md)
- [WebSocket 协议](../archive/WEBSOCKET_PROTOCOL_IMPLEMENTATION.md)
- [Agent Hooks](../cursor-hooks/QUICKSTART.md)

**用户**
- [快速开始](../QUICK_START.md)
- [ChatTTS 使用](../bridge/CHATTTS_USAGE.md)
- [语音选择](../bridge/VOICE_GUIDE.md)

**维护者**
- [项目状态](../PROJECT_STATUS.md)
- [故障排查](./AITUBER_ARCHITECTURE_GUIDE.md#故障排查指南)
- [配置文档](../cursor-injector/CONFIG.md)

---

## 📝 文档规范

### 创建新文档

1. **选择合适的位置**
   - 核心文档 → `docs/`
   - 模块文档 → 对应模块目录
   - 修复记录 → 根目录或 `docs/`

2. **文档命名**
   - 使用大写和下划线：`MY_DOCUMENT.md`
   - 描述性名称：`AITUBER_ARCHITECTURE_GUIDE.md`
   - 避免缩写：不要用 `AI_ARCH.md`

3. **文档结构**
   ```markdown
   # 标题
   > 简短描述
   
   ## 目录
   [可选，长文档建议添加]
   
   ## 内容章节
   ...
   
   ## 更新日志
   - 日期: 变更说明
   ```

4. **更新索引**
   - 新文档创建后更新本索引文件
   - 在相关文档中添加交叉引用

### 维护建议

- **定期更新**：功能变更时及时更新文档
- **清理过期**：将过期文档移到 `archive/`
- **版本标记**：重要变更标注日期和版本
- **交叉引用**：相关文档互相链接

---

## 🔗 外部资源

- [Next.js 文档](https://nextjs.org/docs)
- [VRM 规范](https://github.com/vrm-c/vrm-specification)
- [ChatTTS GitHub](https://github.com/2noise/ChatTTS)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

---

**索引维护者**: AI Assistant  
**最后更新**: 2025-12-08  
**总文档数**: 40+  
**版本**: 1.0.0


















