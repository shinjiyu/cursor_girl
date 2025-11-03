#!/usr/bin/env python3
"""
获取并打印 Cursor 的完整 DOM 结构（通过进程名附加）
"""

import frida
import sys
import json
import time

def main():
    print("=" * 80)
    print("  🔍 Cursor DOM 结构获取器 v2")
    print("=" * 80)
    print()
    
    # 列出所有 Cursor 进程
    print("📝 Step 1: 列出所有 Cursor 进程")
    print("─" * 80)
    
    device = frida.get_local_device()
    processes = device.enumerate_processes()
    
    cursor_processes = [p for p in processes if 'Cursor' in p.name or 'cursor' in p.name.lower()]
    
    if not cursor_processes:
        print("❌ 未找到 Cursor 进程")
        sys.exit(1)
    
    print(f"✅ 找到 {len(cursor_processes)} 个 Cursor 进程:")
    for i, p in enumerate(cursor_processes, 1):
        print(f"   {i}. PID: {p.pid:6d}  Name: {p.name}")
    print()
    
    # 尝试附加到每个进程，找到有 window 的
    print("📝 Step 2: 查找渲染进程")
    print("─" * 80)
    
    renderer_session = None
    renderer_pid = None
    
    for proc in cursor_processes:
        try:
            print(f"   尝试 PID {proc.pid} ({proc.name[:40]})... ", end='', flush=True)
            
            # 尝试附加
            session = frida.attach(proc.pid)
            
            # 快速检测是否有 window
            check_script = session.create_script("""
                rpc.exports = {
                    hasWindow: function() {
                        try {
                            return typeof window !== 'undefined' && 
                                   typeof document !== 'undefined' &&
                                   document.body !== null;
                        } catch (e) {
                            return false;
                        }
                    }
                };
            """)
            check_script.load()
            
            has_window = check_script.exports.has_window()
            
            if has_window:
                print("✅ 这是渲染进程！")
                renderer_session = session
                renderer_pid = proc.pid
                break
            else:
                print("主进程或其他")
                session.detach()
                
        except frida.PermissionDeniedError:
            print("权限不足")
        except Exception as e:
            print(f"跳过 ({str(e)[:20]})")
    
    if not renderer_session:
        print()
        print("❌ 未找到可访问的渲染进程")
        print()
        print("💡 可能的原因:")
        print("   1. macOS 权限限制（需要允许终端控制其他应用）")
        print("   2. Cursor 正在受保护模式运行")
        print()
        print("💡 解决方法:")
        print("   1. 系统设置 → 隐私与安全性 → 辅助功能")
        print("   2. 添加 Terminal.app 到允许列表")
        print("   3. 或者在 Cursor 的 DevTools 中手动运行脚本")
        print()
        print("📝 手动方法:")
        print("   1. 在 Cursor 中按 Cmd+Shift+I 打开 DevTools")
        print("   2. 在 Console 中粘贴以下代码:")
        print()
        print("=" * 80)
        print("""
// 获取 DOM 结构
function getDomInfo() {
    const textareas = Array.from(document.querySelectorAll('textarea')).map((ta, i) => ({
        index: i,
        placeholder: ta.placeholder,
        visible: ta.offsetParent !== null,
        classes: ta.className
    }));
    
    const monaco = window.monaco && window.monaco.editor ? {
        count: window.monaco.editor.getEditors().length,
        language: window.monaco.editor.getEditors()[0]?.getModel().getLanguageId()
    } : null;
    
    return {
        title: document.title,
        totalElements: document.querySelectorAll('*').length,
        textareas: textareas,
        buttons: document.querySelectorAll('button').length,
        monaco: monaco
    };
}

console.log(JSON.stringify(getDomInfo(), null, 2));
""")
        print("=" * 80)
        sys.exit(1)
    
    print()
    
    # 注入 DOM 获取脚本
    print("📝 Step 3: 注入 DOM 获取脚本")
    print("─" * 80)
    
    script_code = """
    // 查找关键元素
    function findKeyElements() {
        const keyElements = {
            textareas: [],
            buttons: [],
            aiRelated: [],
            monacoEditor: null
        };
        
        // 查找所有 textarea
        document.querySelectorAll('textarea').forEach((ta, i) => {
            if (i < 20) {
                keyElements.textareas.push({
                    index: i,
                    placeholder: ta.placeholder || '',
                    visible: ta.offsetParent !== null,
                    id: ta.id || null,
                    classes: ta.className.substring(0, 100)
                });
            }
        });
        
        // 查找所有按钮（前20个）
        document.querySelectorAll('button').forEach((btn, i) => {
            if (i < 20) {
                const text = btn.textContent ? btn.textContent.trim().substring(0, 50) : '';
                const ariaLabel = btn.getAttribute('aria-label');
                if (text || ariaLabel) {
                    keyElements.buttons.push({
                        index: i,
                        text: text,
                        ariaLabel: ariaLabel,
                        classes: btn.className.substring(0, 100)
                    });
                }
            }
        });
        
        // 查找 AI 相关元素
        const aiSelectors = [
            '[class*="ai"]',
            '[class*="chat"]',
            '[data-*="ai"]'
        ];
        
        aiSelectors.forEach(selector => {
            try {
                document.querySelectorAll(selector).forEach((elem, i) => {
                    if (keyElements.aiRelated.length < 10) {
                        keyElements.aiRelated.push({
                            tag: elem.tagName.toLowerCase(),
                            classes: elem.className.substring(0, 100),
                            visible: elem.offsetParent !== null
                        });
                    }
                });
            } catch (e) {}
        });
        
        // Monaco Editor
        if (window.monaco && window.monaco.editor) {
            const editors = window.monaco.editor.getEditors();
            if (editors.length > 0) {
                const editor = editors[0];
                keyElements.monacoEditor = {
                    count: editors.length,
                    lineCount: editor.getModel().getLineCount(),
                    language: editor.getModel().getLanguageId()
                };
            }
        }
        
        return keyElements;
    }
    
    rpc.exports = {
        getDomInfo: function() {
            return {
                timestamp: new Date().toISOString(),
                title: document.title,
                url: window.location.href,
                keyElements: findKeyElements(),
                summary: {
                    totalElements: document.querySelectorAll('*').length,
                    divCount: document.querySelectorAll('div').length,
                    textareaCount: document.querySelectorAll('textarea').length,
                    buttonCount: document.querySelectorAll('button').length
                }
            };
        }
    };
    """
    
    def on_message(message, data):
        if message['type'] == 'send':
            print(f"[Cursor] {message['payload']}")
    
    script = renderer_session.create_script(script_code)
    script.on('message', on_message)
    script.load()
    
    print("✅ DOM 获取脚本已加载")
    print()
    
    time.sleep(0.5)
    
    # 获取 DOM 信息
    print("📝 Step 4: 获取 DOM 信息")
    print("─" * 80)
    print()
    
    try:
        dom_data = script.exports.get_dom_info()
        
        # 保存到文件
        output_file = "/Users/user/Documents/ cursorgirl/playwright-cursor/output/cursor_dom_info.json"
        
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dom_data, f, indent=2, ensure_ascii=False)
        
        # 打印结果
        print("=" * 80)
        print("  📊 Cursor DOM 信息")
        print("=" * 80)
        print()
        
        print(f"📄 页面信息:")
        print(f"   标题: {dom_data['title']}")
        print(f"   URL: {dom_data['url'][:100]}")
        print()
        
        print(f"📈 元素统计:")
        summary = dom_data['summary']
        print(f"   总元素数: {summary['totalElements']}")
        print(f"   div 数量: {summary['divCount']}")
        print(f"   textarea 数量: {summary['textareaCount']}")
        print(f"   button 数量: {summary['buttonCount']}")
        print()
        
        # 关键元素
        key_elements = dom_data['keyElements']
        
        if key_elements['textareas']:
            print(f"🔍 Textareas ({len(key_elements['textareas'])} 个):")
            for ta in key_elements['textareas']:
                visible = "✅" if ta['visible'] else "❌"
                print(f"   {visible} [{ta['index']}] '{ta['placeholder'][:60]}'")
                print(f"       classes: {ta['classes'][:80]}")
            print()
        
        if key_elements['monacoEditor']:
            monaco = key_elements['monacoEditor']
            print(f"📝 Monaco Editor:")
            print(f"   编辑器数量: {monaco['count']}")
            print(f"   当前行数: {monaco['lineCount']}")
            print(f"   语言: {monaco['language']}")
            print()
        
        if key_elements['aiRelated']:
            print(f"🤖 AI 相关元素 ({len(key_elements['aiRelated'])} 个):")
            for ai in key_elements['aiRelated'][:10]:
                visible = "✅" if ai['visible'] else "❌"
                print(f"   {visible} {ai['tag']} - {ai['classes'][:70]}")
            print()
        
        print(f"📝 完整按钮列表 ({len(key_elements['buttons'])} 个，显示前10个):")
        for btn in key_elements['buttons'][:10]:
            text = btn['text'] or btn['ariaLabel'] or '(无文本)'
            print(f"   [{btn['index']}] {text[:60]}")
        print()
        
        print("=" * 80)
        print()
        print(f"✅ 完整信息已保存到: {output_file}")
        print()
        
    except Exception as e:
        print(f"❌ 获取信息失败: {e}")
        import traceback
        traceback.print_exc()
    
    renderer_session.detach()
    print("✅ 已断开连接")

if __name__ == "__main__":
    main()

