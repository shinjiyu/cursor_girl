# Cursor 控制底层实现指南

**目标**: 从底层开始，实现对 Cursor Composer 的完整控制

---

## 🎯 实现步骤

### 第一步：观察和分析（DOM 监控）

使用 `dom_monitor.py` 定时拉取 DOM 结构，观察不同状态下的变化。

#### 1.1 启动监控

```bash
cd cursor-injector

# 方式 1: 交互模式
python3 dom_monitor.py

# 方式 2: 自动模式（2秒间隔）
python3 dom_monitor.py --auto 2
```

#### 1.2 观察不同状态

**状态 1: 空闲（Idle）**
- 输入框为空
- 提交按钮可能禁用
- 没有思考中指示器
- 没有停止按钮

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⏰ 14:30:15 - Composer 状态快照
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 输入框:   
   内容: ""
   长度: 0
   为空: True

✅ 提交按钮: 🚫
   文本: "Submit"
   禁用: True

⚡ 思考中指示器: ❌ 未找到

❗ 错误: ❌ 无错误

🛑 停止按钮: ❌ 不可用
```

**状态 2: 输入中（Typing）**
- 输入框有内容
- 提交按钮可用
- 没有思考中指示器

```
✅ 输入框: 🎯
   内容: "写一个函数"
   长度: 6
   为空: False

✅ 提交按钮: ✅
   文本: "Submit"
   禁用: False
```

**状态 3: 执行中（Working）**
- 输入框可能清空或保留
- 出现思考中指示器 或 停止按钮可用

```
⚡ 思考中指示器: ✅ 找到
   选择器: .cursor-thinking
   可见: True

🛑 停止按钮: ✅ 可用
   选择器: .stop-generation-button
```

**状态 4: 完成（Completed）**
- 思考中指示器消失
- 停止按钮消失或禁用
- 输入框可用

#### 1.3 记录关键选择器

通过监控发现的关键选择器：

| 元素 | 选择器 | 用途 |
|------|--------|------|
| 输入框 | `.aislash-editor-input` | 输入提示词 |
| 提交按钮 | `button[type="submit"]` | 提交执行 |
| 思考中指示器 | `.cursor-thinking` 等 | 判断是否在执行 |
| 停止按钮 | `.stop-generation-button` | 判断是否在执行 + 停止 |
| 错误提示 | `.error` 等 | 检测错误 |

---

### 第二步：实现底层操作

使用 `composer_operations.py` 实现具体的 DOM 操作。

#### 2.1 测试所有操作

```bash
cd cursor-injector
python3 composer_operations.py
```

这会运行所有测试：
1. ✅ 查找输入框
2. ✅ 查找提交按钮
3. ✅ 判断是否正在工作
4. ✅ 检查错误
5. ✅ 执行提示词（不等待）
6. ✅ 执行提示词（等待完成）

#### 2.2 操作详解

##### 操作 1: 找到输入框

```python
async def find_input(self):
    """找到输入框"""
    code = f'''
    (function() {{
        const input = document.querySelector('.aislash-editor-input');
        if (!input) {{
            return JSON.stringify({{
                success: false,
                error: '输入框未找到'
            }});
        }}
        
        return JSON.stringify({{
            success: true,
            exists: true,
            tagName: input.tagName,
            isEmpty: (input.innerText || '').trim().length === 0,
            content: input.innerText || ''
        }});
    }})()
    '''
    
    result = await self.eval_in_renderer(code)
    return result
```

**关键点**:
- 使用 `document.querySelector()` 查找元素
- 检查 `innerText` 判断是否为空
- 返回详细信息用于调试

##### 操作 2: 输入文字

```python
async def input_text(self, text, clear_first=True):
    """输入文字到 Composer"""
    code = f'''
    (function() {{
        const input = document.querySelector('.aislash-editor-input');
        if (!input) {{
            return JSON.stringify({{
                success: false,
                error: '输入框未找到'
            }});
        }}
        
        // 聚焦
        input.focus();
        
        // 清空（如果需要）
        if (true) {{
            const sel = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(input);
            sel.removeAllRanges();
            sel.addRange(range);
            document.execCommand('delete', false, null);
        }}
        
        // 输入文字
        document.execCommand('insertText', false, '{text}');
        
        // 触发 input 事件
        input.dispatchEvent(new InputEvent('input', {{ 
            bubbles: true, 
            cancelable: true 
        }}));
        
        return JSON.stringify({{
            success: true,
            message: '文字输入成功'
        }});
    }})()
    '''
    
    result = await self.eval_in_renderer(code)
    return result
