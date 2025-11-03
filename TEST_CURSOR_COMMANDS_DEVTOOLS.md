# 在 DevTools 中测试 Cursor 命令

**目的**: 快速验证哪些 Cursor 命令可用，无需创建扩展

---

## 🚀 立即测试

### 步骤 1: 打开 DevTools

在 Cursor 中：
- macOS: `Cmd + Shift + I` 或 `Cmd + Option + I`
- Windows/Linux: `Ctrl + Shift + I`

或者：
- 菜单: `Help` → `Toggle Developer Tools`

### 步骤 2: 粘贴测试脚本

在 Console 标签中，粘贴以下代码：

```javascript
// ============================================================================
// Cursor 命令测试脚本
// 使用方法：
// 1. 在 Cursor 中按 Cmd+Shift+I 打开 DevTools
// 2. 切换到 Console 标签
// 3. 复制粘贴这整段代码
// 4. 按 Enter 运行
// 5. 查看结果
// ============================================================================

console.clear();
console.log('🔍 开始测试 Cursor 命令...\n');

(async function testCursorCommands() {
    // 1. 获取所有已注册的命令
    console.log('📋 Step 1: 获取所有命令...');
    
    try {
        // VSCode API 在 DevTools 中可能以不同方式暴露
        // 我们需要找到命令注册表
        
        // 方法 1: 尝试访问 vscode API
        if (typeof vscode !== 'undefined') {
            console.log('✅ 找到 vscode 全局对象');
            
            const commands = await vscode.commands.getCommands(true);
            console.log(`✅ 总共 ${commands.length} 个命令\n`);
            
            // 2. 过滤 Cursor 相关命令
            const cursorCommands = commands.filter(cmd => 
                cmd.includes('cursor') || 
                cmd.includes('aichat') || 
                cmd.includes('composer') ||
                cmd.includes('ai.')
            ).sort();
            
            console.log('=' .repeat(80));
            console.log(`📌 找到 ${cursorCommands.length} 个 Cursor 相关命令:`);
            console.log('=' .repeat(80));
            cursorCommands.forEach(cmd => console.log(`  - ${cmd}`));
            console.log('=' .repeat(80));
            console.log('');
            
            // 3. 测试每个命令
            console.log('🧪 Step 2: 测试每个命令...\n');
            
            const results = [];
            
            for (const cmd of cursorCommands) {
                try {
                    console.log(`测试: ${cmd}...`);
                    const result = await vscode.commands.executeCommand(cmd);
                    
                    console.log(`  ✅ 成功! 返回值: ${JSON.stringify(result)?.substring(0, 100)}`);
                    results.push({
                        command: cmd,
                        success: true,
                        result: result,
                        error: null
                    });
                } catch (error) {
                    console.log(`  ❌ 失败: ${error.message}`);
                    results.push({
                        command: cmd,
                        success: false,
                        result: null,
                        error: error.message
                    });
                }
            }
            
            // 4. 生成报告
            console.log('\n');
            console.log('=' .repeat(80));
            console.log('📊 测试报告');
            console.log('=' .repeat(80));
            
            const successful = results.filter(r => r.success);
            const failed = results.filter(r => !r.success);
            
            console.log(`✅ 成功: ${successful.length}`);
            console.log(`❌ 失败: ${failed.length}`);
            console.log('');
            
            if (successful.length > 0) {
                console.log('✅ 可用命令:');
                successful.forEach(r => {
                    console.log(`  - ${r.command}`);
                    if (r.result !== undefined) {
                        console.log(`    返回值: ${JSON.stringify(r.result)}`);
                    }
                });
                console.log('');
            }
            
            if (failed.length > 0) {
                console.log('❌ 不可用命令 (可能需要参数):');
                failed.forEach(r => {
                    console.log(`  - ${r.command}`);
                    console.log(`    错误: ${r.error}`);
                });
                console.log('');
            }
            
            console.log('=' .repeat(80));
            console.log('');
            
            // 5. 保存结果
            console.log('💾 结果已保存到变量 cursorCommandsTestResults');
            window.cursorCommandsTestResults = results;
            
            // 6. 提供复制功能
            console.log('💡 运行以下命令复制结果:');
            console.log('   copy(cursorCommandsTestResults)');
            console.log('');
            
            return results;
            
        } else {
            console.error('❌ 找不到 vscode 全局对象');
            console.log('💡 尝试其他方法...');
            
            // 方法 2: 查找可能的命令注册表
            console.log('\n🔍 搜索可能的 API 入口...');
            
            const possibleAPIs = [
                'window.vscode',
                'window._vscode',
                'window.require("vscode")',
                'window.acquireVsCodeApi',
                'window.parent.vscode'
            ];
            
            for (const api of possibleAPIs) {
                try {
                    const value = eval(api);
                    if (value) {
                        console.log(`✅ 找到: ${api}`);
                        console.log(value);
                    }
                } catch (e) {
                    console.log(`❌ ${api} - ${e.message}`);
                }
            }
        }
        
    } catch (error) {
        console.error('❌ 测试失败:', error);
        console.log('\n💡 可能的原因:');
        console.log('  1. DevTools 上下文不支持 vscode API');
        console.log('  2. 需要在扩展上下文中运行');
        console.log('  3. Cursor 版本不支持');
        console.log('\n💡 替代方案:');
        console.log('  - 创建一个简单的测试扩展');
        console.log('  - 使用扩展开发主机模式');
    }
})();
```

