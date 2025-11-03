#!/usr/bin/env python3
"""
Frida 动态注入测试脚本
测试 Frida 能否动态附加到 Cursor 并访问 DOM
"""

import frida
import sys
import time

def on_message(message, data):
    """处理来自 Frida 脚本的消息"""
    if message['type'] == 'send':
        print(f"[Cursor] {message['payload']}")
    elif message['type'] == 'error':
        print(f"[错误] {message['stack']}")

def main():
    print("=" * 70)
    print("  🔥 Frida 动态注入测试")
    print("=" * 70)
    print()
    
    # Step 1: 查找 Cursor 进程
    print("📝 Step 1: 查找 Cursor 进程")
    print("─" * 70)
    
    try:
        # 尝试通过进程名附加
        print("🔍 尝试附加到 Cursor...")
        session = frida.attach("Cursor")
        print(f"✅ 成功附加到 Cursor!")
        print(f"   PID: {session.pid}")
    except frida.ProcessNotFoundError:
        print("❌ Cursor 未运行")
        print()
        print("请先启动 Cursor：")
        print("   open -a Cursor")
        print()
        print("然后重新运行此脚本：")
        print("   python playwright-cursor/test-frida-python.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 附加失败: {e}")
        sys.exit(1)
    
    print()
    
    # Step 2: 注入测试脚本
    print("📝 Step 2: 注入测试脚本")
    print("─" * 70)
    
    script_code = """
    console.log('');
    console.log('=' .repeat(70));
    console.log('  🎉 Frida 动态注入成功！');
    console.log('=' .repeat(70));
    console.log('');
    
    // 测试 1: 检查环境
    console.log('✅ 测试 1: 检查 JavaScript 环境');
    console.log('   typeof globalThis:', typeof globalThis);
    console.log('   typeof process:', typeof process);
    console.log('');
    
    // 测试 2: 尝试访问 window（如果在渲染进程）
    console.log('✅ 测试 2: 检查渲染进程环境');
    try {
        if (typeof window !== 'undefined') {
            console.log('   ✅ 在渲染进程中！可以访问 window');
            console.log('   typeof document:', typeof document);
            console.log('   document.title:', document.title);
            
            // 测试 3: 查找 DOM 元素
            console.log('');
            console.log('✅ 测试 3: 查找 DOM 元素');
            const bodyChildren = document.body ? document.body.children.length : 0;
            console.log('   body.children.length:', bodyChildren);
            
            const textareas = document.querySelectorAll('textarea').length;
            console.log('   textarea 数量:', textareas);
            
            const divs = document.querySelectorAll('div').length;
            console.log('   div 数量:', divs);
            
            // 测试 4: 查找 Monaco Editor
            console.log('');
            console.log('✅ 测试 4: 查找 Monaco Editor');
            if (window.monaco) {
                console.log('   ✅ Monaco Editor 可用！');
                if (window.monaco.editor) {
                    const editors = window.monaco.editor.getEditors();
                    console.log('   编辑器数量:', editors.length);
                    if (editors.length > 0) {
                        const editor = editors[0];
                        const lineCount = editor.getModel().getLineCount();
                        const language = editor.getModel().getLanguageId();
                        console.log('   当前文件行数:', lineCount);
                        console.log('   当前语言:', language);
                    }
                }
            } else {
                console.log('   ⚠️  Monaco Editor 未找到（可能尚未加载）');
            }
            
            // 测试 5: 创建测试 API
            console.log('');
            console.log('✅ 测试 5: 创建全局 API');
            window.fridaTestAPI = {
                version: '1.0.0-test',
                injectedAt: new Date().toISOString(),
                test: function() {
                    return 'Frida 注入成功！';
                }
            };
            console.log('   ✅ window.fridaTestAPI 已创建');
            
        } else {
            console.log('   ⚠️  不在渲染进程中（这是主进程）');
            console.log('   ⚠️  无法访问 window 和 DOM');
            console.log('');
            console.log('   💡 Electron 有多个进程：');
            console.log('      - 主进程（管理窗口）← 你现在在这里');
            console.log('      - 渲染进程（UI 界面）← 我们需要附加到这里');
            console.log('');
            console.log('   解决方法：');
            console.log('      1. 使用 frida-ps 列出所有 Cursor 进程');
            console.log('      2. 找到渲染进程的 PID');
            console.log('      3. 直接附加到渲染进程');
        }
    } catch (e) {
        console.log('   ❌ 错误:', e.message);
    }
    console.log('');
    
    // 暴露 RPC 接口
    rpc.exports = {
        ping: function() {
            return { success: true, message: 'Frida RPC 工作正常！' };
        },
        
        checkEnvironment: function() {
            const hasWindow = typeof window !== 'undefined';
            const hasDocument = typeof document !== 'undefined';
            
            let result = {
                hasWindow: hasWindow,
                hasDocument: hasDocument,
                isRenderer: hasWindow && hasDocument
            };
            
            if (hasWindow && hasDocument) {
                result.title = document.title;
                result.bodyChildren = document.body ? document.body.children.length : 0;
                result.textareas = document.querySelectorAll('textarea').length;
            }
            
            return result;
        }
    };
    
    console.log('=' .repeat(70));
    console.log('  ✅ 注入脚本加载完成');
    console.log('=' .repeat(70));
    console.log('');
    """
    
    try:
        print("💉 创建并加载 Frida 脚本...")
        script = session.create_script(script_code)
        script.on('message', on_message)
        script.load()
        print("✅ 脚本已加载")
        print()
        
        # 等待脚本执行
        time.sleep(2)
        
        # Step 3: 测试 RPC 调用
        print("📝 Step 3: 测试 RPC 调用")
        print("─" * 70)
        
        print("🧪 调用 ping()...")
        result = script.exports.ping()
        print(f"   结果: {result}")
        print()
        
        print("🧪 调用 checkEnvironment()...")
        env_info = script.exports.check_environment()
        print(f"   环境信息:")
        for key, value in env_info.items():
            print(f"      {key}: {value}")
        print()
        
        # Step 4: 总结
        print("=" * 70)
        print("  📊 测试总结")
        print("=" * 70)
        print()
        
        if env_info.get('isRenderer'):
            print("✅ 成功！Frida 已附加到 Cursor 的渲染进程")
            print("✅ 可以访问 DOM 和 window 对象")
            print("✅ 可以控制 Cursor 的 UI")
            print()
            print("🎉 动态注入测试通过！")
            print()
            print("🚀 下一步:")
            print("   1. 查找 Cursor AI 的 DOM 元素")
            print("   2. 实现自动发送 AI 命令")
            print("   3. 集成到 Ortensia 系统")
        else:
            print("⚠️  注意：Frida 附加到了主进程，不是渲染进程")
            print()
            print("📝 这是正常的，因为 Electron 有多个进程：")
            print("   • 主进程：管理窗口、文件系统（Node.js 环境）")
            print("   • 渲染进程：UI 界面、DOM（浏览器环境）")
            print()
            print("💡 解决方法：")
            print("   1. 列出所有 Cursor 进程：")
            print("      source venv/bin/activate")
            print("      frida-ps | grep -i cursor")
            print()
            print("   2. 找到带有 '--type=renderer' 的进程")
            print()
            print("   3. 直接附加到渲染进程：")
            print("      frida -p <renderer_pid> -l script.js")
            print()
            print("   我会创建一个自动查找渲染进程的脚本...")
        
        print()
        print("=" * 70)
        
        # 保持连接
        print()
        print("🔄 保持 Frida 连接...")
        print("   按 Ctrl+C 断开连接")
        print()
        
        try:
            sys.stdin.read()
        except KeyboardInterrupt:
            print()
            print("👋 断开连接...")
        
    except Exception as e:
        print(f"❌ 注入失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if session:
            session.detach()
            print("✅ 已断开 Frida 连接")

if __name__ == "__main__":
    main()

