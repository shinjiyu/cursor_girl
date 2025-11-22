#!/usr/bin/env python3
"""
示例：如何根据 Agent Hook 消息找到对应的 Cursor Hook 并发送命令

场景：
1. 收到 Agent Hook 的 "complete" 事件（命令执行完成）
2. 认为这个 Cursor 现在空闲了
3. 想给它发送新任务

这个示例展示了整个流程。
"""

import asyncio
from protocol import Message, MessageType, MessageBuilder

# 假设这是从 websocket_server.py 导入的
# from websocket_server import registry, find_cursor_for_agent_hook


async def handle_agent_complete_event(message: Message):
    """
    处理 Agent Hook 的 complete 事件
    
    消息格式：
    {
        "type": "aituber_receive_text",
        "from": "agent-hook-d42b-ed81",
        "to": "aituber",
        "timestamp": 1732253401001,
        "payload": {
            "text": "命令完成：git status",
            "emotion": "happy",
            "workspace": "/Users/user/Documents/project",
            "workspace_name": "project",
            "conversation_id": "2d8f9386...",
            "related_cursor_id": "cursor-d42b"  # 这个不准确
        }
    }
    """
    
    print("=" * 70)
    print("📨 收到 Agent Hook 消息")
    print("=" * 70)
    print(f"From: {message.from_}")
    print(f"Workspace: {message.payload.get('workspace')}")
    print(f"Text: {message.payload.get('text')}")
    print()
    
    # ============================================================
    # 步骤 1：根据 workspace 找到对应的 Cursor Hook
    # ============================================================
    
    workspace = message.payload.get('workspace')
    
    if not workspace:
        print("❌ 消息缺少 workspace 字段")
        return
    
    # 从注册表查询（假设 registry 已经维护了 workspace → cursor_id 映射）
    cursor_id = registry.get_cursor_by_workspace(workspace)
    
    if not cursor_id:
        print(f"❌ 未找到 workspace 对应的 Cursor: {workspace}")
        return
    
    cursor_client = registry.get_by_id(cursor_id)
    
    if not cursor_client:
        print(f"❌ Cursor 客户端已断开: {cursor_id}")
        return
    
    print(f"✅ 找到对应的 Cursor Hook: {cursor_id}")
    print()
    
    # ============================================================
    # 步骤 2：发送新任务到这个 Cursor
    # ============================================================
    
    # 例如：发送一个 Agent 执行命令
    command_message = MessageBuilder.agent_execute_prompt(
        from_id="server",
        to_id=cursor_id,  # ← 发送给找到的 Cursor Hook
        agent_id="default",
        prompt="请分析当前项目的代码结构",
        options={
            "context": "当前项目",
            "task_type": "analysis"
        }
    )
    
    print(f"📤 发送任务到 Cursor: {cursor_id}")
    print(f"   命令: agent_execute_prompt")
    print(f"   提示词: {command_message.payload.get('prompt')}")
    print()
    
    # 发送消息
    await cursor_client.websocket.send(command_message.to_json())
    
    print("✅ 任务已发送")
    print("=" * 70)


# ============================================================================
# 实际使用示例
# ============================================================================

async def example_scenario():
    """完整场景示例"""
    
    print("\n" + "=" * 70)
    print("🎬 场景演示：Agent Hook Complete → 发送新任务")
    print("=" * 70)
    print()
    
    # 1. Cursor Hook 注册（这会建立 workspace 映射）
    print("1️⃣  Cursor Hook 注册")
    print("-" * 70)
    print("Client ID: cursor-12345")
    print("Workspace: /Users/user/Documents/project")
    print("→ 服务器维护映射: workspace → cursor-12345")
    print()
    
    # 服务器端代码（在 handle_register 中）：
    # registry.register_cursor_workspace("cursor-12345", "/Users/user/Documents/project")
    
    # 2. Agent Hook 发送 complete 事件
    print("2️⃣  Agent Hook 发送 complete 事件")
    print("-" * 70)
    print("From: agent-hook-d42b-ed81")
    print("Workspace: /Users/user/Documents/project")
    print("Text: 命令完成：git status")
    print()
    
    # 构造 Agent Hook 消息（模拟）
    agent_message = Message(
        type=MessageType.AITUBER_RECEIVE_TEXT,
        from_="agent-hook-d42b-ed81",
        to="aituber",
        timestamp=1732253401,
        payload={
            "text": "命令完成：git status",
            "emotion": "happy",
            "workspace": "/Users/user/Documents/project",
            "workspace_name": "project",
            "conversation_id": "2d8f9386...",
            "related_cursor_id": "cursor-d42b"
        }
    )
    
    # 3. 查找对应的 Cursor 并发送新任务
    print("3️⃣  查找对应的 Cursor")
    print("-" * 70)
    print("workspace: /Users/user/Documents/project")
    print("→ 查询 registry.workspace_to_cursor")
    print("→ 找到: cursor-12345")
    print()
    
    # await handle_agent_complete_event(agent_message)
    
    print("✅ 完成！")
    print("=" * 70)
    print()


# ============================================================================
# 快速参考：服务器端代码片段
# ============================================================================

def quick_reference():
    """快速参考代码"""
    
    print("\n" + "=" * 70)
    print("📚 快速参考：服务器端代码")
    print("=" * 70)
    print()
    
    print("# 1. 当 Cursor Hook 注册时（在 handle_register 中）")
    print("-" * 70)
    print("""
if client_info.client_type == 'cursor_hook':
    workspace = payload.get('workspace')
    if workspace:
        registry.register_cursor_workspace(client_id, workspace)
        # 维护映射: workspace → cursor_id
    """)
    print()
    
    print("# 2. 当收到 Agent Hook 消息时")
    print("-" * 70)
    print("""
async def handle_agent_message(message: Message):
    # 从消息中提取 workspace
    workspace = message.payload.get('workspace')
    
    # 查找对应的 Cursor ID
    cursor_id = registry.get_cursor_by_workspace(workspace)
    
    if cursor_id:
        cursor_client = registry.get_by_id(cursor_id)
        
        # 现在可以发送命令给这个 Cursor
        command = MessageBuilder.agent_execute_prompt(
            from_id="server",
            to_id=cursor_id,
            agent_id="default",
            prompt="你的任务"
        )
        
        await cursor_client.websocket.send(command.to_json())
    """)
    print()
    
    print("# 3. ClientRegistry 的新方法")
    print("-" * 70)
    print("""
class ClientRegistry:
    def __init__(self):
        self.clients = {}
        self.ws_to_id = {}
        self.workspace_to_cursor = {}  # ← 新增
    
    def register_cursor_workspace(self, cursor_id, workspace):
        '''注册 Cursor 的 workspace 映射'''
        self.workspace_to_cursor[workspace] = cursor_id
    
    def get_cursor_by_workspace(self, workspace):
        '''根据 workspace 获取 Cursor ID'''
        return self.workspace_to_cursor.get(workspace)
    """)
    print()


if __name__ == "__main__":
    print("\n🎯 这是一个示例文件，展示如何处理 Agent Hook → Cursor Hook 的场景")
    print()
    
    # 运行示例场景
    asyncio.run(example_scenario())
    
    # 显示快速参考
    quick_reference()