---

## 🎯 预期结果

### 情况 1: 如果成功 ✅

```
🔍 开始测试 Cursor 命令...

📋 Step 1: 获取所有命令...
✅ 找到 vscode 全局对象
✅ 总共 1234 个命令

================================================================================
📌 找到 15 个 Cursor 相关命令:
================================================================================
  - cursor.aichat
  - cursor.aisettings
  - cursor.backgroundcomposer
  - cursor.browserView.executeJavaScript
  - cursor.browserView.getConsoleLogs
  - cursor.browserView.navigate
  - cursor.composer
  - workbench.panel.aichat.view
  ...
================================================================================

🧪 Step 2: 测试每个命令...

测试: cursor.aichat...
  ✅ 成功! 返回值: undefined
  
测试: cursor.composer...
  ❌ 失败: command 'cursor.composer' not found

...

================================================================================
📊 测试报告
================================================================================
✅ 成功: 8
❌ 失败: 7

✅ 可用命令:
  - cursor.aichat
  - cursor.browserView.navigate
  ...

❌ 不可用命令 (可能需要参数):
  - cursor.composer (错误: requires argument 'prompt')
  ...
================================================================================
```

### 情况 2: 如果 vscode API 不可用 ❌

```
❌ 找不到 vscode 全局对象
💡 尝试其他方法...

🔍 搜索可能的 API 入口...
❌ window.vscode - undefined
❌ window._vscode - undefined
✅ 找到: window.acquireVsCodeApi
  [Function: acquireVsCodeApi]
```

---

## 🔬 替代测试方法

### 方法 1: 搜索全局命令对象

```javascript
// 在 DevTools Console 中运行

// 1. 搜索所有可能包含命令的对象
console.log('搜索命令注册表...');

// 遍历全局对象
for (let key in window) {
    if (key.toLowerCase().includes('command') || 
        key.toLowerCase().includes('vscode')) {
        console.log(`${key}:`, window[key]);
    }
}

// 2. 检查是否有 acquireVsCodeApi
if (window.acquireVsCodeApi) {
    const vscode = window.acquireVsCodeApi();
    console.log('VSCode API:', vscode);
}
```

### 方法 2: 监听命令执行

```javascript
// 尝试 Hook 命令执行

// 保存原始方法（如果存在）
if (window.vscode && window.vscode.commands) {
    const originalExecute = window.vscode.commands.executeCommand;
    
    window.vscode.commands.executeCommand = function(...args) {
        console.log('执行命令:', args[0], '参数:', args.slice(1));
        return originalExecute.apply(this, args);
    };
    
    console.log('✅ 已 Hook executeCommand');
    console.log('💡 现在执行任何 Cursor 操作，都会在 Console 中显示命令');
}
```

### 方法 3: 查看已打开的面板

```javascript
// 查找 AI 聊天面板的 DOM 元素

console.log('搜索 AI 聊天相关元素...');

const aiElements = document.querySelectorAll(
    '[class*="ai"], [class*="chat"], [class*="composer"], ' +
    '[data-testid*="ai"], [data-testid*="chat"]'
);

console.log(`找到 ${aiElements.length} 个 AI 相关元素:`);
aiElements.forEach((el, i) => {
    if (i < 10) {  // 只显示前 10 个
        console.log(`${i + 1}.`, el.className, el.id);
    }
});

// 尝试查找输入框
const textareas = document.querySelectorAll('textarea');
console.log(`\n找到 ${textareas.length} 个 textarea:`);
textareas.forEach((ta, i) => {
    console.log(`${i + 1}.`, {
        placeholder: ta.placeholder,
        value: ta.value?.substring(0, 50),
        visible: ta.offsetParent !== null,
        id: ta.id,
        className: ta.className
    });
});
```

---

## 🎯 如果 DevTools 方法不行

### 创建最小测试扩展（5 分钟）

