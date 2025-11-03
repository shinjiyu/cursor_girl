#!/usr/bin/env python3
"""
Ortensia Cursor Client
连接到注入的 Cursor 并动态执行代码
"""

import asyncio
import json
import sys
import websockets


class OrtensiaCursorClient:
    def __init__(self, host='localhost', port=9876):
        self.uri = f'ws://{host}:{port}'
        self.ws = None
    
    async def connect(self):
        """连接到 Cursor"""
        print(f'🔗 连接到 Cursor ({self.uri})...')
        try:
            self.ws = await websockets.connect(self.uri)
            print('✅ 已连接')
            return True
        except Exception as e:
            print(f'❌ 连接失败: {e}')
            print('\n💡 请确认:')
            print('   1. Cursor 已启动')
            print('   2. Ortensia Injector 已安装')
            print('   3. 查看 Cursor DevTools Console 是否有错误')
            return False
    
    async def send(self, data):
        """发送数据并接收响应"""
        if not self.ws:
            raise Exception('未连接')
        
        # 发送
        await self.ws.send(json.dumps(data))
        
        # 接收
        response = await self.ws.recv()
        return json.loads(response)
    
    async def eval_code(self, code, context='main'):
        """执行 JavaScript 代码"""
        print(f'\n📤 执行代码 (context={context}):')
        print(f'   {code[:100]}...' if len(code) > 100 else f'   {code}')
        
        result = await self.send({
            'action': 'eval',
            'params': {
                'code': code,
                'context': context
            }
        })
        
        if result['success']:
            print('✅ 成功')
            if result.get('result') is not None:
                print(f'   返回值: {result["result"]}')
            return result['result']
        else:
            print(f'❌ 失败: {result["error"]}')
            return None
    
    async def eval_in_renderer(self, code):
        """在渲染进程中执行代码"""
        return await self.eval_code(code, context='renderer')
    
    async def ping(self):
        """测试连接"""
        print('\n🏓 Ping...')
        result = await self.send({'action': 'ping'})
        if result['success']:
            print(f'✅ Pong: {result["result"]}')
            return True
        return False
    
    async def get_version(self):
        """获取版本"""
        result = await self.send({'action': 'getVersion'})
        return result.get('result')
    
    async def get_vscode_commands(self):
        """获取所有 VSCode 命令"""
        print('\n📋 获取 VSCode 命令...')
        result = await self.send({
            'action': 'getVSCodeCommands',
            'params': {}
        })
        
        if result['success']:
            commands = result['result']
            cursor_commands = [c for c in commands if 'cursor' in c or 'ai' in c or 'chat' in c]
            
            print(f'✅ 找到 {len(commands)} 个命令')
            print(f'   其中 {len(cursor_commands)} 个 Cursor 相关命令:')
            for cmd in cursor_commands[:20]:
                print(f'      - {cmd}')
            
            if len(cursor_commands) > 20:
                print(f'      ... 还有 {len(cursor_commands) - 20} 个')
            
            return cursor_commands
        else:
            print(f'❌ 失败: {result["error"]}')
            return []
    
    async def execute_vscode_command(self, command, *args):
        """执行 VSCode 命令"""
        print(f'\n⚡ 执行命令: {command}')
        result = await self.send({
            'action': 'executeVSCodeCommand',
            'params': {
                'command': command,
                'args': args
            }
        })
        
        if result['success']:
            print('✅ 成功')
            return result.get('result')
        else:
            print(f'❌ 失败: {result["error"]}')
            return None
    
    async def close(self):
        """关闭连接"""
        if self.ws:
            await self.ws.close()
            print('\n👋 已断开连接')


# ============================================================================
# 示例用法
# ============================================================================

async def test_connection():
    """测试连接"""
    client = OrtensiaCursorClient()
    
    if not await client.connect():
        return
    
    try:
        # 1. Ping
        await client.ping()
        
        # 2. 获取版本
        version = await client.get_version()
        print(f'\n📦 Injector 版本: {version}')
        
        # 3. 在主进程执行代码
        await client.eval_code('console.log("Hello from Ortensia!")')
        
        # 4. 在渲染进程执行代码
        await client.eval_in_renderer('console.log("Hello from renderer!")')
        
        # 5. 获取所有命令
        commands = await client.get_vscode_commands()
        
        # 6. 测试执行命令
        # await client.execute_vscode_command('workbench.action.files.save')
        
    finally:
        await client.close()


async def interactive_mode():
    """交互模式"""
    client = OrtensiaCursorClient()
    
    if not await client.connect():
        return
    
    print('\n' + '=' * 80)
    print('  🎮 Ortensia Cursor - 交互模式')
    print('=' * 80)
    print('\n命令:')
    print('  ping                    - 测试连接')
    print('  version                 - 获取版本')
    print('  commands                - 列出所有命令')
    print('  eval <code>             - 在主进程执行代码')
    print('  evalr <code>            - 在渲染进程执行代码')
    print('  cmd <command> [args]    - 执行 VSCode 命令')
    print('  exit                    - 退出')
    print('')
    
    try:
        while True:
            try:
                line = input('> ').strip()
                
                if not line:
                    continue
                
                if line == 'exit':
                    break
                
                parts = line.split(' ', 1)
                command = parts[0]
                args = parts[1] if len(parts) > 1 else ''
                
                if command == 'ping':
                    await client.ping()
                
                elif command == 'version':
                    version = await client.get_version()
                    print(f'版本: {version}')
                
                elif command == 'commands':
                    await client.get_vscode_commands()
                
                elif command == 'eval':
                    if args:
                        result = await client.eval_code(args)
                        print(f'结果: {result}')
                    else:
                        print('用法: eval <code>')
                
                elif command == 'evalr':
                    if args:
                        result = await client.eval_in_renderer(args)
                        print(f'结果: {result}')
                    else:
                        print('用法: evalr <code>')
                
                elif command == 'cmd':
                    if args:
                        cmd_parts = args.split(' ')
                        cmd_name = cmd_parts[0]
                        cmd_args = cmd_parts[1:] if len(cmd_parts) > 1 else []
                        await client.execute_vscode_command(cmd_name, *cmd_args)
                    else:
                        print('用法: cmd <command> [args]')
                
                else:
                    print(f'未知命令: {command}')
                
            except KeyboardInterrupt:
                print('')
                break
            except Exception as e:
                print(f'❌ 错误: {e}')
    
    finally:
        await client.close()


# ============================================================================
# 主程序
# ============================================================================

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 命令行模式
        cmd = sys.argv[1]
        
        if cmd == 'ping':
            asyncio.run(test_connection())
        elif cmd == 'interactive' or cmd == 'i':
            asyncio.run(interactive_mode())
        else:
            print(f'未知命令: {cmd}')
            print('\n用法:')
            print('  python3 ortensia_cursor_client.py ping        - 测试连接')
            print('  python3 ortensia_cursor_client.py interactive - 交互模式')
    else:
        # 默认：交互模式
        asyncio.run(interactive_mode())
