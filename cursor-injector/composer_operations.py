#!/usr/bin/env python3
"""
Cursor Composer 底层操作实现

包括：
1. 如何找到 DOM 对象
2. 如何发送提示词
3. 如何点击提交
4. 如何判断状态
"""

import asyncio
import websockets
import json
import time


class ComposerOperator:
    """Composer 操作器"""
    
    def __init__(self, ws_url='ws://localhost:9876'):
        self.ws_url = ws_url
        self.ws = None
        
        # DOM 选择器配置
        self.selectors = {
            'input': '.aislash-editor-input',
            'submit_button': 'button[type="submit"]',
            'thinking_indicators': [
                '.cursor-thinking',
                '.agent-working',
                '.thinking-indicator',
                '[data-status="thinking"]',
                '.loading',
                '.spinner'
            ],
            'stop_button': [
                '.stop-generation-button',
                '[aria-label="Stop generating"]',
                'button[aria-label*="stop" i]'
            ],
            'error_indicators': [
                '.error',
                '.agent-error',
                '[data-status="error"]'
            ]
        }
    
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
            return json.loads(response['result'])
        else:
            return {'error': response.get('error')}
    
    # ========== 1. 找到 DOM 对象 ==========
    
    async def find_input(self):
        """找到输入框"""
        code = f'''
        (function() {{
            const input = document.querySelector('{self.selectors["input"]}');
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
                className: input.className,
                isEmpty: (input.innerText || '').trim().length === 0,
                content: input.innerText || ''
            }});
        }})()
        '''
        
        result = await self.eval_in_renderer(code)
        return result
    
    async def find_submit_button(self):
        """找到提交按钮"""
        code = f'''
        (function() {{
            const button = document.querySelector('{self.selectors["submit_button"]}');
            if (!button) {{
                return JSON.stringify({{
                    success: false,
                    error: '提交按钮未找到'
                }});
            }}
            
            return JSON.stringify({{
                success: true,
                exists: true,
                disabled: button.disabled,
                text: button.innerText || button.textContent || ''
            }});
        }})()
        '''
        
        result = await self.eval_in_renderer(code)
        return result
    
    # ========== 2. 发送提示词 ==========
    
    async def input_text(self, text, clear_first=True):
        """输入文字到 Composer"""
        # 转义单引号和反斜杠
        escaped_text = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')
        
        code = f'''
        (function() {{
            const input = document.querySelector('{self.selectors["input"]}');
            if (!input) {{
                return JSON.stringify({{
                    success: false,
                    error: '输入框未找到'
                }});
            }}
            
            // 聚焦
            input.focus();
            
            // 清空（如果需要）
            if ({str(clear_first).lower()}) {{
                const sel = window.getSelection();
                const range = document.createRange();
                range.selectNodeContents(input);
                sel.removeAllRanges();
                sel.addRange(range);
                document.execCommand('delete', false, null);
            }}
            
            // 输入文字
            const success = document.execCommand('insertText', false, '{escaped_text}');
            
            if (!success) {{
                return JSON.stringify({{
                    success: false,
                    error: 'execCommand 执行失败'
                }});
            }}
            
            // 触发 input 事件
            input.dispatchEvent(new InputEvent('input', {{ 
                bubbles: true, 
                cancelable: true 
            }}));
            
            return JSON.stringify({{
                success: true,
                message: '文字输入成功',
                length: '{escaped_text}'.length
            }});
        }})()
        '''
        
        result = await self.eval_in_renderer(code)
        return result
    
    # ========== 3. 点击提交 ==========
    
    async def submit_by_enter(self):
        """通过 Enter 键提交"""
        code = f'''
        (function() {{
            const input = document.querySelector('{self.selectors["input"]}');
            if (!input) {{
                return JSON.stringify({{
                    success: false,
                    error: '输入框未找到'
                }});
            }}
            
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
            
            return JSON.stringify({{
                success: true,
                message: '已发送 Enter 键'
            }});
        }})()
        '''
        
        result = await self.eval_in_renderer(code)
        return result
    
    async def submit_by_button(self):
        """通过点击按钮提交"""
        code = f'''
        (function() {{
            const button = document.querySelector('{self.selectors["submit_button"]}');
            if (!button) {{
                return JSON.stringify({{
                    success: false,
                    error: '提交按钮未找到'
                }});
            }}
            
            if (button.disabled) {{
                return JSON.stringify({{
                    success: false,
                    error: '提交按钮被禁用'
                }});
            }}
            
            button.click();
            
            return JSON.stringify({{
                success: true,
                message: '已点击提交按钮'
            }});
        }})()
        '''
        
        result = await self.eval_in_renderer(code)
        return result
    
    # ========== 4. 判断状态 ==========
    
    async def is_agent_working(self):
        """判断 Agent 是否正在工作"""
        # 构建选择器数组的 JS 代码
        thinking_selectors_js = json.dumps(self.selectors['thinking_indicators'])
        stop_button_selectors_js = json.dumps(self.selectors['stop_button'])
        
        code = f'''
        (function() {{
            const thinkingSelectors = {thinking_selectors_js};
            const stopButtonSelectors = {stop_button_selectors_js};
            
            const result = {{
                isWorking: false,
                indicators: {{
                    thinking: false,
                    stopButton: false
                }},
                found: {{}}
            }};
            
            // 检查思考中指示器
            for (const selector of thinkingSelectors) {{
                const el = document.querySelector(selector);
                if (el && el.offsetParent !== null) {{  // 存在且可见
                    result.indicators.thinking = true;
                    result.found.thinking = {{
                        selector: selector,
                        className: el.className
                    }};
                    break;
                }}
            }}
            
            // 检查停止按钮
            for (const selector of stopButtonSelectors) {{
                const el = document.querySelector(selector);
                if (el && !el.disabled && el.offsetParent !== null) {{
                    result.indicators.stopButton = true;
                    result.found.stopButton = {{
                        selector: selector,
                        disabled: el.disabled
                    }};
                    break;
                }}
            }}
            
            // 只要有任何一个指示器表明正在工作，就认为正在工作
            result.isWorking = result.indicators.thinking || result.indicators.stopButton;
            
            return JSON.stringify(result);
        }})()
        '''
        
        result = await self.eval_in_renderer(code)
        return result
    
    async def check_error(self):
        """检查是否有错误"""
        error_selectors_js = json.dumps(self.selectors['error_indicators'])
        
        code = f'''
        (function() {{
            const errorSelectors = {error_selectors_js};
            
            const result = {{
                hasError: false,
                error: null
            }};
            
            for (const selector of errorSelectors) {{
                const el = document.querySelector(selector);
                if (el && el.offsetParent !== null) {{
                    result.hasError = true;
                    result.error = {{
                        selector: selector,
                        message: el.innerText || el.textContent || '',
                        className: el.className
                    }};
                    break;
                }}
            }}
            
            return JSON.stringify(result);
        }})()
        '''
        
        result = await self.eval_in_renderer(code)
        return result
    
    async def wait_for_completion(self, timeout=300, poll_interval=1):
        """等待 Agent 执行完成"""
        start_time = time.time()
        
        print(f'⏳ 等待 Agent 完成（最多 {timeout} 秒）...')
        
        while time.time() - start_time < timeout:
            # 检查是否正在工作
            status = await self.is_agent_working()
            
            if not status['isWorking']:
                # 不在工作了，再确认一次
                await asyncio.sleep(1)
                confirm = await self.is_agent_working()
                
                if not confirm['isWorking']:
                    elapsed = time.time() - start_time
                    print(f'✅ Agent 已完成（耗时 {elapsed:.1f} 秒）')
                    return {
                        'success': True,
                        'completed': True,
                        'elapsed': elapsed
                    }
            
            # 检查是否有错误
            error_check = await self.check_error()
            if error_check['hasError']:
                return {
                    'success': False,
                    'error': 'Agent 执行出错',
                    'details': error_check['error']
                }
            
            # 等待后重试
            await asyncio.sleep(poll_interval)
        
        # 超时
        return {
            'success': False,
            'error': f'等待超时（{timeout} 秒）'
        }
    
    # ========== 高层次组合操作 ==========
    
    async def execute_prompt(self, prompt, wait_for_completion=False, timeout=300):
        """执行提示词（完整流程）"""
        print('=' * 70)
        print('  🚀 执行提示词')
        print('=' * 70)
        print()
        print(f'提示词: "{prompt[:100]}{"..." if len(prompt) > 100 else ""}"')
        print(f'等待完成: {wait_for_completion}')
        print()
        
        # 步骤 1: 查找输入框
        print('步骤 1: 查找输入框...')
        input_result = await self.find_input()
        
        if not input_result['success']:
            print(f'❌ {input_result["error"]}')
            return input_result
        
        print('✅ 输入框已找到')
        print()
        
        # 步骤 2: 输入文字
        print('步骤 2: 输入文字...')
        input_text_result = await self.input_text(prompt, clear_first=True)
        
        if not input_text_result['success']:
            print(f'❌ {input_text_result["error"]}')
            return input_text_result
        
        print(f'✅ 文字输入成功（{input_text_result["length"]} 字符）')
        print()
        
        # 等待一下让 UI 更新
        await asyncio.sleep(0.5)
        
        # 步骤 3: 提交
        print('步骤 3: 提交（Enter 键）...')
        submit_result = await self.submit_by_enter()
        
        if not submit_result['success']:
            print(f'⚠️  Enter 键提交失败: {submit_result["error"]}')
            print('   尝试点击按钮...')
            
            submit_result = await self.submit_by_button()
            
            if not submit_result['success']:
                print(f'❌ 按钮提交也失败: {submit_result["error"]}')
                return submit_result
        
        print(f'✅ 已提交')
        print()
        
        if not wait_for_completion:
            print('✅ 提交成功（未等待完成）')
            return {
                'success': True,
                'phase': 'submitted',
                'message': '提示词已提交'
            }
        
        # 步骤 4: 等待完成
        print('步骤 4: 等待执行完成...')
        print()
        
        wait_result = await self.wait_for_completion(timeout)
        
        if wait_result['success']:
            print()
            print('=' * 70)
            print(f'  ✅ 执行完成（耗时 {wait_result["elapsed"]:.1f} 秒）')
            print('=' * 70)
        else:
            print()
            print('=' * 70)
            print(f'  ❌ 执行失败: {wait_result["error"]}')
            print('=' * 70)
        
        return wait_result


