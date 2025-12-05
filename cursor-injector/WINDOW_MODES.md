# 窗口定位模式说明

## 三种支持的模式

### 1. 单播模式 - 指定窗口索引

直接指定窗口索引（0, 1, 2, ...）

```python
execute_msg = MessageBuilder.execute_js(
    from_id="server",
    to_id="inject-12345",
    code="console.log('Hello')",
    window_index=0  # 只在第一个窗口执行
)
```

**特点**：
- ✅ 最快，直接定位
- ❌ 窗口索引可能会变化

---

### 2. 单播模式 - conversation_id 查找

inject 自动查找匹配 conversation_id 的窗口

```python
execute_msg = MessageBuilder.execute_js(
    from_id="server",
    to_id="inject-12345",
    code="console.log('Hello')",
    conversation_id="abc123..."  # inject 自动查找匹配的窗口
)
```

**特点**：
- ✅ 可靠，不受窗口顺序变化影响
- ⚠️ 需要先查询所有窗口（稍慢）

---

### 3. 广播模式 + JS 代码内检查 ⭐ **当前使用**

不指定任何窗口参数，广播到所有窗口，在 JS 代码中检查 conversation_id

```python
# 生成包含 conversation_id 检查的 JS 代码
js_code = f"""
(async function() {{
    // 检查当前窗口的 conversation_id
    const expectedConvId = {json.dumps(conversation_id)};
    const convElement = document.querySelector('[id^="composer-bottom-add-context-"]');
    const currentConvId = convElement?.id.match(/composer-bottom-add-context-([a-f0-9-]+)/)?.[1];
    
    if (currentConvId !== expectedConvId) {{
        return {{ skipped: true }};  // 跳过不匹配的窗口
    }}
    
    // 只有匹配的窗口继续执行
    console.log('Hello from matched window');
}})()
"""

execute_msg = MessageBuilder.execute_js(
    from_id="server",
    to_id="inject-12345",
    code=js_code
    # 不指定 window_index 和 conversation_id，广播模式
)
```

**特点**：
- ✅ 逻辑在服务器端，易于维护
- ✅ inject 保持简单
- ✅ 可靠，不受窗口顺序变化影响
- ⚠️ 所有窗口都会执行代码（但不匹配的窗口直接返回）

---

## 为什么选择广播模式？

1. **Inject 保持简单**：不需要修改 inject 代码
2. **逻辑在服务器端**：便于调试和维护
3. **性能可接受**：虽然广播到所有窗口，但不匹配的窗口直接返回，实际开销很小
4. **可靠性高**：不依赖窗口索引，不受窗口顺序变化影响

---

## 何时使用其他模式？

- **window_index**：调试时指定特定窗口
- **conversation_id 单播**：如果性能要求极高，可以切换到单播模式
- **广播模式**：日常使用，最佳平衡







