# 最终解决方案总结

## 🎯 你的场景

```
收到 hook 的 "complete" 事件
     ↓
 想给对应的 inject 发送新任务
     ↓
   如何找到它？
```

---

## ✅ 答案：环境变量

### inject 设置

```javascript
// inject 启动时
process.env.ORTENSIA_INJECT_ID = "inject-12345";
```

### hook 读取

```python
# hook 执行时
inject_id = os.getenv('ORTENSIA_INJECT_ID')

# 包含在消息中
payload["inject_id"] = inject_id
```

### server 查找

```python
# server 处理时
inject_id = message.payload["inject_id"]
inject_client = registry.get_by_id(inject_id)

# 发送新任务
await inject_client.websocket.send(task.to_json())
```

---

## 🎉 完美解决你指出的所有问题

| 问题 | 解决方案 |
|------|---------|
| ❌ inject 可以无 workspace 启动 | ✅ 不依赖 workspace |
| ❌ inject 可以切换 workspace | ✅ inject_id 不变 |
| ❌ workspace 映射会过期 | ✅ 直接通过 ID 查找 |

---

## 📊 三方术语

- **inject**: 注入到 Cursor 的服务（长连接）
- **hook**: Agent Hooks 脚本（短连接）
- **server**: Ortensia 中央服务器

---

## 📝 一行查找

```python
inject = registry.get_by_id(message.payload["inject_id"])
```

就这么简单！✅

---

**文档**: `INJECT_ID_SOLUTION.md` 查看完整说明