async def test_operations():
    """测试所有操作"""
    operator = ComposerOperator()
    await operator.connect()
    
    print('=' * 70)
    print('  🧪 测试 Composer 底层操作')
    print('=' * 70)
    print()
    
    # 测试 1: 查找输入框
    print('测试 1: 查找输入框')
    print('─' * 70)
    result = await operator.find_input()
    print(f'结果: {json.dumps(result, indent=2, ensure_ascii=False)}')
    print()
    
    # 测试 2: 查找提交按钮
    print('测试 2: 查找提交按钮')
    print('─' * 70)
    result = await operator.find_submit_button()
    print(f'结果: {json.dumps(result, indent=2, ensure_ascii=False)}')
    print()
    
    # 测试 3: 判断是否正在工作
    print('测试 3: 判断 Agent 是否正在工作')
    print('─' * 70)
    result = await operator.is_agent_working()
    print(f'结果: {json.dumps(result, indent=2, ensure_ascii=False)}')
    print()
    
    # 测试 4: 检查错误
    print('测试 4: 检查错误')
    print('─' * 70)
    result = await operator.check_error()
    print(f'结果: {json.dumps(result, indent=2, ensure_ascii=False)}')
    print()
    
    # 测试 5: 完整流程（不等待）
    print('测试 5: 执行提示词（不等待完成）')
    print('─' * 70)
    result = await operator.execute_prompt(
        prompt="写一个 Python 函数计算两个数的最大公约数",
        wait_for_completion=False
    )
    print()
    
    input('按回车继续下一个测试（等待完成）...')
    print()
    
    # 测试 6: 完整流程（等待完成）
    print('测试 6: 执行提示词（等待完成）')
    print('─' * 70)
    result = await operator.execute_prompt(
        prompt="解释一下什么是递归",
        wait_for_completion=True,
        timeout=60
    )
    print()


async def main():
    """主函数"""
    try:
        await test_operations()
    except KeyboardInterrupt:
        print('\n\n⚠️  测试被中断')
    except Exception as e:
        print(f'\n❌ 错误: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())

