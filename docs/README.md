# 项目文档

> AITuber Kit + Ortensia 集成系统

---

## 🤖 AI 协作

**处理任何任务前，请先阅读 [AI_INDEX.md](./AI_INDEX.md)**

---

## 📂 目录结构

```
docs/
├── AI_INDEX.md          # 🤖 AI 协作入口（必读）
│
├── protocols/           # 📜 协议文档（核心）
│   ├── README.md       # 协议索引
│   ├── WEBSOCKET_PROTOCOL.md
│   └── AITUBER_PROTOCOL.md
│
├── _FEATURES/           # 📦 功能实现记录
│   ├── _TEMPLATE.md    # 模板
│   └── *.md            # 各功能
│
├── _DECISIONS/          # 🎯 架构决策 (ADR)
│   └── ADR-*.md
│
├── guides/              # 📖 使用指南
│   ├── AITUBER_ARCHITECTURE_GUIDE.md
│   ├── TROUBLESHOOTING_INDEX.md
│   └── *.md
│
└── archive/             # 📁 归档（旧文档）
```

---

## 🚀 快速导航

| 我想... | 文档 |
|--------|------|
| **AI 协作开发** | [AI_INDEX.md](./AI_INDEX.md) ⭐ |
| 了解协议 | [protocols/](./protocols/) |
| 了解架构 | [guides/AITUBER_ARCHITECTURE_GUIDE.md](./guides/AITUBER_ARCHITECTURE_GUIDE.md) |
| 排查问题 | [guides/TROUBLESHOOTING_INDEX.md](./guides/TROUBLESHOOTING_INDEX.md) |
| 查看功能实现 | [_FEATURES/](./_FEATURES/) |

---

## 📋 文档规范

本项目遵循 [Vibe Coding 文档规范](./VIBE_CODING_DOC_STANDARD.md)

核心原则：
1. **协议优先** - 协议是系统的核心
2. **代码地图 > 描述** - 告诉 AI 代码在哪，而不是做什么
3. **陷阱清单** - 记录踩过的坑
4. **不记录变更** - Git 已经做了
