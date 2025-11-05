#!/usr/bin/env python3
"""
测试中央 Server 模式

连接到中央 Server，注册为 Command Client，发送命令到 Cursor Hook
"""

import asyncio
import websockets
import json
import uuid
from datetime import datetime


class CommandClient:
    def __init__(self, server_url='ws://localhost:8765'):
        self.server_url = server_url
        self.ws = None
        self.client_id = f"cmd-client-{uuid.uuid4().hex[:8]}"
        
    async def connect(self):
        """连接到中央 Server"""
        print(f'🔗 连接到中央 Server: {self.server_url}')
        self.ws = await websockets.connect(self.server_url)
        print('✅ 已连接\n')
        
    async def register(self):
        """注册为 Command Client"""
        print('📝 注册为 Command Client...')
        
        register_msg = {
            'type': 'register',
            'from': self.client_id,
            'to': 'server',
            'timestamp': int(datetime.now().timestamp()),
            'payload': {
                'client_type': 'command_client',
                'name': 'Test Command Client',
                'version': '1.0'
            }
        }
        
        await self.ws.send(json.dumps(register_msg))
        response = await self.ws.recv()
        result = json.loads(response)
        
        if result['type'] == 'register_ack':
            print(f'✅ 注册成功')
            print(f'   Client ID: {self.client_id}')
            print()
            return True
        else:
            print(f'❌ 注册失败: {result}')
            return False
    
    async def list_cursor_hooks(self):
        """列出所有 Cursor Hook"""
        print('📋 查询 Cursor Hook 列表...')
        
        # 这里需要向 Server 请求列表，但目前协议可能还没有这个功能
        # 我们可以假设有一个 cursor-xxxxx 的 ID
        # 或者直接尝试发送命令到广播地址
        
        print('   (当前协议需要知道 Cursor Hook ID)')
        print('   提示: 查看 Server 日志找到 Cursor Hook ID')
        print()
        
        cursor_id = input('请输入 Cursor Hook ID (或按回车使用测试): ').strip()
        
        if not cursor_id:
            # 等待一下看 Server 日志
            print('\n请查看 Server 终端，找到类似 "cursor-xxxxxxxx" 的 ID')
            print('然后输入该 ID：')
            cursor_id = input('Cursor Hook ID: ').strip()
        
        return cursor_id
    
    async def send_prompt(self, cursor_id, prompt):
        """发送提示词到 Cursor"""
        print(f'📤 发送提示词到 {cursor_id}...')
        print(f'   内容: "{prompt}"')
        print()
        
        agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        
        message = {
            'type': 'composer_send_prompt',
            'from': self.client_id,
            'to': cursor_id,
            'timestamp': int(datetime.now().timestamp()),
            'payload': {
                'agent_id': agent_id,
                'prompt': prompt
            }
        }
        
        await self.ws.send(json.dumps(message))
        print('✅ 命令已发送，等待响应...\n')
        
        # 等待响应
        try:
            response = await asyncio.wait_for(self.ws.recv(), timeout=10)
            result = json.loads(response)
            
            print('📬 收到响应:')
            print(f'   类型: {result["type"]}')
            print(f'   来自: {result.get("from")}')
            
            if result['type'] == 'composer_send_prompt_result':
                payload = result['payload']
                if payload['success']:
                    print(f'   ✅ 成功: {payload["message"]}')
                else:
                    print(f'   ❌ 失败: {payload["error"]}')
            
            print()
            return result
            
        except asyncio.TimeoutError:
            print('⚠️  10 秒内未收到响应')
            return None


async def main():
    print('=' * 70)
    print('  🌸 Ortensia 中央 Server 模式测试')
    print('=' * 70)
    print()
    
    client = CommandClient()
    
    try:
        # 1. 连接
        await client.connect()
        
        # 2. 注册
        if not await client.register():
            return
        
        # 3. 获取 Cursor Hook ID
        cursor_id = await client.list_cursor_hooks()
        
        if not cursor_id:
            print('❌ 未指定 Cursor Hook ID')
            return
        
        # 4. 发送测试命令
        print('─' * 70)
        print()
        
        test_prompt = "用 Python 实现冒泡排序算法"
        result = await client.send_prompt(cursor_id, test_prompt)
        
        if result and result['payload'].get('success'):
            print('✅ 测试成功！')
            print()
            print('说明:')
            print('  1. ✅ 中央 Server 正常运行')
            print('  2. ✅ Command Client 成功连接')
            print('  3. ✅ Cursor Hook 成功接收命令')
            print('  4. ✅ 命令执行成功')
        else:
            print('❌ 测试失败')
            if result:
                print(f'   错误: {result["payload"].get("error")}')
        
        print()
        print('=' * 70)
        
        # 保持连接
        print('\n按 Ctrl+C 退出...')
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print('\n\n⚠️  已断开连接')
    except Exception as e:
        print(f'\n❌ 错误: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())








