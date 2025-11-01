# オルテンシア 待办事项

## 🔴 紧急任务（本周）

### 1. Cursor IDE 扩展开发（核心功能）
**状态**: ⏳ 未开始  
**优先级**: P0 - 最高  
**预计时间**: 2-3 天

这是让オルテンシア真正"活起来"的关键！目前只能手动测试，需要实现自动捕获编码事件。

#### 子任务：
- [ ] 研究 Cursor/VSCode 扩展 API 文档
- [ ] 创建扩展项目 `cursorgirl-extension/`
- [ ] 实现文件保存事件监听
- [ ] 实现 WebSocket 客户端连接 bridge
- [ ] 测试完整流程：
  ```
  保存文件 → Cursor扩展捕获 → 发送到bridge → オルテンシア反应 ✨
  ```

**参考资料**:
- https://code.visualstudio.com/api/get-started/your-first-extension
- https://code.visualstudio.com/api/references/vscode-api

---

## 🟡 重要任务（本月）

### 2. 完善 Cursor 扩展功能
**状态**: ⏳ 等待任务1完成  
**优先级**: P1 - 高  
**预计时间**: 3-5 天

- [ ] 实现 Git 操作事件（commit, push, merge）
- [ ] 实现错误检测（Linter 集成）
- [ ] 实现测试运行事件
- [ ] 添加扩展设置界面
- [ ] 添加状态栏图标和快捷开关

### 3. TTS 引擎扩展
**状态**: ⏳ 可选  
**优先级**: P2 - 中  
**预计时间**: 1-2 天

目前只有 macOS TTS，考虑添加：
- [ ] Edge TTS（免费，支持中文）
- [ ] Azure TTS（需要 API key）
- [ ] 在线 TTS 服务（备用方案）

---

## 🟢 优化任务（后续）

### 4. 用户体验优化
- [ ] 优化 Electron 窗口透明度
- [ ] 添加设置面板（TTS 音色、音量、速度）
- [ ] 实现主题切换
- [ ] 添加快捷键支持

### 5. 动画和表情增强
- [ ] 加载 `.vrma` 动画文件
- [ ] 更丰富的身体动作
- [ ] 表情过渡动画
- [ ] 支持多个 VRM 模型切换

### 6. 性能和稳定性
- [ ] 添加错误重试机制
- [ ] 优化 WebSocket 重连逻辑
- [ ] 添加性能监控
- [ ] 日志系统统一管理

---

## 📅 时间线

```
Week 1 (11/01-11/07)
├─ Day 1-2: 研究 Cursor 扩展 API
├─ Day 3-4: 实现基础文件事件监听
└─ Day 5-7: 测试和调试

Week 2 (11/08-11/14)
├─ Day 8-10: 实现 Git 和错误事件
├─ Day 11-12: 添加配置界面
└─ Day 13-14: 完善文档和打包

Week 3 (11/15-11/21)
├─ 内部测试和反馈收集
└─ Bug 修复和优化

Week 4 (11/22-11/30)
├─ 添加更多 TTS 引擎
└─ 动画和表情优化
```

---

## 🎯 本周目标

**目标**: 完成 Cursor 扩展的基础版本

**定义完成标准**:
1. ✅ 能自动捕获文件保存事件
2. ✅ 能通过 WebSocket 发送到 bridge
3. ✅ オルテンシア 能正确反应（表情+语音）
4. ✅ 扩展能正常安装和启用

**成功指标**:
- 保存文件 → オルテンシア 说 "保存成功~" ✨
- 提交代码 → オルテンシア 说 "太棒了！" 😊
- 出现错误 → オルテンシア 说 "别担心，我们一起修复它~" 🤗

---

## 💡 快速开始

### 今天就开始做任务 1！

1. **创建扩展项目**:
```bash
cd "/Users/user/Documents/ cursorgirl"
mkdir cursorgirl-extension
cd cursorgirl-extension
npm init -y
npm install @types/vscode @types/node typescript
npx tsc --init
```

2. **创建基础文件**:
```
cursorgirl-extension/
├── package.json          # 扩展配置
├── tsconfig.json         # TypeScript 配置
└── src/
    └── extension.ts      # 扩展入口
```

3. **参考代码模板** (见下方)

---

## 📝 扩展代码模板

### package.json
```json
{
  "name": "cursorgirl-extension",
  "displayName": "オルテンシア AI Assistant",
  "description": "AI programming assistant with VRM character",
  "version": "0.1.0",
  "engines": {
    "vscode": "^1.80.0"
  },
  "activationEvents": [
    "onStartupFinished"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "cursorgirl.enable",
        "title": "オルテンシア: Enable"
      }
    ]
  }
}
```

### src/extension.ts (起点)
```typescript
import * as vscode from 'vscode';
import WebSocket from 'ws';

let ws: WebSocket | null = null;

export function activate(context: vscode.ExtensionContext) {
    console.log('オルテンシア extension activated!');
    
    // 连接到 WebSocket bridge
    connectToWebSocket();
    
    // 监听文件保存事件
    vscode.workspace.onDidSaveTextDocument((document) => {
        const fileName = document.fileName;
        sendEvent('file_save', { file: fileName });
    });
}

function connectToWebSocket() {
    ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.on('open', () => {
        console.log('✅ Connected to オルテンシア bridge');
    });
    
    ws.on('error', (error) => {
        console.error('❌ WebSocket error:', error);
    });
}

function sendEvent(eventType: string, data: any) {
    if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: eventType,
            data: data,
            timestamp: Date.now()
        }));
    }
}

export function deactivate() {
    ws?.close();
}
```

---

## 🚀 下一步

1. **今天**: 创建扩展项目，实现基础文件保存监听
2. **明天**: 完善 WebSocket 连接，测试端到端流程
3. **后天**: 添加更多事件类型，优化用户体验

---

**记住**: オルテンシア 已经能说话和表达情绪了，现在只需要让她"听到"你的编码过程！🎉

**需要帮助?** 查看:
- `ROADMAP.md` - 完整开发路线图
- `WEBSOCKET_ARCHITECTURE.md` - WebSocket 通信架构
- `README.md` - 项目说明

---

**最后更新**: 2025-11-01  
**状态**: Phase 1 完成 ✅ → Phase 2 准备开始 🚀

