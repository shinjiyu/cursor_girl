#!/usr/bin/env python3
"""
自动查找并附加到 Cursor 渲染进程
"""

import frida
import sys
import time

def find_cursor_renderer():
    """查找 Cursor 的渲染进程"""
    print("🔍 查找 Cursor 渲染进程...")
    print()
    
    # 获取所有进程
    device = frida.get_local_device()
    processes = device.enumerate_processes()
    
    # 查找所有 Cursor 相关进程
    cursor_processes = []
    for proc in processes:
        if 'Cursor' in proc.name or 'cursor' in proc.name.lower():
            cursor_processes.append(proc)
    
    if not cursor_processes:
        print("❌ 未找到 Cursor 进程")
        print()
        print("请先启动 Cursor：")
        print("   open -a Cursor")
        return None
    
    print(f"✅ 找到 {len(cursor_processes)} 个 Cursor 进程：")
    print()
    
    # 显示所有进程
    for i, proc in enumerate(cursor_processes, 1):
        print(f"   {i}. PID: {proc.pid:6d}  Name: {proc.name}")
    
    print()
    
    # Electron 渲染进程通常是主进程之后的进程
    # 或者我们可以尝试附加到每个进程并检查是否有 window 对象
    
    print("🔬 检测哪个是渲染进程...")
    print()
    
    renderer_pid = None
    
    for proc in cursor_processes:
        try:
            print(f"   尝试 PID {proc.pid}... ", end='', flush=True)
            session = frida.attach(proc.pid)
            
            # 快速检测脚本
            check_script = session.create_script("""
                rpc.exports = {
                    hasWindow: function() {
                        return typeof window !== 'undefined' && typeof document !== 'undefined';
                    }
                };
            """)
            check_script.load()
            
            has_window = check_script.exports.has_window()
            
            session.detach()
            
            if has_window:
                print("✅ 这是渲染进程！")
                renderer_pid = proc.pid
                break
            else:
                print("主进程或其他进程")
        except Exception as e:
            print(f"跳过 ({str(e)[:30]})")
            continue
    
    print()
    return renderer_pid

