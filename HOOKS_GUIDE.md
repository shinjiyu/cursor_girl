# Cursor Hooks 完整指南

## 📚 概述

オルテンシア 现已支持 **10 个 Cursor Hooks**，可以自动响应你的所有编码操作！

## 🚀 快速部署

### 部署到当前项目

```bash
cd cursor-hooks
./deploy.sh ..
```

### 部署到其他项目

```bash
cd cursor-hooks
./deploy.sh /path/to/your/project
```

### 卸载

```bash
cd cursor-hooks
./undeploy.sh /path/to/your/project
```

---

## 🎣 支持的 Hooks (10个)

### 1. 文件操作 (1个)

#### ✅ post-save
**触发时机**: 文件保存后  
**オルテンシア 反应**: "保存成功~" 😊  
**使用场景**: Cmd+S 保存文件时自动触发

```bash
# 手动测试
./.cursor/hooks/post-save "/path/to/file.txt" "$(pwd)"
```

---

### 2. Git 操作 (3个)

#### ✅ pre-commit
**触发时机**: Git commit 前  
**オルテンシア 反应**: "准备提交..." 😊  
**使用场景**: 代码验证、格式化检查

```bash
# Cursor 自动在 git commit 前调用
# 手动测试
./.cursor/hooks/pre-commit
```

#### ✅ post-commit
**触发时机**: Git commit 后  
**オルテンシア 反应**: "太棒了！代码提交成功~" 🎉  
**使用场景**: 提交成功后的通知

```bash
# Cursor 自动在 git commit 后调用
# 手动测试
./.cursor/hooks/post-commit
```

#### ✅ post-push
**触发时机**: Git push 后  
**オルテンシア 反应**: "Push 完成！辛苦了~" 🎉  
**使用场景**: 推送成功后的通知

```bash
# Cursor 自动在 git push 后调用
# 手动测试
./.cursor/hooks/post-push "origin"
```

---

### 3. 构建 (2个)

#### ✅ on-build
**触发时机**: 构建开始时  
**オルテンシア 反应**: "开始构建..." 😊  
**使用场景**: npm run build, webpack, vite 等构建工具

```bash
# 手动测试
./.cursor/hooks/on-build "npm run build" "production"
```

#### ✅ post-build
**触发时机**: 构建完成后  
**オルテンシア 反应**:
- 成功: "构建成功！" 😊
- 失败: "构建失败了...别担心，我们一起修复它~" 😢

```bash
# 测试成功情况
./.cursor/hooks/post-build "success" "npm run build" "45" ""

# 测试失败情况
./.cursor/hooks/post-build "failure" "npm run build" "10" "Error: Module not found"
```

---

### 4. 测试 (2个)

#### ✅ on-test
**触发时机**: 测试开始时  
**オルテンシア 反应**: "开始测试..." 😊  
**使用场景**: npm test, jest, vitest 等测试工具

```bash
# 手动测试
./.cursor/hooks/on-test "npm test" "unit"
```

#### ✅ post-test
**触发时机**: 测试完成后  
**オルテンシア 反应**:
- 通过: "测试通过！你真厉害！" 🎊
- 失败: "测试失败了...我们再检查一下~" 😢

```bash
# 测试通过情况 (10个通过, 0个失败, 耗时2.5秒)
./.cursor/hooks/post-test "pass" "10" "0" "2.5"

# 测试失败情况 (8个通过, 2个失败, 耗时3.0秒)
./.cursor/hooks/post-test "fail" "8" "2" "3.0"
```

---

### 5. 错误处理 (1个)

#### ✅ on-error
**触发时机**: 错误发生时  
**オルテンシア 反应**:
- 语法错误: "语法错误...让我帮你看看~" 😢
- 运行时错误: "运行时错误...别担心，我们一起调试~" 😢
- 构建错误: "构建失败了...别担心，我们一起修复它~" 😢

```bash
# 语法错误
./.cursor/hooks/on-error "syntax" "Unexpected token" "test.js" "42"

# 运行时错误
./.cursor/hooks/on-error "runtime" "Cannot read property 'foo' of undefined" "app.js" "100"

# 构建错误
./.cursor/hooks/on-error "build" "Module not found: Error: Can't resolve './module'" "webpack.config.js" "0"
```

---

## 🔧 集成到你的工具

### npm/package.json

在 `package.json` 中添加 hooks：

```json
{
  "scripts": {
    "build": "npm run hook:build:start && vite build && npm run hook:build:end",
    "test": "npm run hook:test:start && vitest && npm run hook:test:end",
    "hook:build:start": "./.cursor/hooks/on-build 'npm run build' 'production'",
    "hook:build:end": "./.cursor/hooks/post-build 'success' 'npm run build' $BUILD_TIME",
    "hook:test:start": "./.cursor/hooks/on-test 'npm test' 'unit'",
    "hook:test:end": "./.cursor/hooks/post-test 'pass' $PASSED $FAILED $TEST_TIME"
  }
}
```

### Git Hooks (.git/hooks/)

Cursor hooks 可以与 Git hooks 集成：

