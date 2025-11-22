#!/usr/bin/env python3
"""
示例：如何根据 hook 消息找到对应的 inject 并发送命令

场景：
1. 收到 hook 的 "complete" 事件（命令执行完成）
2. 认为这个 Cursor (inject) 现在空闲了
3. 想给它发送新任务

这个示例展示了整个流程。

术语说明：
- inject: 注入到 Cursor 的 WebSocket 服务（长连接）
- hook: Agent Hooks，由 Cursor 调用的脚本（短连接）
- server: Ortensia 中央服务器（消息路由）
"""

import asyncio
from protocol import Message, MessageType, MessageBuilder

# 假设这是从 websocket_server.py 导入的
# from websocket_server import registry, find_cursor_for_agent_hook


async def handle_hook_complete_event(message: Message):
    """
    处理 hook 的 complete 事件
    
    消息格式：
    {
        "type": "aituber_receive_text",
        "from": "hook-d42b-ed81",
        "to": "aituber",
        "timestamp": 1732253401001,
        "payload": {
            "text": "命令完成：git status",
            "emotion": "happy",
            "workspace": "/Users/user/Documents/project",
            "workspace_name": "project",
            "conversation_id": "2d8f9386...",
            "inject_id": "inject-12345"  # ← 关键！直接包含 inject ID
        }
    }
    """
    
    print("=" * 70)
    print("📨 收到 hook 消息")
    print("=" * 70)
    print(f"From: {message.from_}")
    print(f"Text: {message.payload.get('text')}")
    print(f"Inject ID: {message.payload.get('inject_id')}")
    print()
    
    # ============================================================
    # 步骤 1：从消息中提取 inject_id
    # ============================================================
    
    inject_id = message.payload.get('inject_id')
    
    if not inject_id:
        print("❌ 消息缺少 inject_id 字段")
        print("   这通常意味着 inject 未正确设置环境变量")
        return
    
    # ============================================================
    # 步骤 2：直接通过 inject_id 查找
    # ============================================================
    
    inject_client = registry.get_by_id(inject_id)
    
    if not inject_client:
        print(f"❌ inject 客户端不存在或已断开: {inject_id}")
        return
    
    print(f"✅ 找到对应的 inject: {inject_id}")
    print()
    
    # ============================================================
    # 步骤 3：发送新任务到这个 inject
    # ============================================================
    
    # 例如：发送一个 Agent 执行命令
    command_message = MessageBuilder.agent_execute_prompt(
        from_id="server",
        to_id=inject_id,  # ← 发送给找到的 inject
        agent_id="default",
        prompt="请分析当前项目的代码结构",
        options={
            "context": "当前项目",
            "task_type": "analysis"
        }
    )
    
    print(f"📤 发送任务到 inject: {inject_id}")
    print(f"   命令: agent_execute_prompt")
    print(f"   提示词: {command_message.payload.get('prompt')}")
    print()
    
    # 发送消息
    await inject_client.websocket.send(command_message.to_json())
    
    print("✅ 任务已发送")
    print("=" * 70)


# ============================================================================
# 实际使用示例
# ============================================================================

async def example_scenario():
    """完整场景示例"""
    
    print("\n" + "=" * 70)
    print("🎬 场景演示：hook Complete → 发送新任务")
    print("=" * 70)
    print()
    
    # 1. inject 启动并注册
    print("1️⃣  inject 启动并注册")
    print("-" * 70)
    print("Cursor 启动（PID: 12345）")
    print("inject 设置环境变量: ORTENSIA_INJECT_ID=inject-12345")
    print("inject 连接到 server")
    print("Client ID: inject-12345")
    print()
    
    # 2. hook 发送 complete 事件
    print("2️⃣  hook 发送 complete 事件")
    print("-" * 70)
    print("Cursor 执行命令后调用 hook")
    print("hook 读取环境变量: ORTENSIA_INJECT_ID=inject-12345")
    print("From: hook-d42b-ed81")
    print("inject_id: inject-12345  ← 关键！")
    print("Text: 命令完成：git status")
    print()
    
    # 构造 hook 消息（模拟）
    hook_message = Message(
        type=MessageType.AITUBER_RECEIVE_TEXT,
        from_="hook-d42b-ed81",
        to="aituber",
        timestamp=1732253401,
        payload={
            "text": "命令完成：git status",
            "emotion": "happy",
            "workspace": "/Users/user/Documents/project",
            "workspace_name": "project",
            "conversation_id": "2d8f9386...",
            "inject_id": "inject-12345"  # ← 直接包含 inject ID
        }
    )
    
    # 3. 查找对应的 inject 并发送新任务
    print("3️⃣  查找对应的 inject")
    print("-" * 70)
    print("inject_id: inject-12345")
    print("→ 直接查询 registry.get_by_id()")
    print("→ 找到: inject-12345 ✅")
    print()
    
    # await handle_hook_complete_event(hook_message)
    
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
    
    print("# 1. inject 设置环境变量（在 inject 启动时）")
    print("-" * 70)
    print("""
// inject 启动时设置环境变量
const injectId = `inject-${process.pid}`;
process.env.ORTENSIA_INJECT_ID = injectId;

// 这样所有子进程（包括 hook）都能读取到这个变量
    """)
    print()
    
    print("# 2. hook 读取环境变量并发送消息")
    print("-" * 70)
    print("""
# hook 从环境变量读取 inject ID
inject_id = os.getenv('ORTENSIA_INJECT_ID', '')

# 在消息 payload 中包含 inject_id
message = {
    "type": "aituber_receive_text",
    "from": "hook-xxx",
    "payload": {
        "text": "命令完成",
        "inject_id": inject_id  # ← 关键！
    }
}
    """)
    print()
    
    print("# 3. server 处理 hook 消息")
    print("-" * 70)
    print("""
async def handle_hook_message(message: Message):
    # 从消息中提取 inject_id
    inject_id = message.payload.get('inject_id')
    
    if not inject_id:
        logger.warning("消息缺少 inject_id")
        return
    
    # 直接通过 inject_id 查找
    inject_client = registry.get_by_id(inject_id)
    
    if inject_client:
        # 发送命令给这个 inject
        command = MessageBuilder.agent_execute_prompt(
            from_id="server",
            to_id=inject_id,  # ← 直接使用 inject_id
            agent_id="default",
            prompt="新任务"
        )
        
        await inject_client.websocket.send(command.to_json())
    """)
    print()


if __name__ == "__main__":
    print("\n🎯 这是一个示例文件，展示如何处理 hook → inject 的场景")
    print()
    print("术语说明：")
    print("  inject: 注入到 Cursor 的 WebSocket 服务（长连接）")
    print("  hook:   Agent Hooks，由 Cursor 调用的脚本（短连接）")
    print("  server: Ortensia 中央服务器（消息路由）")
    print()
    
    # 运行示例场景
    asyncio.run(example_scenario())
    
    # 显示快速参考
    quick_reference()

