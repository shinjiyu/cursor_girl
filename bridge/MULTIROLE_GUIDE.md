# 多角色客户端支持指南

## 概述

从 v2.0 开始，Ortensia 中央服务器支持**多角色客户端**。一个客户端可以同时拥有多个角色，例如同时作为 AITuber 和 Command Client。

## 功能特性

### ✅ 向后兼容

- 旧协议（单角色）依然完全支持
- 无需修改现有客户端代码

### 🆕 新功能

1. **多角色注册**：一个客户端可以拥有多个角色
2. **动态添加角色**：可以通过重复注册添加新角色
3. **角色查询**：服务器可以按角色查找客户端

## 协议说明

### 旧协议（单角色）

```json
{
  "type": "register",
  "from": "my-client-id",
  "to": "server",
  "timestamp": 1234567890,
  "payload": {
    "client_type": "aituber_client",  // ← 单个字符串
    "platform": "darwin",
    "pid": 12345
  }
}
```

### 新协议（多角色）

```json
{
  "type": "register",
  "from": "my-client-id",
  "to": "server",
  "timestamp": 1234567890,
  "payload": {
    "client_types": [  // ← 字符串数组
      "aituber_client",
      "command_client"
    ],
    "platform": "darwin",
    "pid": 12345
  }
}
```

## 可用角色类型

服务器识别以下角色：

| 角色 | 说明 |
|------|------|
| `cursor_inject` | Cursor 注入客户端（长连接） |
| `agent_hook` | Cursor Agent Hook（短连接） |
| `aituber_client` | AITuber 虚拟角色客户端 |
| `command_client` | 命令控制客户端 |

## 使用示例

### 示例 1：注册为 AITuber + Command Client

```python
import websockets
import json

async def register_multi_role():
    async with websockets.connect("ws://localhost:8765") as ws:
        register_msg = {
            "type": "register",
            "from": "my-awesome-client",
            "to": "server",
            "timestamp": int(time.time()),
            "payload": {
                "client_types": [
                    "aituber_client",
                    "command_client"
                ],
                "platform": "darwin",
                "pid": os.getpid()
            }
        }
        
        await ws.send(json.dumps(register_msg))
        response = await ws.recv()
        
        # 服务器会返回 multi_role: true
        result = json.loads(response)
        print(f"多角色支持: {result['payload']['server_info']['multi_role']}")
```

### 示例 2：动态添加角色

```python
# 第一次注册：只作为 AITuber
await ws.send(json.dumps({
    "type": "register",
    "from": "my-client",
    "payload": {
        "client_types": ["aituber_client"],
        ...
    }
}))

# 稍后添加 command_client 角色（使用相同的 client_id）
await ws.send(json.dumps({
    "type": "register",
    "from": "my-client",  # ← 相同的 ID
    "payload": {
        "client_types": ["command_client"],  # ← 新角色
        ...
    }
}))

# 现在 my-client 拥有两个角色：aituber_client + command_client
```

### 示例 3：查询特定角色的客户端（服务器端）

```python
# 在服务器代码中
from websocket_server import registry

# 查找所有 AITuber 客户端（可能同时还是 command_client）
aituber_clients = registry.get_by_type('aituber_client')

# 查找同时拥有两个角色的客户端
dual_clients = [
    c for c in registry.clients.values()
    if c.has_role('aituber_client') and c.has_role('command_client')
]
```

## 服务器 API

### ClientInfo 类

```python
class ClientInfo:
    client_types: set[str]  # 角色集合
    
    def add_role(self, role: str):
        """添加角色"""
        
    def remove_role(self, role: str):
        """移除角色"""
        
    def has_role(self, role: str) -> bool:
        """检查是否拥有某个角色"""
    
    @property
    def client_type(self) -> str:
        """向后兼容：返回主要角色"""
```

### ClientRegistry 类

```python
class ClientRegistry:
    def register(self, websocket, client_id: str, 
                 client_types: list, metadata: dict = None):
        """
        注册客户端（支持多角色）
        
        如果客户端已存在，添加新角色而不是覆盖
        """
    
    def get_by_type(self, client_type: str) -> list:
        """获取拥有指定角色的所有客户端"""
```

## 测试

运行测试脚本验证多角色功能：

```bash
cd bridge
python3 test_multirole.py
```

测试包括：
1. ✅ 单角色注册（旧协议兼容性）
2. ✅ 多角色注册（新协议）
3. ✅ 动态添加角色（重复注册）

## 服务器日志示例

```
[19:36:10] INFO: ✅ [test-single-role] 注册成功，角色: [aituber_client]
[19:36:11] INFO: ✅ [test-multi-role] 注册成功，角色: [aituber_client, command_client]
[19:36:13] INFO: 🔄 [test-add-role] 添加角色: ['command_client']
[19:36:13] INFO: ✅ [test-add-role] 注册成功，角色: [aituber_client, command_client]
```

## 迁移指南

### 从单角色迁移到多角色

**不需要任何修改！** 单角色协议依然完全支持。

如果想使用多角色功能，只需：

1. 将 `client_type` 改为 `client_types`
2. 将字符串改为数组

```diff
{
  "payload": {
-   "client_type": "aituber_client",
+   "client_types": ["aituber_client", "command_client"],
    ...
  }
}
```

## 使用场景

### 场景 1：统一客户端

一个应用同时充当 AITuber 和命令客户端：

```python
client_types = ["aituber_client", "command_client"]
```

- 可以接收来自 Hook 的事件通知（作为 aituber）
- 可以向 Cursor 发送命令（作为 command_client）

### 场景 2：功能升级

应用启动时只注册基础角色，根据用户操作动态添加角色：

```python
# 启动时
register(client_types=["aituber_client"])

# 用户启用远程控制后
register(client_types=["command_client"])  # 添加新角色
```

## 注意事项

1. **角色去重**：服务器会自动去除重复的角色
2. **角色持久**：一旦添加，角色会保持到客户端断开连接
3. **`unknown` 角色**：临时连接会自动获得 `unknown` 角色，注册后会添加真实角色

## 版本信息

- **引入版本**：v2.0
- **协议版本**：v1（向后兼容）
- **向后兼容**：✅ 完全兼容旧客户端

## 相关文件

- `bridge/websocket_server.py` - 服务器实现
- `bridge/protocol.py` - 协议定义
- `bridge/test_multirole.py` - 测试脚本
- `bridge/websocket_server_multirole.py` - 实现示例代码