```

**关键点**:
- **先聚焦** - `input.focus()`
- **清空旧内容** - 选中全部 → delete
- **使用 execCommand** - 兼容 Lexical 编辑器
- **触发 input 事件** - 让编辑器知道内容变化

##### 操作 3: 提交（两种方式）

**方式 A: Enter 键**

```python
async def submit_by_enter(self):
    """通过 Enter 键提交"""
    code = f'''
    (function() {{
        const input = document.querySelector('.aislash-editor-input');
        input.focus();
        
        // 模拟按下 Enter 键
        const enterEvent = new KeyboardEvent('keydown', {{
            key: 'Enter',
            code: 'Enter',
            keyCode: 13,
            which: 13,
            bubbles: true,
            cancelable: true
        }});
        
        input.dispatchEvent(enterEvent);
        
        return JSON.stringify({{ success: true }});
    }})()
    '''
    
    result = await self.eval_in_renderer(code)
    return result
```

**方式 B: 点击按钮**

```python
async def submit_by_button(self):
    """通过点击按钮提交"""
    code = f'''
    (function() {{
        const button = document.querySelector('button[type="submit"]');
        if (!button || button.disabled) {{
            return JSON.stringify({{ 
                success: false,
                error: '按钮不可用'
            }});
        }}
        
        button.click();
        
        return JSON.stringify({{ success: true }});
    }})()
    '''
    
    result = await self.eval_in_renderer(code)
    return result
```

**推荐**: 优先使用 Enter 键，失败时尝试按钮

##### 操作 4: 判断状态（核心难点）

```python
async def is_agent_working(self):
    """判断 Agent 是否正在工作"""
    code = f'''
    (function() {{
        // 方法 1: 检查思考中指示器
        const thinkingSelectors = [
            '.cursor-thinking',
            '.agent-working',
            '.thinking-indicator',
            '[data-status="thinking"]',
            '.loading',
            '.spinner'
        ];
        
        let hasThinkingIndicator = false;
        for (const selector of thinkingSelectors) {{
            const el = document.querySelector(selector);
            if (el && el.offsetParent !== null) {{  // 存在且可见
                hasThinkingIndicator = true;
                break;
            }}
        }}
        
        // 方法 2: 检查停止按钮
        const stopButtonSelectors = [
            '.stop-generation-button',
            '[aria-label="Stop generating"]',
            'button[aria-label*="stop" i]'
        ];
        
        let hasStopButton = false;
        for (const selector of stopButtonSelectors) {{
            const el = document.querySelector(selector);
            if (el && !el.disabled && el.offsetParent !== null) {{
                hasStopButton = true;
                break;
            }}
        }}
        
        // 只要有任何一个指示器，就认为正在工作
        const isWorking = hasThinkingIndicator || hasStopButton;
        
        return JSON.stringify({{
            isWorking: isWorking,
            indicators: {{
                thinking: hasThinkingIndicator,
                stopButton: hasStopButton
            }}
        }});
    }})()
    '''
    
    result = await self.eval_in_renderer(code)
    return result
