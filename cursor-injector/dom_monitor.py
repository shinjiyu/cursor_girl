#!/usr/bin/env python3
"""
Cursor DOM 监控工具

定时拉取 Cursor 的 DOM 结构，观察变化和状态
用于分析和调试 Cursor UI 的 DOM 特征
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime
import os


class DOMMonitor:
    """DOM 监控器"""
    
    def __init__(self, ws_url='ws://localhost:9876'):
        self.ws_url = ws_url
        self.ws = None
        self.monitoring = False
        self.interval = 2  # 默认 2 秒拉取一次
    
    async def connect(self):
        """连接到 Cursor Hook"""
        print(f'🔗 连接到 Cursor Hook: {self.ws_url}')
        self.ws = await websockets.connect(self.ws_url)
        print('✅ 已连接\n')
    
    async def eval_in_renderer(self, code):
        """在渲染进程执行代码"""
        eval_code = f'''
        (async () => {{
            const {{ BrowserWindow }} = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {{
                const code = `{code}`;
                return await windows[0].webContents.executeJavaScript(code);
            }}
            return JSON.stringify({{ error: "没有窗口" }});
        }})()
        '''
        
        await self.ws.send(eval_code)
        response_str = await self.ws.recv()
        response = json.loads(response_str)
        
        if response['success']:
            return response['result']
        else:
            return json.dumps({'error': response.get('error')})
    
    async def get_composer_snapshot(self):
        """获取 Composer 区域的 DOM 快照"""
        code = '''
        (function() {
            const snapshot = {
                timestamp: Date.now(),
                input: null,
                submit: null,
                status: null,
                thinking: null,
                error: null
            };
            
            // 1. 输入框
            const input = document.querySelector('.aislash-editor-input');
            if (input) {
                snapshot.input = {
                    exists: true,
                    innerText: input.innerText || '',
                    textContent: input.textContent || '',
                    length: (input.innerText || '').length,
                    isEmpty: (input.innerText || '').trim().length === 0,
                    isFocused: document.activeElement === input,
                    className: input.className,
                    tagName: input.tagName
                };
            } else {
                snapshot.input = { exists: false };
            }
            
            // 2. 提交按钮
            const submit = document.querySelector('button[type="submit"]');
            if (submit) {
                snapshot.submit = {
                    exists: true,
                    disabled: submit.disabled,
                    className: submit.className,
                    innerText: submit.innerText || submit.textContent || '',
                    ariaLabel: submit.getAttribute('aria-label')
                };
            } else {
                snapshot.submit = { exists: false };
            }
            
            // 3. 状态指示器（尝试多种选择器）
            const statusSelectors = [
                '.composer-status',
                '.agent-status',
                '[data-status]',
                '.status-indicator'
            ];
            
            for (const selector of statusSelectors) {
                const el = document.querySelector(selector);
                if (el) {
                    snapshot.status = {
                        exists: true,
                        selector: selector,
                        className: el.className,
                        innerText: el.innerText || '',
                        dataStatus: el.getAttribute('data-status'),
                        ariaLabel: el.getAttribute('aria-label')
                    };
                    break;
                }
            }
            if (!snapshot.status) {
                snapshot.status = { exists: false };
            }
            
            // 4. 思考中指示器
            const thinkingSelectors = [
                '.cursor-thinking',
                '.agent-working',
                '.thinking-indicator',
                '[data-status="thinking"]',
                '[aria-label*="thinking"]',
                '.loading',
                '.spinner'
            ];
            
            for (const selector of thinkingSelectors) {
                const el = document.querySelector(selector);
                if (el) {
                    snapshot.thinking = {
                        exists: true,
                        selector: selector,
                        className: el.className,
                        visible: el.offsetParent !== null
                    };
                    break;
                }
            }
            if (!snapshot.thinking) {
                snapshot.thinking = { exists: false };
            }
            
            // 5. 错误指示器
            const errorSelectors = [
                '.error',
                '.agent-error',
                '[data-status="error"]',
                '.error-message'
            ];
            
            for (const selector of errorSelectors) {
                const el = document.querySelector(selector);
                if (el) {
                    snapshot.error = {
                        exists: true,
                        selector: selector,
                        className: el.className,
                        message: el.innerText || el.textContent || ''
                    };
                    break;
                }
            }
            if (!snapshot.error) {
                snapshot.error = { exists: false };
            }
            
            // 6. 额外信息 - 查找所有可能相关的元素
            snapshot.extra = {
                composerContainer: !!document.querySelector('.composer'),
                aiPanel: !!document.querySelector('.ai-panel'),
                chatPanel: !!document.querySelector('.chat-panel'),
                stopButton: null
            };
            
            // 停止按钮
            const stopBtnSelectors = [
                '.stop-generation-button',
                '[aria-label="Stop generating"]',
                'button[aria-label*="stop" i]',
                'button[aria-label*="cancel" i]'
            ];
            
            for (const selector of stopBtnSelectors) {
                const el = document.querySelector(selector);
                if (el && !el.disabled) {
                    snapshot.extra.stopButton = {
                        exists: true,
                        selector: selector,
                        disabled: el.disabled,
                        visible: el.offsetParent !== null
                    };
                    break;
                }
            }
            
            return JSON.stringify(snapshot, null, 2);
        })()
        '''
        
        result_str = await self.eval_in_renderer(code)
        return json.loads(result_str)
    
    def print_snapshot(self, snapshot):
        """打印快照"""
        now = datetime.now().strftime('%H:%M:%S')
        
        print('━' * 70)
        print(f'  ⏰ {now} - Composer 状态快照')
        print('━' * 70)
        
        # 输入框
        if snapshot['input']['exists']:
            inp = snapshot['input']
            status = '✅' if inp['exists'] else '❌'
            focus = '🎯' if inp['isFocused'] else '  '
            print(f'{status} 输入框: {focus}')
            print(f'   内容: "{inp["innerText"][:50]}{"..." if inp["length"] > 50 else ""}"')
            print(f'   长度: {inp["length"]}')
            print(f'   为空: {inp["isEmpty"]}')
        else:
            print('❌ 输入框: 未找到')
        
        print()
        
        # 提交按钮
        if snapshot['submit']['exists']:
            sub = snapshot['submit']
            status = '✅' if sub['exists'] else '❌'
            disabled = '🚫' if sub['disabled'] else '✅'
            print(f'{status} 提交按钮: {disabled}')
            print(f'   文本: "{sub["innerText"]}"')
            print(f'   禁用: {sub["disabled"]}')
        else:
            print('❌ 提交按钮: 未找到')
        
        print()
        
        # 思考中指示器
        if snapshot['thinking']['exists']:
            print(f'⚡ 思考中指示器: ✅ 找到')
            print(f'   选择器: {snapshot["thinking"]["selector"]}')
            print(f'   可见: {snapshot["thinking"]["visible"]}')
        else:
            print(f'⚡ 思考中指示器: ❌ 未找到')
        
        print()
        
        # 错误
        if snapshot['error']['exists']:
            print(f'❗ 错误: ✅ 有错误')
            print(f'   消息: {snapshot["error"]["message"]}')
        else:
            print(f'❗ 错误: ❌ 无错误')
        
        print()
        
        # 停止按钮
        if snapshot['extra']['stopButton']:
            print(f'🛑 停止按钮: ✅ 可用')
            print(f'   选择器: {snapshot["extra"]["stopButton"]["selector"]}')
        else:
            print(f'🛑 停止按钮: ❌ 不可用')
        
        print()
    
    async def monitor_loop(self):
        """监控循环"""
        print('=' * 70)
        print('  🔍 Cursor DOM 监控器')
        print('=' * 70)
        print()
        print(f'监控间隔: {self.interval} 秒')
        print('按 Ctrl+C 停止监控')
        print()
        
        try:
            while self.monitoring:
                try:
                    snapshot = await self.get_composer_snapshot()
                    self.print_snapshot(snapshot)
                    
                    # 等待下一次
                    await asyncio.sleep(self.interval)
                    
                except Exception as e:
                    print(f'❌ 获取快照失败: {e}')
                    await asyncio.sleep(self.interval)
        
        except asyncio.CancelledError:
            print('\n🛑 监控已停止')
    
    async def start_monitoring(self, interval=2):
        """开始监控"""
        self.interval = interval
        self.monitoring = True
        
        await self.connect()
        await self.monitor_loop()
    
    async def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.ws:
            await self.ws.close()


async def interactive_mode():
    """交互模式"""
    print('=' * 70)
    print('  🎮 Cursor DOM 监控工具 - 交互模式')
    print('=' * 70)
    print()
    
    monitor = DOMMonitor()
    await monitor.connect()
    
    print('可用命令:')
    print('  1 - 获取一次快照')
    print('  2 - 开始持续监控（2秒间隔）')
    print('  3 - 开始持续监控（5秒间隔）')
    print('  4 - 开始持续监控（10秒间隔）')
    print('  q - 退出')
    print()
    
    monitoring_task = None
    
    try:
        while True:
            cmd = input('请输入命令: ').strip()
            
            if cmd == 'q':
                break
            
            elif cmd == '1':
                print()
                snapshot = await monitor.get_composer_snapshot()
                monitor.print_snapshot(snapshot)
            
            elif cmd in ['2', '3', '4']:
                if monitoring_task:
                    print('⚠️  已在监控中，先停止...')
                    monitor.monitoring = False
                    monitoring_task.cancel()
                    try:
                        await monitoring_task
                    except:
                        pass
                
                interval = {
                    '2': 2,
                    '3': 5,
                    '4': 10
                }[cmd]
                
                print(f'\n🔄 开始监控（间隔 {interval} 秒）...')
                print('按 Ctrl+C 停止\n')
                
                monitor.monitoring = True
                monitor.interval = interval
                monitoring_task = asyncio.create_task(monitor.monitor_loop())
            
            else:
                print('❌ 未知命令')
    
    except KeyboardInterrupt:
        print('\n\n⚠️  用户中断')
    
    finally:
        if monitoring_task:
            monitoring_task.cancel()
            try:
                await monitoring_task
            except:
                pass
        
        await monitor.stop_monitoring()


async def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        # 自动模式：直接开始持续监控
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        
        monitor = DOMMonitor()
        try:
            await monitor.start_monitoring(interval)
        except KeyboardInterrupt:
            print('\n⚠️  监控已停止')
    else:
        # 交互模式
        await interactive_mode()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n👋 再见！')
        sys.exit(0)

