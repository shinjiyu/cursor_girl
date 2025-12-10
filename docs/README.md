# 项目文档

> AITuber Kit + Ortensia 集成系统完整文档

## 🎯 快速开始

### 我是...

**新用户** → 阅读 [快速开始](../QUICK_START.md) 了解如何启动项目

**开发者** → 阅读 [AITuber 架构详解](./AITUBER_ARCHITECTURE_GUIDE.md) 了解系统设计

**遇到问题** → 查看 [故障排查索引](./TROUBLESHOOTING_INDEX.md) 快速定位解决方案

**查找文档** → 浏览 [文档索引](./PROJECT_DOCUMENTATION_INDEX.md) 查看所有可用文档

---

## 📚 核心文档（必读）

### 1. [AITuber 架构详解](./AITUBER_ARCHITECTURE_GUIDE.md) ⭐

**内容**：
- 系统架构图和模块说明
- 完整的初始化时序
- 消息流转详解
- 自动任务检查流程
- 故障排查指南
- 最佳实践和性能优化

**适合**：开发者、架构师、维护者

**关键概念**：
- OrtensiaManager：中央协调器
- OrtensiaClient：WebSocket 客户端
- React Strict Mode 兼容
- 消息去重机制
- 对话发现重试

---

### 2. [项目文档索引](./PROJECT_DOCUMENTATION_INDEX.md)

**内容**：
- 40+ 文档的完整索引
- 按类型和受众分类
- 快速导航和常见问题
- 文档维护规范

**适合**：所有人

**分类**：
- 架构设计（6 篇）
- 使用指南（8 篇）
- 问题修复（5 篇）
- 项目报告（6 篇）

---

### 3. [故障排查索引](./TROUBLESHOOTING_INDEX.md)

**内容**：
- 症状 → 解决方案快速查找
- 按类别分类的常见问题
- 调试工具和命令
- 检查清单和紧急处理

**适合**：开发者、维护者

**涵盖问题**：
- 消息处理问题
- 对话发现问题
- VRM 和动画问题
- 自动任务检查问题
- TTS 和后端问题

---

## 🗺️ 文档结构

```
docs/
├── README.md                           # 本文件
├── AITUBER_ARCHITECTURE_GUIDE.md      # ⭐ 架构详解
├── PROJECT_DOCUMENTATION_INDEX.md      # 文档索引
├── TROUBLESHOOTING_INDEX.md           # 故障排查
├── AITUBER_ARCHITECTURE.md            # 旧架构文档
├── ANIMATION_ACTION_DESIGN.md         # 动画系统
├── VRM_ANIMATION_QUICKSTART.md        # VRM 快速开始
└── [其他文档...]

根目录/
├── QUICK_START.md                     # 快速开始
├── PROJECT_STATUS.md                  # 项目状态
├── README.md                          # 项目简介
├── ORTENSIA_INTEGRATION.md            # Ortensia 集成
└── [最近修复文档...]

bridge/
├── README.md                          # Bridge 服务
├── CHATTTS_USAGE.md                   # ChatTTS 使用
├── MULTIROLE_GUIDE.md                 # 多角色指南
└── [TTS 相关文档...]

cursor-hooks/
├── QUICKSTART.md                      # Hook 快速开始
├── README.md                          # Hook 说明
└── [Hook 开发文档...]

cursor-injector/
├── QUICK_START.md                     # Injector 快速开始
├── CONFIG.md                          # 配置说明
├── WINDOW_MODES.md                    # 窗口模式
└── [Injector 文档...]
```

---

## 🎓 学习路径

### 路径 1：从零开始

```
1. 快速开始 (QUICK_START.md)
   ↓
2. 项目简介 (README.md)
   ↓
3. Ortensia 集成 (ORTENSIA_INTEGRATION.md)
   ↓
4. AITuber 架构 (AITUBER_ARCHITECTURE_GUIDE.md)
   ↓
5. 具体模块文档
```