```

**判断逻辑**:
1. 检查多个可能的思考中指示器
2. 检查停止按钮是否可用
3. 只要有任何一个指示器 → 正在工作
4. 都没有 → 已完成/空闲

**注意**: 
- 使用 `el.offsetParent !== null` 判断是否可见
- 使用 `!el.disabled` 判断按钮是否可用

##### 操作 5: 等待完成

```python
async def wait_for_completion(self, timeout=300, poll_interval=1):
    """等待 Agent 执行完成"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # 检查是否正在工作
        status = await self.is_agent_working()
        
        if not status['isWorking']:
            # 不在工作了，再确认一次
            await asyncio.sleep(1)
            confirm = await self.is_agent_working()
            
            if not confirm['isWorking']:
                # 确认完成
                return {
                    'success': True,
                    'completed': True
                }
        
        # 等待后重试
        await asyncio.sleep(poll_interval)
    
    # 超时
    return {
        'success': False,
        'error': f'等待超时（{timeout} 秒）'
    }
```

**等待逻辑**:
1. 轮询检查 `is_agent_working()`
2. 如果不在工作 → 等待 1 秒再确认（避免误判）
3. 确认后返回成功
4. 超时后返回失败

---

### 第三步：组合成完整操作

```python
async def execute_prompt(self, prompt, wait_for_completion=False, timeout=300):
    """执行提示词（完整流程）"""
    
    # 步骤 1: 查找输入框
    input_result = await self.find_input()
    if not input_result['success']:
        return input_result
    
    # 步骤 2: 输入文字
    input_text_result = await self.input_text(prompt, clear_first=True)
    if not input_text_result['success']:
        return input_text_result
    
    # 等待 UI 更新
    await asyncio.sleep(0.5)
    
    # 步骤 3: 提交
    submit_result = await self.submit_by_enter()
    if not submit_result['success']:
        # 尝试点击按钮
        submit_result = await self.submit_by_button()
        if not submit_result['success']:
            return submit_result
    
    if not wait_for_completion:
        return {
            'success': True,
            'phase': 'submitted',
            'message': '提示词已提交'
        }
    
    # 步骤 4: 等待完成
    wait_result = await self.wait_for_completion(timeout)
    
    return wait_result
```

---

## 🐛 调试技巧

### 1. 使用 DOM 监控观察

```bash
# 在一个终端运行监控
python3 dom_monitor.py --auto 1

# 在另一个终端运行操作
python3 composer_operations.py
```

这样可以实时看到操作对 DOM 的影响。

### 2. 单步测试

在 `composer_operations.py` 中：

```python
# 只测试查找输入框
result = await operator.find_input()
print(json.dumps(result, indent=2))

# 只测试输入文字
result = await operator.input_text("测试")
print(json.dumps(result, indent=2))

# 只测试状态判断
result = await operator.is_agent_working()
print(json.dumps(result, indent=2))
```

### 3. 增加日志

在关键位置添加打印：

```python
print(f'📍 当前位置: 准备输入文字')
print(f'📝 内容: {text[:50]}...')

result = await self.input_text(text)

print(f'✅ 结果: {result}')
```

---

## ⚠️ 常见问题

### Q1: 输入框找不到

**原因**: 
- Cursor 未打开 AI 聊天面板
- 选择器不正确

**解决**:
1. 手动打开 Cursor AI 聊天
2. 使用 DOM 监控确认选择器
3. 尝试其他可能的选择器

### Q2: 文字输入后没有显示

**原因**:
- 没有聚焦
- 没有触发 input 事件
- Lexical 编辑器需要特殊处理

**解决**:
```javascript
// 确保这三步都执行
input.focus();                          // 1. 聚焦
document.execCommand('insertText', ...); // 2. 输入
input.dispatchEvent(new InputEvent(...)); // 3. 触发事件
```

### Q3: 无法判断是否在执行

**原因**:
- 选择器不正确
- Cursor UI 更新了

**解决**:
1. 使用 DOM 监控，在执行时观察 DOM
2. 找到新的指示器选择器
3. 更新 `selectors` 配置

### Q4: 等待完成时误判

**原因**:
- UI 更新有延迟
- 指示器闪烁

**解决**:
```python
# 二次确认
if not status['isWorking']:
    await asyncio.sleep(1)  # 等待 1 秒
    confirm = await self.is_agent_working()
    if not confirm['isWorking']:
        # 确认完成
```

---

## 📊 实现状态

| 功能 | 状态 | 文件 |
|------|------|------|
| DOM 监控 | ✅ | `dom_monitor.py` |
| 查找输入框 | ✅ | `composer_operations.py` |
| 输入文字 | ✅ | `composer_operations.py` |
| 提交执行 | ✅ | `composer_operations.py` |
| 判断状态 | ✅ | `composer_operations.py` |
| 等待完成 | ✅ | `composer_operations.py` |
| 完整流程 | ✅ | `composer_operations.py` |

---

## 🚀 下一步

1. **验证和测试**
   - 在实际 Cursor 中运行测试
   - 根据监控结果调整选择器
   - 优化状态判断逻辑

2. **集成到协议**
   - 将 `composer_operations.py` 的逻辑集成到 V9
   - 支持通过 WebSocket 协议调用
   - 实现完整的端到端流程

3. **扩展功能**
   - 停止执行
   - 获取输出
   - 错误处理优化

---

*最后更新: 2025-11-03*

