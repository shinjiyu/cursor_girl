#!/usr/bin/env python3
"""
使用 sudo 权限获取 Cursor DOM 结构
运行方法: sudo python3 dump-cursor-dom-sudo.py
"""

import frida
import sys
import json
import time
import os

def main():
    # 检查是否以 root 运行
    if os.geteuid() != 0:
        print("❌ 此脚本需要 root 权限")
        print()
        print("请使用 sudo 运行:")
        print(f"   sudo python3 {sys.argv[0]}")
        print()
        sys.exit(1)
    
    print("=" * 80)
    print("  🔥 Cursor DOM 获取器（高权限模式）")
    print("=" * 80)
    print()
    
    # 列出所有 Cursor 进程
    print("📝 Step 1: 查找 Cursor 进程")
    print("─" * 80)
    
    device = frida.get_local_device()
    processes = device.enumerate_processes()
    
    cursor_processes = [p for p in processes if 'Cursor' in p.name]
    
    if not cursor_processes:
        print("❌ 未找到 Cursor 进程")
        print("请确保 Cursor 正在运行")
        sys.exit(1)
    
    print(f"✅ 找到 {len(cursor_processes)} 个 Cursor 进程:")
    for i, p in enumerate(cursor_processes[:15], 1):  # 只显示前15个
        print(f"   {i:2d}. PID: {p.pid:6d}  {p.name[:60]}")
    print()
    
    # 查找渲染进程
    print("📝 Step 2: 查找并附加到渲染进程")
    print("─" * 80)
    
    renderer_session = None
    renderer_pid = None
    
    for proc in cursor_processes:
        # 优先尝试名字中包含 "Renderer" 的进程
        if 'Renderer' in proc.name:
            try:
                print(f"   尝试附加到 PID {proc.pid} ({proc.name[:50]})... ", end='', flush=True)
                
                session = frida.attach(proc.pid)
                
                # 快速检测是否有 window 和 document
                check_script = session.create_script("""
                    rpc.exports = {
                        hasDOM: function() {
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
                
                has_dom = check_script.exports.has_dom()
                
                if has_dom:
                    print("✅ 成功！找到渲染进程")
                    renderer_session = session
                    renderer_pid = proc.pid
                    break
                else:
                    print("没有 DOM")
                    session.detach()
                    
            except Exception as e:
                print(f"失败 ({str(e)[:30]})")
    
    if not renderer_session:
        print()
        print("❌ 未找到渲染进程")
        sys.exit(1)
    
    print()
    
    # 注入 DOM 获取脚本
    print("📝 Step 3: 注入 DOM 获取脚本")
    print("─" * 80)
    
    script_code = """
    console.log('🎉 Frida 注入成功！开始获取 DOM...');
    
    // 获取关键元素
    function getKeyElements() {
        const result = {
            textareas: [],
            buttons: [],
            aiRelated: [],
            monacoEditor: null
        };
        
        // Textareas
        document.querySelectorAll('textarea').forEach((ta, i) => {
            if (i < 20) {
                const rect = ta.getBoundingClientRect();
                result.textareas.push({
                    index: i,
                    id: ta.id || null,
                    placeholder: ta.placeholder || '',
                    visible: ta.offsetParent !== null,
                    focused: document.activeElement === ta,
                    classes: ta.className,
                    position: {
                        top: Math.round(rect.top),
                        left: Math.round(rect.left),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height)
                    }
                });
            }
        });
        
        // Buttons (前30个)
        document.querySelectorAll('button').forEach((btn, i) => {
            if (i < 30) {
                const text = btn.textContent ? btn.textContent.trim().substring(0, 50) : '';
                const ariaLabel = btn.getAttribute('aria-label');
                result.buttons.push({
                    index: i,
                    text: text,
                    ariaLabel: ariaLabel,
                    visible: btn.offsetParent !== null,
                    classes: btn.className ? btn.className.substring(0, 100) : ''
                });
            }
        });
        
        // AI 相关元素
        const aiSelectors = [
            '[class*="ai"]',
            '[class*="chat"]',
            '[class*="assistant"]'
        ];
        
        aiSelectors.forEach(selector => {
            try {
                document.querySelectorAll(selector).forEach((elem, i) => {
                    if (result.aiRelated.length < 20) {
                        result.aiRelated.push({
                            selector: selector,
                            tag: elem.tagName.toLowerCase(),
                            id: elem.id || null,
                            classes: elem.className ? elem.className.substring(0, 100) : '',
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
                const model = editor.getModel();
                result.monacoEditor = {
                    count: editors.length,
                    language: model.getLanguageId(),
                    lineCount: model.getLineCount(),
                    valueLength: model.getValue().length,
                    firstLine: model.getLineContent(1).substring(0, 100)
                };
            }
        }
        
        return result;
    }
    
    rpc.exports = {
        getDomData: function() {
            return {
                timestamp: new Date().toISOString(),
                title: document.title,
                url: window.location.href,
                summary: {
                    totalElements: document.querySelectorAll('*').length,
                    divs: document.querySelectorAll('div').length,
                    textareas: document.querySelectorAll('textarea').length,
                    inputs: document.querySelectorAll('input').length,
                    buttons: document.querySelectorAll('button').length
                },
                keyElements: getKeyElements()
            };
        }
    };
    
    console.log('✅ DOM 获取脚本已就绪');
    """
    
    def on_message(message, data):
        if message['type'] == 'send':
            print(f"[Cursor] {message['payload']}")
    
    script = renderer_session.create_script(script_code)
    script.on('message', on_message)
    script.load()
    
    print("✅ 脚本已加载")
    print()
    
    time.sleep(1)
    
    # 获取 DOM 数据
    print("📝 Step 4: 获取 DOM 数据")
    print("─" * 80)
    print()
    
    try:
        dom_data = script.exports.get_dom_data()
        
        # 保存到文件
        output_dir = "/Users/user/Documents/ cursorgirl/playwright-cursor/output"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, "cursor_dom_structure.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dom_data, f, indent=2, ensure_ascii=False)
        
        # 打印结果
        print("=" * 80)
        print("  📊 Cursor DOM 结构")
        print("=" * 80)
        print()
        
        print(f"📄 页面信息:")
        print(f"   标题: {dom_data['title']}")
        print(f"   URL: {dom_data['url'][:80]}")
        print()
        
        print(f"📈 元素统计:")
        summary = dom_data['summary']
        print(f"   总元素: {summary['totalElements']}")
        print(f"   DIV: {summary['divs']}")
        print(f"   TEXTAREA: {summary['textareas']}")
        print(f"   INPUT: {summary['inputs']}")
        print(f"   BUTTON: {summary['buttons']}")
        print()
        
        key_elements = dom_data['keyElements']
        
        # Textareas
        if key_elements['textareas']:
            print(f"🔍 Textareas ({len(key_elements['textareas'])} 个):")
            for ta in key_elements['textareas']:
                visible = "✅" if ta['visible'] else "❌"
                focused = "🔴" if ta['focused'] else "  "
                print(f"   {visible}{focused} [{ta['index']}] \"{ta['placeholder'][:60]}\"")
                if ta['classes']:
                    print(f"          classes: {ta['classes'][:80]}")
                print(f"          position: {ta['position']}")
            print()
        
        # Monaco Editor
        if key_elements['monacoEditor']:
            monaco = key_elements['monacoEditor']
            print(f"📝 Monaco Editor:")
            print(f"   编辑器数量: {monaco['count']}")
            print(f"   语言: {monaco['language']}")
            print(f"   行数: {monaco['lineCount']}")
            print(f"   字符数: {monaco['valueLength']}")
            print(f"   第一行: {monaco['firstLine'][:60]}")
            print()
        
        # AI 元素
        if key_elements['aiRelated']:
            print(f"🤖 AI 相关元素 ({len(key_elements['aiRelated'])} 个):")
            for ai in key_elements['aiRelated'][:10]:
                visible = "✅" if ai['visible'] else "❌"
                print(f"   {visible} {ai['tag']} - {ai['classes'][:70]}")
            if len(key_elements['aiRelated']) > 10:
                print(f"   ... 还有 {len(key_elements['aiRelated']) - 10} 个")
            print()
        
        # 按钮
        print(f"🔘 按钮 ({len(key_elements['buttons'])} 个，显示前10个):")
        for btn in key_elements['buttons'][:10]:
            text = btn['text'] or btn['ariaLabel'] or '(无文本)'
            visible = "✅" if btn['visible'] else "❌"
            print(f"   {visible} [{btn['index']}] {text[:60]}")
        print()
        
        print("=" * 80)
        print()
        print(f"✅ 完整数据已保存到:")
        print(f"   {output_file}")
        print()
        print("📝 查看文件:")
        print(f"   cat '{output_file}'")
        print(f"   或")
        print(f"   code '{output_file}'")
        print()
        
        # 打印完整 JSON 到终端
        print("=" * 80)
        print("  📋 完整 JSON 数据（可直接复制）")
        print("=" * 80)
        print()
        print(json.dumps(dom_data, indent=2, ensure_ascii=False))
        print()
        
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 清理
    renderer_session.detach()
    print("✅ 已断开连接")

if __name__ == "__main__":
    main()