### 路径 2：解决问题

```
1. 故障排查索引 (TROUBLESHOOTING_INDEX.md)
   ↓
2. 查找症状对应的文档
   ↓
3. 阅读详细解决方案
   ↓
4. 如需深入，阅读架构文档
```

### 路径 3：开发新功能

```
1. AITuber 架构详解 (AITUBER_ARCHITECTURE_GUIDE.md)
   ↓
2. WebSocket 协议 (WEBSOCKET_PROTOCOL_IMPLEMENTATION.md)
   ↓
3. 相关模块文档
   ↓
4. 参考现有实现
```

---

## 🔄 最近更新

### 2025-12-08 - 文档大整理

**新增文档**：
- ✨ AITuber 架构详解（完整重写）
- ✨ 项目文档索引
- ✨ 故障排查索引
- ✨ 本 README

**主要改进**：
- 完整的架构和时序说明
- 40+ 文档统一索引
- 症状 → 解决方案快速查找
- 清晰的学习路径

**修复的问题**：
- 消息重复处理
- 自动任务检查
- 对话发现时序
- VRM 加载错误

---

## 📊 文档统计

- **总文档数**: 40+
- **核心架构文档**: 6 篇
- **使用指南**: 8 篇
- **问题修复记录**: 5 篇
- **项目报告**: 6 篇
- **代码注释率**: 85%+

---

## 💡 贡献指南

### 创建新文档

1. 选择合适的位置（参考文档结构）
2. 使用描述性命名（大写 + 下划线）
3. 遵循文档模板：
   ```markdown
   # 标题
   > 简短描述
   
   ## 目录
   
   ## 内容
   
   ## 更新日志
   ```
4. 更新文档索引

### 更新现有文档

1. 在文档末尾添加更新日志
2. 更新最后更新日期
3. 如有重大变更，在 `docs/README.md` 中记录

### 文档规范

- **清晰性**: 使用简单语言，避免行话
- **完整性**: 包含必要的上下文和示例
- **准确性**: 确保代码和说明同步
- **可维护**: 添加交叉引用，便于更新

---

## 🔗 外部资源

- [Next.js 文档](https://nextjs.org/docs)
- [React 文档](https://react.dev)
- [VRM 规范](https://github.com/vrm-c/vrm-specification)
- [ChatTTS](https://github.com/2noise/ChatTTS)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Zustand](https://github.com/pmndrs/zustand)
- [Three.js](https://threejs.org/docs/)

---

## ❓ 常见问题

### Q: 从哪里开始阅读文档？

**A**: 取决于你的目标：
- 快速上手 → [快速开始](../QUICK_START.md)
- 深入理解 → [架构详解](./AITUBER_ARCHITECTURE_GUIDE.md)
- 解决问题 → [故障排查](./TROUBLESHOOTING_INDEX.md)

### Q: 文档太多，如何查找？

**A**: 使用 [文档索引](./PROJECT_DOCUMENTATION_INDEX.md) 的搜索功能或分类浏览

### Q: 发现文档错误怎么办？

**A**: 
1. 检查是否是最新版本
2. 查看 Git 历史是否有更新
3. 提交 Issue 或直接修改

### Q: 某个功能没有文档？

**A**: 
1. 查看代码注释
2. 查看相关测试文件
3. 参考类似功能的文档
4. 考虑创建新文档

---

## 📝 待完善

- [ ] 添加更多架构图和流程图
- [ ] 补充 API 参考文档
- [ ] 创建视频教程
- [ ] 添加交互式示例
- [ ] 翻译成英文版本

---

## 📮 反馈

如果你对文档有任何建议或发现问题，欢迎：
- 提交 Issue
- 直接修改并提交 PR
- 在团队聊天中讨论

---

**文档维护**: AI Assistant  
**最后更新**: 2025-12-08  
**版本**: 2.0.0  
**状态**: ✅ 已完成大整理







