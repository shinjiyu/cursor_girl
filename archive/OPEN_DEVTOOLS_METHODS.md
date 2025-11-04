# 打开 Cursor DevTools 的所有方法

## 🎯 多种方式

### 方法 1: 菜单 ⭐⭐⭐⭐⭐ (最可靠)

**macOS**:
```
Help → Toggle Developer Tools
```

或者:
```
View → Toggle Developer Tools
```

**如果找不到菜单**，试试：
```
顶部菜单栏 → Help → 搜索 "developer" 或 "toggle"
```

---

### 方法 2: 命令面板 ⭐⭐⭐⭐⭐ (推荐)

1. 按 **`Cmd + Shift + P`** 打开命令面板
2. 输入 `developer`
3. 选择 **`Developer: Toggle Developer Tools`**

![命令面板](https://i.imgur.com/example.png)

或者输入：
- `Toggle Developer Tools`
- `DevTools`
- `Debug`

---

### 方法 3: 其他快捷键

试试这些（可能其中一个能用）：

```bash
# macOS
Cmd + Option + I          # 替代方案 1
Cmd + Shift + C          # 检查元素模式
Cmd + Option + J         # 直接打开 Console
F12                      # 标准快捷键（macOS 需要 Fn + F12）

# 如果有 Touch Bar
触摸 Touch Bar 上的开发者工具图标
```

---

### 方法 4: 修改快捷键 ⭐⭐⭐⭐

如果默认快捷键被占用，可以重新绑定：

1. 按 **`Cmd + K, Cmd + S`** 打开快捷键设置
   - 或者 `Cmd + Shift + P` → `Preferences: Open Keyboard Shortcuts`

2. 搜索 `Toggle Developer Tools`

3. 点击左边的 `+` 或双击现有快捷键

4. 设置新的快捷键，比如：
   - `Cmd + Option + D`
   - `Cmd + Shift + D`
   - 或任何你喜欢的组合

---

### 方法 5: 创建自定义命令 ⭐⭐⭐

创建一个快速打开 DevTools 的脚本：

#### 方法 5.1: AppleScript (macOS)

```applescript
#!/usr/bin/osascript
# 保存为 open-cursor-devtools.scpt

tell application "Cursor"
    activate
end tell

tell application "System Events"
    tell process "Cursor"
        click menu item "Toggle Developer Tools" of menu "Help" of menu bar 1
    end tell
end tell
```

运行：
```bash
osascript open-cursor-devtools.scpt
```

#### 方法 5.2: Shell 脚本

```bash
#!/bin/bash
# 保存为 open-devtools.sh

osascript -e '
tell application "System Events"
    tell process "Cursor"
        click menu item "Toggle Developer Tools" of menu "Help" of menu bar 1
    end tell
end tell
'
```

使用：
```bash
chmod +x open-devtools.sh
./open-devtools.sh
```

---

### 方法 6: 通过启动参数

启动 Cursor 时自动打开 DevTools：

```bash
# macOS
/Applications/Cursor.app/Contents/MacOS/Cursor --inspect --remote-debugging-port=9222
```

或者创建一个启动脚本：
```bash
#!/bin/bash
# start-cursor-with-devtools.sh

/Applications/Cursor.app/Contents/MacOS/Cursor \
    --inspect \
    --remote-debugging-port=9222 \
    --auto-open-devtools-for-tabs \
    "$@"
```

---

## ⚡ 最快的方法（现在就试）

### 推荐顺序：

1. **命令面板** （`Cmd + Shift + P` → 输入 `developer`） ⭐
2. **菜单** （`Help` → `Toggle Developer Tools`）
3. **F12** 或 **Fn + F12**
4. **Cmd + Option + I**

---

## 🔧 如果还是打不开

### 检查清单：

```bash
# 1. 检查 Cursor 是否禁用了 DevTools
# 在终端运行：
defaults read com.cursor.plist DisableDevTools
# 如果返回 1，说明被禁用了

# 2. 重置设置
defaults delete com.cursor.plist DisableDevTools

# 3. 重启 Cursor
```

### 强制打开 DevTools（终极方案）

```bash
# 1. 关闭 Cursor

# 2. 以调试模式启动
/Applications/Cursor.app/Contents/MacOS/Cursor \
    --enable-devtools \
    --remote-debugging-port=9222 \
    --inspect

# DevTools 会自动打开
```

---

## 🎯 测试是否成功

当 DevTools 打开后，你应该看到：

```
┌─────────────────────────────────────┐
│ Elements | Console | Sources | ... │  ← 标签页
├─────────────────────────────────────┤
│                                     │
│  >  (控制台输入区域)                 │  ← 可以输入 JavaScript
│                                     │
└─────────────────────────────────────┘
```

---

## 📝 现在就试试

### 步骤 1: 打开 DevTools

**最简单的方法**：
1. 按 **`Cmd + Shift + P`**
2. 输入 `toggle dev`
3. 按 Enter

### 步骤 2: 运行测试脚本

在 Console 标签粘贴：

```javascript
// 快速测试 - 验证 DevTools 是否正常工作
console.log('✅ DevTools 已打开！');
console.log('📋 现在可以测试 Cursor 命令了');

// 测试 vscode API 是否可用
if (typeof vscode !== 'undefined') {
    console.log('✅ vscode API 可用');
    console.log('🚀 可以运行完整测试脚本');
} else {
    console.log('❌ vscode API 不可用（可能需要在扩展上下文）');
    console.log('💡 但可以搜索 DOM 元素和全局对象');
}
```

---

## 💡 如果 vscode API 不可用

在 DevTools 中仍然可以做很多事情：

### 1. 搜索 Cursor 的全局对象

```javascript
// 查找所有包含 'cursor' 的全局变量
Object.keys(window).filter(k => 
    k.toLowerCase().includes('cursor') ||
    k.toLowerCase().includes('vscode')
).forEach(k => console.log(k, ':', typeof window[k]));
```

### 2. 分析 DOM 结构

```javascript
// 查找 AI 聊天相关元素
const aiElements = document.querySelectorAll(
    '[class*="ai"], [class*="chat"], [class*="composer"]'
);
console.log(`找到 ${aiElements.length} 个 AI 元素`);
```

### 3. 监听网络请求

切换到 **Network** 标签，然后：
- 点击 Cursor 的 AI 聊天
- 观察发送了什么请求
- 查看请求参数和响应

---

## 🎯 总结

### 打开 DevTools 最简单的方法：

1. **`Cmd + Shift + P`** → 输入 `developer` → Enter ✅
2. **Help 菜单** → Toggle Developer Tools ✅
3. **Fn + F12** ✅

### 如果都不行：

```bash
# 以调试模式启动 Cursor
/Applications/Cursor.app/Contents/MacOS/Cursor --inspect
```

---

**现在试试其中一种方法，然后告诉我结果！** 🚀