```bash
# .git/hooks/pre-commit
#!/bin/bash
./.cursor/hooks/pre-commit

# .git/hooks/post-commit
#!/bin/bash
./.cursor/hooks/post-commit

# .git/hooks/post-push (Git 2.8+)
#!/bin/bash
./.cursor/hooks/post-push "$1"
```

### Webpack/Vite 插件

创建自定义插件来触发 hooks：

```javascript
// webpack.config.js
const { exec } = require('child_process');

class CursorHooksPlugin {
  apply(compiler) {
    compiler.hooks.compile.tap('CursorHooksPlugin', () => {
      exec('./.cursor/hooks/on-build "webpack" "production"');
    });
    
    compiler.hooks.done.tap('CursorHooksPlugin', (stats) => {
      const status = stats.hasErrors() ? 'failure' : 'success';
      const time = Math.round(stats.endTime - stats.startTime) / 1000;
      exec(`./.cursor/hooks/post-build "${status}" "webpack" "${time}"`);
    });
  }
}

module.exports = {
  plugins: [new CursorHooksPlugin()]
};
```

---

## 📊 完整工作流示例

### 典型的开发流程

```
1. 💻 编辑代码
   ↓

2. 💾 保存文件 (Cmd+S)
   → post-save hook
   → オルテンシア: "保存成功~" 😊
   ↓

3. 🏗️ 运行构建 (npm run build)
   → on-build hook
   → オルテンシア: "开始构建..." 😊
   → ... 构建中 ...
   → post-build hook
   → オルテンシア: "构建成功！" 😊
   ↓

4. 🧪 运行测试 (npm test)
   → on-test hook
   → オルテンシア: "开始测试..." 😊
   → ... 测试中 ...
   → post-test hook
   → オルテンシア: "测试通过！你真厉害！" 🎊
   ↓

5. 📦 Git 提交
   → pre-commit hook
   → オルテンシア: "准备提交..." 😊
   → ... 验证代码 ...
   → git commit -m "feat: add feature"
   → post-commit hook
   → オルテンシア: "太棒了！代码提交成功~" 🎉
   ↓

6. 🚀 Git 推送
   → git push
   → post-push hook
   → オルテンシア: "Push 完成！辛苦了~" 🎉
```

---

## 🎨 自定义消息

编辑 `.cursor/lib/websocket_sender.py` 来自定义消息：

```python
messages = {
    'file_save': ('你的自定义消息', '情绪类型'),
    'build_success': ('构建完美！', 'excited'),
    # ...
}
```

支持的情绪类型：
- `neutral` - 中性
- `happy` - 开心
- `sad` - 难过
- `angry` - 生气
- `relaxed` - 放松
- `surprised` - 惊讶
- `excited` - 兴奋

---

## 📝 Hook 参数详解

### post-save
```bash
post-save <file_path> <working_dir>
```

### pre-commit
```bash
pre-commit  # 无参数，自动检测 Git staged files
```

### post-commit
```bash
post-commit  # 无参数，自动获取 Git commit 信息
```

### post-push
```bash
post-push <remote>  # 例如: origin
```

### on-build
```bash
on-build <command> <type>  # 例如: "npm run build" "production"
```

### post-build
```bash
post-build <status> <command> <duration> <output>
# 例如: "success" "npm run build" "45" ""
```

### on-test
```bash
on-test <command> <type>  # 例如: "npm test" "unit"
```

### post-test
```bash
post-test <status> <passed> <failed> <duration>
# 例如: "pass" "10" "0" "2.5"
```

### on-error
```bash
on-error <type> <message> <file> <line>
# 例如: "syntax" "Unexpected token" "test.js" "42"
```

---

## 🐛 故障排查

### Hook 没有触发

1. **检查权限**:
   ```bash
   ls -l .cursor/hooks/
   # 应该看到 -rwxr-xr-x
   ```

2. **检查配置**:
   ```bash
   cat .cursor/hooks/config.sh
   ```

3. **手动测试 hook**:
   ```bash
   ./.cursor/hooks/post-save "test.txt" "$(pwd)"
   ```

### オルテンシア 没有响应

1. **检查 WebSocket 服务器**:
   ```bash
   lsof -i :8000
   ```

2. **查看日志**:
   ```bash
   tail -f /tmp/cursor-hooks.log
   ```

3. **测试 WebSocket 连接**:
   ```bash
   cd bridge
   source venv/bin/activate
   python websocket_client.py
   ```

---

## 🎯 最佳实践

1. **不要在 hooks 中执行耗时操作** - Hooks 应该快速完成
2. **使用 DEBUG 模式调试** - 设置 `DEBUG=true` 在 config.sh
3. **定期清理日志** - `> /tmp/cursor-hooks.log`
4. **自定义消息** - 让オルテンシア更符合你的个性
5. **组合使用 hooks** - 构建完整的工作流

---

## 📚 参考

- [Cursor Hooks 官方文档](https://cursor.com/en-US/docs/agent/hooks)
- [主 README](./README.md)
- [WebSocket 架构](./WEBSOCKET_ARCHITECTURE.md)

---

**状态**: ✅ 10 个 Hooks 全部实现  
**版本**: 1.2.0  
**最后更新**: 2025-11-02

🎊 **享受和オルテンシア一起编程的完整体验！**