def test_renderer(pid):
    """测试渲染进程"""
    print("=" * 70)
    print(f"  🎯 附加到渲染进程 (PID: {pid})")
    print("=" * 70)
    print()
    
    session = frida.attach(pid)
    
    script_code = """
    console.log('🎉 成功附加到渲染进程！');
    console.log('');
    
    // DOM 测试
    console.log('📄 DOM 信息:');
    console.log('   document.title:', document.title);
    console.log('   window.location:', window.location.href);
    console.log('   body children:', document.body.children.length);
    console.log('');
    
    // 查找 Cursor UI 元素
    console.log('🔍 查找 Cursor UI 元素:');
    
    const textareas = document.querySelectorAll('textarea');
    console.log('   textarea 数量:', textareas.length);
    
    textareas.forEach((ta, i) => {
        console.log(`   textarea ${i + 1}:`);
        console.log('      placeholder:', ta.placeholder);
        console.log('      visible:', ta.offsetParent !== null);
    });
    console.log('');
    
    // Monaco Editor
    console.log('📝 Monaco Editor:');
    if (window.monaco && window.monaco.editor) {
        const editors = window.monaco.editor.getEditors();
        console.log('   编辑器数量:', editors.length);
        if (editors.length > 0) {
            const editor = editors[0];
            console.log('   当前行数:', editor.getModel().getLineCount());
            console.log('   语言:', editor.getModel().getLanguageId());
            console.log('   前 3 行:', editor.getModel().getLineContent(1).substring(0, 50));
        }
    } else {
        console.log('   ⚠️  Monaco 未找到');
    }
    console.log('');
    
    // 创建控制 API
    console.log('🎮 创建 Ortensia 控制 API...');
    window.ortensiaAPI = {
        version: '1.0.0-renderer',
        
        findAIInput: function() {
            const selectors = [
                'textarea[placeholder*="Ask"]',
                'textarea[placeholder*="Chat"]',
                'textarea[placeholder*="AI"]',
                '.ai-input textarea',
                '.chat-input textarea'
            ];
            
            for (const selector of selectors) {
                const elem = document.querySelector(selector);
                if (elem && elem.offsetParent !== null) {
                    return {
                        found: true,
                        selector: selector,
                        placeholder: elem.placeholder
                    };
                }
            }
            
            return { found: false };
        },
        
        sendToAI: function(prompt) {
            const input = document.querySelector('textarea[placeholder*="Ask"], textarea[placeholder*="Chat"]');
            if (input) {
                input.value = prompt;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new KeyboardEvent('keydown', {
                    key: 'Enter',
                    code: 'Enter',
                    bubbles: true
                }));
                return { success: true };
            }
            return { success: false, error: 'Input not found' };
        },
        
        getEditorCode: function() {
            if (window.monaco && window.monaco.editor) {
                const editors = window.monaco.editor.getEditors();
                if (editors.length > 0) {
                    return {
                        success: true,
                        code: editors[0].getValue(),
                        language: editors[0].getModel().getLanguageId()
                    };
                }
            }
            return { success: false };
        }
    };
    console.log('✅ ortensiaAPI 已创建');
    console.log('');
    
    // 暴露 RPC
    rpc.exports = {
        findAIInput: function() {
            return window.ortensiaAPI.findAIInput();
        },
        
        sendToAI: function(prompt) {
            return window.ortensiaAPI.sendToAI(prompt);
        },
        
        getEditorCode: function() {
            return window.ortensiaAPI.getEditorCode();
        }
    };
    
    console.log('=' .repeat(70));
    console.log('✅ 渲染进程注入完成！');
    console.log('=' .repeat(70));
    """
    
    def on_message(message, data):
        if message['type'] == 'send':
            print(f"[Cursor] {message['payload']}")
        elif message['type'] == 'error':
            print(f"[错误] {message['stack']}")
    
    script = session.create_script(script_code)
    script.on('message', on_message)
    script.load()
    
    time.sleep(1)
    
    # 测试 RPC
    print()
    print("=" * 70)
    print("  🧪 测试控制功能")
    print("=" * 70)
    print()
    
    print("1️⃣  查找 AI 输入框...")
    ai_input = script.exports.find_ai_input()
    print(f"   结果: {ai_input}")
    print()
    
    print("2️⃣  获取编辑器代码...")
    editor_info = script.exports.get_editor_code()
    if editor_info.get('success'):
        code = editor_info['code']
        print(f"   语言: {editor_info['language']}")
        print(f"   行数: {len(code.splitlines())}")
        print(f"   前 100 字符: {code[:100]}")
    else:
        print("   ⚠️  未找到编辑器")
    print()
    
    # 询问是否测试发送 AI 命令
    print("3️⃣  测试发送 AI 命令（可选）")
    try:
        response = input("   是否测试发送 AI 命令？(y/N): ")
        if response.lower() == 'y':
            prompt = input("   输入要发送的命令: ")
            result = script.exports.send_to_ai(prompt)
            print(f"   结果: {result}")
    except EOFError:
        print("   跳过")
    
    print()
    print("=" * 70)
    print("  🎉 测试完成！")
    print("=" * 70)
    print()
    print("✅ Frida 可以:")
    print("   • 动态附加到 Cursor 渲染进程")
    print("   • 完整访问 DOM 和 window 对象")
    print("   • 查找和控制 UI 元素")
    print("   • 访问 Monaco Editor")
    print("   • 发送 AI 命令")
    print()
    print("🚀 下一步: 集成到 Ortensia 系统")
    print()
    print("按 Ctrl+C 断开连接...")
    
    try:
        sys.stdin.read()
    except KeyboardInterrupt:
        print()
    
    session.detach()
    print("✅ 已断开")

def main():
    print()
    print("=" * 70)
    print("  🔥 Frida 渲染进程查找器")
    print("=" * 70)
    print()
    
    renderer_pid = find_cursor_renderer()
    
    if renderer_pid:
        print("=" * 70)
        print()
        try:
            test_renderer(renderer_pid)
        except KeyboardInterrupt:
            print()
            print("👋 中断")
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ 未找到渲染进程")
        print()
        print("💡 可能的原因:")
        print("   1. Cursor 未完全启动")
        print("   2. 渲染进程尚未创建")
        print("   3. 权限问题")
        print()
        print("💡 解决方法:")
        print("   1. 确保 Cursor 已完全启动")
        print("   2. 打开一个文件（触发编辑器加载）")
        print("   3. 重新运行此脚本")

if __name__ == "__main__":
    main()