```bash
# 1. 创建目录
mkdir test-cursor-commands
cd test-cursor-commands

# 2. 创建 package.json
cat > package.json << 'EOF'
{
  "name": "test-cursor-commands",
  "version": "0.0.1",
  "engines": {
    "vscode": "^1.74.0"
  },
  "activationEvents": ["onStartupFinished"],
  "main": "./extension.js",
  "contributes": {
    "commands": [
      {
        "command": "test.listCommands",
        "title": "Test: List All Cursor Commands"
      }
    ]
  }
}
EOF

# 3. 创建 extension.js
cat > extension.js << 'EOF'
const vscode = require('vscode');

function activate(context) {
    console.log('🧪 Test extension activated');
    
    // 立即测试
    testCursorCommands();
    
    // 注册命令
    context.subscriptions.push(
        vscode.commands.registerCommand('test.listCommands', testCursorCommands)
    );
}

async function testCursorCommands() {
    console.log('=' .repeat(80));
    console.log('🔍 Testing Cursor Commands');
    console.log('=' .repeat(80));
    
    try {
        // 获取所有命令
        const commands = await vscode.commands.getCommands(true);
        
        // 过滤 Cursor 相关
        const cursorCommands = commands.filter(cmd => 
            cmd.includes('cursor') || 
            cmd.includes('aichat') || 
            cmd.includes('composer')
        ).sort();
        
        console.log(`\n📋 Found ${cursorCommands.length} Cursor commands:`);
        cursorCommands.forEach(cmd => console.log(`  - ${cmd}`));
        
        console.log('\n🧪 Testing commands...\n');
        
        // 测试每个命令
        for (const cmd of cursorCommands) {
            try {
                const result = await vscode.commands.executeCommand(cmd);
                console.log(`✅ ${cmd}`);
                if (result !== undefined) {
                    console.log(`   返回: ${JSON.stringify(result)}`);
                }
            } catch (error) {
                console.log(`❌ ${cmd} - ${error.message}`);
            }
        }
        
        console.log('\n' + '=' .repeat(80));
        
        // 显示通知
        vscode.window.showInformationMessage(
            `Found ${cursorCommands.length} Cursor commands. Check console for details.`
        );
        
    } catch (error) {
        console.error('❌ Test failed:', error);
        vscode.window.showErrorMessage('Test failed: ' + error.message);
    }
}

module.exports = { activate };
EOF

# 4. 打包
npx vsce package --allow-missing-repository

# 5. 安装到 Cursor
# 在 Cursor 中: Extensions → Install from VSIX → 选择 test-cursor-commands-0.0.1.vsix
```

---

## 📊 期望得到的信息

### 关键问题

1. **`cursor.aichat` 是否存在？**
   - ✅ 如果存在 → 可以调用
   - ❌ 如果不存在 → 需要其他方法

2. **是否需要参数？**
   - 成功: 可以无参数调用
   - 失败 "requires parameter": 需要参数（需要猜测或反编译）

3. **返回值是什么？**
   - `undefined`: 只执行，不返回
   - `Promise`: 异步操作
   - `Object`: 可能包含有用信息

4. **其他可用命令**
   - `workbench.panel.aichat.view`: 打开 AI 面板
   - `cursor.browserView.*`: 浏览器相关

---

## 🎯 测试清单

### 必须测试的命令

```javascript
// 在 Console 或扩展中测试

const commandsToTest = [
    // AI 相关
    'cursor.aichat',
    'cursor.aisettings',
    'cursor.composer',
    'workbench.panel.aichat.view',
    
    // 浏览器视图
    'cursor.browserView.navigate',
    'cursor.browserView.executeJavaScript',
    'cursor.browserView.getConsoleLogs',
    
    // 其他
    'cursor.backgroundcomposer',
    'cursor.reviewchanges',
    'cursor.bugbot',
];

for (const cmd of commandsToTest) {
    try {
        const result = await vscode.commands.executeCommand(cmd);
        console.log(`✅ ${cmd} -> ${JSON.stringify(result)}`);
    } catch (error) {
        console.log(`❌ ${cmd} -> ${error.message}`);
    }
}
```

---

## 💡 根据测试结果决定方案

### 结果 1: `cursor.aichat` 可用 ✅

```typescript
// 扩展中可以直接调用
await vscode.commands.executeCommand('cursor.aichat', ...);

// 方案：直接控制
```

### 结果 2: `cursor.aichat` 需要参数 ⚠️

```typescript
// 需要猜测参数结构
await vscode.commands.executeCommand('cursor.aichat', {
    prompt: 'test',
    // ... 其他参数？
});

// 方案：试错法找出参数
```

### 结果 3: `cursor.aichat` 不可用 ❌

```typescript
// 使用间接方法
await vscode.env.clipboard.writeText(prompt);
await vscode.commands.executeCommand('workbench.panel.aichat.view');

// 方案：剪贴板 + 面板
```

---

## 🚀 立即行动

### 现在就试试！

1. **在 Cursor 中按 `Cmd+Shift+I`**
2. **切换到 Console 标签**
3. **粘贴上面的测试脚本**
4. **按 Enter**
5. **查看结果**

### 如果成功

把结果告诉我，我们就知道：
- ✅ 哪些命令可用
- ✅ 需要什么参数
- ✅ 最佳实施方案

### 如果失败

创建测试扩展（5 分钟），然后：
- ✅ 100% 可以测试
- ✅ 获得完整信息

---

## 📝 总结

**是的，DevTools 是最快的测试方法！**

- ⚡ 无需创建扩展
- ⚡ 立即测试
- ⚡ 快速验证

**如果 DevTools 中 `vscode` API 不可用**：
- 创建 5 分钟测试扩展
- 100% 能测试

**测试后我们就知道**：
- ✅ 哪些功能可用
- ✅ 如何调用
- ✅ 最佳实施方案

**现在就试试吧！** 🚀

