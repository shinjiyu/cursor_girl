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
        
        # DOM 选择器配置（基于实际验证）
        self.selectors = {
            'input': '.aislash-editor-input',
            'submit_button': '.send-with-mode > .anysphere-icon-button',  # ✅ 必须点击子元素！
            'submit_button_parent': '.send-with-mode',  # 父元素（用于查找）
            'submit_icon': '.codicon-arrow-up-two',  # SPAN 图标
            'editor_tab': '.segmented-tab',  # Editor tab 切换
            'thinking_indicators': [
                '[class*="loading" i]',  # ✅ 实际验证有效
                '.cursor-thinking',
                '.agent-working',
                '.thinking-indicator',
                '[data-status="thinking"]',
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
    
    # ========== 0. 确保 UI 就绪 ==========
    
    async def ensure_editor_tab(self):
        """确保在 Editor tab（不是 Agents tab）"""
        code = f'''
        (function() {{
            // 查找所有标签
            const tabs = document.querySelectorAll('{self.selectors["editor_tab"]}');
            
            if (tabs.length === 0) {{
                return JSON.stringify({{
                    success: false,
                    error: '未找到标签'
                }});
            }}
            
            // 查找 Editor 标签（通过文本识别）
            let editorTab = null;
            for (const tab of tabs) {{
                const text = (tab.innerText || tab.textContent || '').toLowerCase();
                if (text.includes('editor')) {{
                    editorTab = tab;
                    break;
                }}
            }}
            
            if (!editorTab) {{
                return JSON.stringify({{
                    success: false,
                    error: '未找到 Editor 标签'
                }});
            }}
            
            // 检查是否已经激活
            const isActive = editorTab.classList.contains('active') || 
                           editorTab.getAttribute('aria-selected') === 'true';
            
            if (!isActive) {{
                // 点击切换到 Editor
                editorTab.click();
                return JSON.stringify({{
                    success: true,
                    switched: true,
                    message: '已切换到 Editor tab'
                }});
            }}
            
            return JSON.stringify({{
                success: true,
                switched: false,
                message: '已经在 Editor tab'
            }});
        }})()
        '''
        
        result = await self.eval_in_renderer(code)
        return result
    
    async def invoke_composer(self):
        """使用 Cmd+I 唤出 Composer"""
        code = '''
        (function() {
            // 模拟 Cmd+I（Mac）或 Ctrl+I（Windows）
            const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
            
            const event = new KeyboardEvent('keydown', {
                key: 'i',
                code: 'KeyI',
                keyCode: 73,
                which: 73,
                metaKey: isMac,      // Mac 使用 Cmd
                ctrlKey: !isMac,     // Windows 使用 Ctrl
                bubbles: true,
                cancelable: true
            });
            
            document.dispatchEvent(event);
            
            return JSON.stringify({
                success: true,
                message: 'Cmd+I 已发送'
            });
        })()
        '''
        
        result = await self.eval_in_renderer(code)
        return result
    
    async def ensure_composer_ready(self):
        """确保 Composer 已就绪（在 Editor tab 且可见）"""
        print('  📍 确保 Composer 就绪...')
        
        # 1. 确保在 Editor tab
        tab_result = await self.ensure_editor_tab()
        if not tab_result['success']:
            return tab_result
        
        if tab_result.get('switched'):
            print('  ✅ 已切换到 Editor tab')
            await asyncio.sleep(0.5)  # 等待 UI 更新
        else:
            print('  ✅ 已在 Editor tab')
        
        # 2. 检查输入框是否存在
        input_result = await self.find_input()
        
        if not input_result['success']:
            # 输入框不存在，尝试用 Cmd+I 唤出
            print('  📢 输入框不可见，尝试 Cmd+I 唤出...')
            
            invoke_result = await self.invoke_composer()
            if not invoke_result['success']:
                return invoke_result
            
            print('  ✅ Cmd+I 已发送')
            await asyncio.sleep(1)  # 等待 Composer 出现
            
            # 再次检查
            input_result = await self.find_input()
            if not input_result['success']:
                return {
                    'success': False,
                    'error': 'Cmd+I 后输入框仍未出现'
                }
        
        print('  ✅ Composer 已就绪')
        return {'success': True}
    
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
        """找到提交按钮（上箭头按钮）"""
        code = f'''
        (function() {{
            const button = document.querySelector('{self.selectors["submit_button"]}');
            if (!button) {{
                return JSON.stringify({{
                    success: false,
                    error: '提交按钮未找到'
                }});
            }}
            
            // 检查可见性
            const isVisible = button.offsetParent !== null;
            
            return JSON.stringify({{
                success: true,
                exists: true,
                visible: isVisible,
                className: button.className,
                tagName: button.tagName
            }});
        }})()
        '''
        
        result = await self.eval_in_renderer(code)
        return result
    
    async def wait_for_submit_button(self, timeout=10):
        """等待提交按钮出现（输入后才会出现）"""
        start_time = time.time()
        attempts = 0
        
        print(f'  ⏱️  等待按钮出现（最多 {timeout} 秒）...')
        
        while time.time() - start_time < timeout:
            attempts += 1
            result = await self.find_submit_button()
            
            if result['success'] and result.get('visible'):
                elapsed = time.time() - start_time
                print(f'  ✅ 按钮已出现（耗时 {elapsed:.1f} 秒，尝试 {attempts} 次）')
                return result
            
            if attempts % 5 == 0:  # 每 1 秒打印一次
                print(f'  ⏳ 等待中... ({attempts * 0.2:.1f}s)')
            
            await asyncio.sleep(0.2)
        
        return {
            'success': False,
            'error': f'提交按钮未在 {timeout} 秒内出现（尝试了 {attempts} 次）'
        }
    
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
    
    async def submit_by_button(self, wait_for_button=True):
        """通过点击上箭头按钮提交"""
        # 如果需要，等待按钮出现
        if wait_for_button:
            wait_result = await self.wait_for_submit_button(timeout=5)
            if not wait_result['success']:
                return wait_result
        
        code = f'''
        (function() {{
            const button = document.querySelector('{self.selectors["submit_button"]}');
            if (!button) {{
                return JSON.stringify({{
                    success: false,
                    error: '提交按钮未找到'
                }});
            }}
            
            // 检查可见性
            if (button.offsetParent === null) {{
                return JSON.stringify({{
                    success: false,
                    error: '提交按钮不可见'
                }});
            }}
            
            // 点击按钮
            button.click();
            
            return JSON.stringify({{
                success: true,
                message: '已点击上箭头按钮'
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
            
            # 检查返回结果是否有效
            if not isinstance(status, dict) or 'isWorking' not in status:
                print(f'⚠️  状态检测返回异常: {status}')
                await asyncio.sleep(poll_interval)
                continue
            
            if not status['isWorking']:
                # 不在工作了，再确认一次
                await asyncio.sleep(1)
                confirm = await self.is_agent_working()
                
                if isinstance(confirm, dict) and 'isWorking' in confirm and not confirm['isWorking']:
                    elapsed = time.time() - start_time
                    print(f'✅ Agent 已完成（耗时 {elapsed:.1f} 秒）')
                    return {
                        'success': True,
                        'completed': True,
                        'elapsed': elapsed
                    }
            
            # 检查是否有错误
            error_check = await self.check_error()
            if isinstance(error_check, dict) and error_check.get('hasError'):
                return {
                    'success': False,
                    'error': 'Agent 执行出错',
                    'details': error_check.get('error')
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
        
        # 步骤 0: 确保 Composer 就绪
        print('步骤 0: 确保 Composer 就绪...')
        ready_result = await self.ensure_composer_ready()
        
        if not ready_result['success']:
            print(f'❌ {ready_result["error"]}')
            return ready_result
        
        print()
        
        # 步骤 1: 输入文字
        print('步骤 1: 输入文字...')
        input_text_result = await self.input_text(prompt, clear_first=True)
        
        if not input_text_result['success']:
            print(f'❌ {input_text_result["error"]}')
            return input_text_result
        
        print(f'✅ 文字输入成功（{input_text_result["length"]} 字符）')
        print()
        
        # 等待 UI 更新（输入后上箭头按钮才会出现）
        print('  ⏳ 等待上箭头按钮出现...')
        await asyncio.sleep(1)  # 增加到 1 秒
        
        # 步骤 2: 点击上箭头按钮提交
        print('步骤 2: 点击上箭头按钮提交...')
        submit_result = await self.submit_by_button(wait_for_button=True)
        
        if not submit_result['success']:
            print(f'❌ 提交失败: {submit_result["error"]}')
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

