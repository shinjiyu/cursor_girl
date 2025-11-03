# Test Cursor Commands Extension

测试 Cursor 中可用的命令和 API。

## 安装

### 方法 1: 直接加载（最简单）

1. 在 Cursor 中按 `Cmd+Shift+P`
2. 输入 `Developer: Install Extension from Location`
3. 选择这个文件夹 `test-cursor-commands/`
4. 重启 Cursor

### 方法 2: 打包安装

```bash
cd test-cursor-commands

# 安装 vsce（如果还没安装）
npm install -g @vscode/vsce

# 打包
vsce package --allow-missing-repository

# 会生成 test-cursor-commands-0.0.1.vsix
```

然后在 Cursor 中：
1. 打开 Extensions 面板
2. 点击 `...` 菜单
3. 选择 `Install from VSIX...`
4. 选择生成的 .vsix 文件

## 使用

### 自动测试

扩展激活后会自动运行一次测试，查看 DevTools Console 查看结果。

### 手动测试

**列出所有 Cursor 命令**：
1. `Cmd+Shift+P`
2. 输入 `Test: List All Cursor Commands`

**测试所有命令**：
1. `Cmd+Shift+P`
2. 输入 `Test: Test All Cursor Commands`

## 查看结果

### Console 日志

打开 DevTools Console (`Cmd+Shift+P` → `Toggle Developer Tools`)

你会看到：
```
================================================================================
🧪 Testing Cursor Commands
================================================================================

测试 15 个命令...

测试: cursor.aichat...
  ✅ 成功! 返回: undefined

测试: cursor.composer...
  ❌ 失败: command 'cursor.composer' requires argument 'prompt'

...

================================================================================
📊 测试报告
================================================================================

✅ 成功: 8
❌ 失败: 7

✅ 可用命令:
  - cursor.aichat
  - workbench.panel.aichat.view
  ...

❌ 不可用命令 (可能需要参数):
  - cursor.composer (原因: requires argument 'prompt')
  ...
================================================================================
```

### Markdown 报告

测试完成后会自动打开一个 Markdown 文档，包含详细的测试结果。

## 输出文件

测试结果会显示在：
- DevTools Console (实时日志)
- Markdown 文档 (格式化报告)

## 疑难解答

### 如果看不到输出

1. 打开 DevTools: `Cmd+Shift+P` → `Toggle Developer Tools`
2. 切换到 Console 标签
3. 重新运行命令

### 如果扩展没有激活

1. 检查扩展是否已安装: Extensions 面板 → 搜索 "Test Cursor Commands"
2. 重启 Cursor
3. 查看 DevTools Console 是否有错误信息

### 如果命令找不到

1. `Cmd+Shift+P`
2. 输入 `test` 
3. 应该能看到 "Test: List All Cursor Commands" 和 "Test: Test All Cursor Commands"

## 下一步

根据测试结果，我们可以：
1. 确定哪些 Cursor 命令可用
2. 了解需要什么参数
3. 设计 Ortensia 扩展的实施方案

