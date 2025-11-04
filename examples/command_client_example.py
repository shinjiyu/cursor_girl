#!/usr/bin/env python3
"""
示例 Command Client

演示如何使用 Ortensia WebSocket 协议与中央Server通信，
控制 Cursor 执行 Composer 操作。

使用方法:
    1. 启动中央Server (python3 bridge/websocket_server.py)
    2. 启动 Cursor (设置 export ORTENSIA_SERVER=ws://localhost:8765)
    3. 运行此脚本 (python3 examples/command_client_example.py)
"""

import asyncio
import sys
import os

# 添加 bridge 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bridge'))

import websockets
from protocol import (
    Message,
    MessageBuilder,
    MessageType,
    ClientType,
    Platform,
    AgentStatus
)


class CommandClient:
    """示例 Command Client"""
    
    def __init__(self, server_url='ws://localhost:8765', client_id='cc-001'):
        self.server_url = server_url
        self.client_id = client_id
        self.ws = None
        self.cursor_instances = {}  # cursor_id -> info
        self.running = True
    
    async def connect(self):
        """连接到中央Server"""
        print(f'🔗 连接到中央Server: {self.server_url}')
        try:
            self.ws = await websockets.connect(self.server_url)
            print('✅ 已连接')
            return True
        except Exception as e:
            print(f'❌ 连接失败: {e}')
            return False
    
    async def register(self):
        """注册为 Command Client"""
        print(f'\n📝 注册为 Command Client (ID: {self.client_id})')
        
        msg = MessageBuilder.register(
            from_id=self.client_id,
            client_type=ClientType.COMMAND_CLIENT,
            platform=Platform.DARWIN,
            pid=os.getpid()
        )
        
        await self.ws.send(msg.to_json())
        print('✅ 注册消息已发送')
    
    async def listen(self):
        """监听来自Server的消息"""
        print('\n👂 开始监听消息...\n')
        
        try:
            async for message_str in self.ws:
                message = Message.from_json(message_str)
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print('\n🔌 连接已关闭')
        except Exception as e:
            print(f'\n❌ 监听错误: {e}')
    
    async def handle_message(self, message: Message):
        """处理接收到的消息"""
        msg_type = message.type
        
        print(f'📨 收到消息: {msg_type.value}')
        
        if msg_type == MessageType.REGISTER_ACK:
            await self.handle_register_ack(message)
        
        elif msg_type == MessageType.AGENT_STATUS_CHANGED:
            await self.handle_agent_status_changed(message)
        
        elif msg_type == MessageType.AGENT_COMPLETED:
            await self.handle_agent_completed(message)
        
        elif msg_type == MessageType.AGENT_ERROR:
            await self.handle_agent_error(message)
        
        elif msg_type == MessageType.COMPOSER_SEND_PROMPT_RESULT:
            await self.handle_composer_send_prompt_result(message)
        
        elif msg_type == MessageType.COMPOSER_STATUS_RESULT:
            await self.handle_composer_status_result(message)
        
        else:
            print(f'   ℹ️  未处理的消息类型')
    
    async def handle_register_ack(self, message: Message):
        """处理注册确认"""
        payload = message.payload
        
        if payload['success']:
            print(f'   ✅ 注册成功！')
            print(f'   🔑 分配ID: {payload["assigned_id"]}')
            
            # 注册成功后，开始自动化流程
            await asyncio.sleep(2)
            await self.start_automation()
        else:
            print(f'   ❌ 注册失败: {payload.get("error")}')
    
    async def handle_agent_status_changed(self, message: Message):
        """处理 Agent 状态变化事件"""
        payload = message.payload
        cursor_id = message.from_
        
        print(f'   📊 [{cursor_id}] Agent 状态变化:')
        print(f'      {payload["old_status"]} → {payload["new_status"]}')
        
        if payload.get('task_description'):
            print(f'      任务: {payload["task_description"]}')
        
        # 更新状态
        if cursor_id not in self.cursor_instances:
            self.cursor_instances[cursor_id] = {}
        
        self.cursor_instances[cursor_id]['status'] = payload['new_status']
    
    async def handle_agent_completed(self, message: Message):
        """处理 Agent 完成事件"""
        payload = message.payload
        cursor_id = message.from_
        
        print(f'   🎉 [{cursor_id}] Agent 任务完成！')
        print(f'      结果: {payload["result"]}')
        
        if payload.get('files_modified'):
            print(f'      修改的文件: {", ".join(payload["files_modified"])}')
        
        if payload.get('summary'):
            print(f'      总结: {payload["summary"]}')
        
        # 更新状态
        if cursor_id in self.cursor_instances:
            self.cursor_instances[cursor_id]['status'] = 'completed'
    
    async def handle_agent_error(self, message: Message):
        """处理 Agent 错误事件"""
        payload = message.payload
        cursor_id = message.from_
        
        print(f'   ❌ [{cursor_id}] Agent 错误！')
        print(f'      类型: {payload["error_type"]}')
        print(f'      消息: {payload["error_message"]}')
        print(f'      可重试: {payload["can_retry"]}')
    
    async def handle_composer_send_prompt_result(self, message: Message):
        """处理提示词发送结果"""
        payload = message.payload
        cursor_id = message.from_
        
        if payload['success']:
            print(f'   ✅ [{cursor_id}] 提示词已发送')
            print(f'      消息: {payload["message"]}')
        else:
            print(f'   ❌ [{cursor_id}] 提示词发送失败')
            print(f'      错误: {payload["error"]}')
    
    async def handle_composer_status_result(self, message: Message):
        """处理状态查询结果"""
        payload = message.payload
        cursor_id = message.from_
        
        if payload['success']:
            print(f'   📊 [{cursor_id}] Agent 状态: {payload["status"]}')
        else:
            print(f'   ❌ [{cursor_id}] 状态查询失败: {payload["error"]}')
    
    async def send_prompt(self, cursor_id: str, prompt: str):
        """发送提示词到指定 Cursor 实例"""
        print(f'\n💬 发送提示词到 {cursor_id}:')
        print(f'   "{prompt}"')
        
        msg = MessageBuilder.composer_send_prompt(
            from_id=self.client_id,
            to_id=cursor_id,
            agent_id='default',
            prompt=prompt
        )
        
        await self.ws.send(msg.to_json())
        print('   ✅ 已发送')
    
    async def query_status(self, cursor_id: str):
        """查询指定 Cursor 实例的 Agent 状态"""
        print(f'\n📊 查询 {cursor_id} 的 Agent 状态')
        
        msg = MessageBuilder.composer_query_status(
            from_id=self.client_id,
            to_id=cursor_id,
            agent_id='default'
        )
        
        await self.ws.send(msg.to_json())
        print('   ✅ 查询已发送')
    
    async def start_automation(self):
        """开始自动化流程（演示）"""
        print('\n' + '=' * 70)
        print('  🤖 开始自动化演示')
        print('=' * 70)
        
        # 等待 Cursor 实例注册
        print('\n⏳ 等待 Cursor 实例连接...')
        await asyncio.sleep(3)
        
        if not self.cursor_instances:
            print('⚠️  没有 Cursor 实例连接，演示结束')
            print('💡 请确保:')
            print('   1. Cursor 已启动')
            print('   2. 已设置 export ORTENSIA_SERVER=ws://localhost:8765')
            print('   3. 已重启 Cursor')
            return
        
        # 获取第一个 Cursor 实例
        cursor_id = list(self.cursor_instances.keys())[0]
        print(f'✅ 找到 Cursor 实例: {cursor_id}\n')
        
        # 演示 1: 发送提示词
        print('━' * 70)
        print('  演示 1: 发送提示词')
        print('━' * 70)
        
        await self.send_prompt(
            cursor_id,
            "写一个 Python 函数计算斐波那契数列的第 n 项"
        )
        
        await asyncio.sleep(2)
        
        # 演示 2: 查询状态
        print('\n━' * 70)
        print('  演示 2: 查询 Agent 状态')
        print('━' * 70)
        
        await self.query_status(cursor_id)
        
        await asyncio.sleep(2)
        
        # 演示 3: 再次发送提示词
        print('\n━' * 70)
        print('  演示 3: 发送第二个提示词')
        print('━' * 70)
        
        await self.send_prompt(
            cursor_id,
            "为上面的函数添加单元测试"
        )
        
        print('\n' + '=' * 70)
        print('  ✅ 演示完成！持续监听事件...')
        print('  💡 按 Ctrl+C 退出')
        print('=' * 70 + '\n')
    
    async def run(self):
        """运行 Command Client"""
        if not await self.connect():
            return
        
        await self.register()
        
        # 启动监听
        await self.listen()


async def main():
    """主函数"""
    
    print('=' * 70)
    print('  🎮 Ortensia Command Client 示例')
    print('=' * 70)
    print()
    print('此示例演示如何:')
    print('  1. 连接到中央Server')
    print('  2. 注册为 Command Client')
    print('  3. 监听事件通知')
    print('  4. 发送命令到 Cursor')
    print('  5. 接收并处理响应')
    print()
    print('=' * 70)
    print()
    
    # 检查中央Server地址
    server_url = os.getenv('ORTENSIA_SERVER', 'ws://localhost:8765')
    print(f'中央Server地址: {server_url}')
    print()
    
    # 创建并运行客户端
    client = CommandClient(server_url=server_url)
    
    try:
        await client.run()
    except KeyboardInterrupt:
        print('\n\n⚠️  用户中断')
    except Exception as e:
        print(f'\n\n❌ 错误: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())

