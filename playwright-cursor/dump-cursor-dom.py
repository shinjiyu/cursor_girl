#!/usr/bin/env python3
"""
获取并打印 Cursor 的完整 DOM 结构
"""

import frida
import sys
import json
import time

def find_renderer_process():
    """查找 Cursor 渲染进程"""
    device = frida.get_local_device()
    processes = device.enumerate_processes()
    
    # 查找 Cursor Helper (Renderer)
    for proc in processes:
        if 'Cursor Helper (Renderer)' in proc.name:
            return proc.pid
    
    return None

def main():
    print("=" * 80)
    print("  🔍 Cursor DOM 结构获取器")
    print("=" * 80)
    print()
    
    # 查找渲染进程
    print("📝 Step 1: 查找 Cursor 渲染进程")
    print("─" * 80)
    
    renderer_pid = find_renderer_process()
    
    if not renderer_pid:
        print("❌ 未找到 Cursor 渲染进程")
        print()
        print("请确保:")
        print("  1. Cursor 正在运行")
        print("  2. 已打开一个文件（触发编辑器加载）")
        sys.exit(1)
    
    print(f"✅ 找到渲染进程: PID {renderer_pid}")
    print()
    
    # 附加到渲染进程
    print("📝 Step 2: 附加到渲染进程")
    print("─" * 80)
    
    try:
        session = frida.attach(renderer_pid)
        print(f"✅ 已附加到 PID {renderer_pid}")
    except Exception as e:
        print(f"❌ 附加失败: {e}")
        sys.exit(1)
    
    print()
    
    # 注入 DOM 获取脚本
    print("📝 Step 3: 注入 DOM 获取脚本")
    print("─" * 80)
    
    script_code = """
    console.log('🔍 开始获取 DOM 结构...');
    
    // 递归获取元素信息
    function getElementInfo(element, depth = 0, maxDepth = 5) {
        if (depth > maxDepth || !element) {
            return null;
        }
        
        const info = {
            tag: element.tagName ? element.tagName.toLowerCase() : element.nodeName,
            type: element.nodeType,
            id: element.id || null,
            classes: element.className ? 
                (typeof element.className === 'string' ? 
                    element.className.split(' ').filter(c => c.trim()) : 
                    []) : [],
            attributes: {},
            text: null,
            children: []
        };
        
        // 获取文本内容（仅对文本节点或叶子节点）
        if (element.nodeType === 3) { // Text node
            info.text = element.textContent ? element.textContent.trim().substring(0, 100) : null;
        } else if (element.children.length === 0 && element.textContent) {
            info.text = element.textContent.trim().substring(0, 100);
        }
        
        // 获取关键属性
        if (element.attributes) {
            for (let i = 0; i < element.attributes.length; i++) {
                const attr = element.attributes[i];
                // 只保留重要属性
                if (['placeholder', 'aria-label', 'role', 'type', 'name', 'data-*'].some(
                    pattern => attr.name === pattern || attr.name.startsWith('data-')
                )) {
                    info.attributes[attr.name] = attr.value ? attr.value.substring(0, 100) : '';
                }
            }
        }
        
        // 递归获取子元素（限制数量）
        if (element.children && depth < maxDepth) {
            const childrenToProcess = Math.min(element.children.length, 50); // 限制每层最多 50 个子元素
            for (let i = 0; i < childrenToProcess; i++) {
                const childInfo = getElementInfo(element.children[i], depth + 1, maxDepth);
                if (childInfo) {
                    info.children.push(childInfo);
                }
            }
            if (element.children.length > childrenToProcess) {
                info.children.push({
                    tag: '... more',
                    note: `省略了 ${element.children.length - childrenToProcess} 个子元素`
                });
            }
        }
        
        return info;
    }
    
    // 查找关键元素
    function findKeyElements() {
        const keyElements = {
            textareas: [],
            buttons: [],
            inputs: [],
            aiRelated: [],
            monacoEditor: null
        };
        
        // 查找所有 textarea
        document.querySelectorAll('textarea').forEach((ta, i) => {
            if (i < 10) { // 限制数量
                keyElements.textareas.push({
                    index: i,
                    placeholder: ta.placeholder || '',
                    visible: ta.offsetParent !== null,
                    value: ta.value ? ta.value.substring(0, 50) : '',
                    id: ta.id || null,
                    classes: ta.className
                });
            }
        });
        
        // 查找所有按钮
        document.querySelectorAll('button').forEach((btn, i) => {
            if (i < 20) {
                const text = btn.textContent ? btn.textContent.trim().substring(0, 50) : '';
                const ariaLabel = btn.getAttribute('aria-label');
                if (text || ariaLabel) {
                    keyElements.buttons.push({
                        index: i,
                        text: text,
                        ariaLabel: ariaLabel,
                        visible: btn.offsetParent !== null,
                        classes: btn.className
                    });
                }
            }
        });
        
        // 查找所有 input
        document.querySelectorAll('input').forEach((inp, i) => {
            if (i < 10) {
                keyElements.inputs.push({
                    index: i,
                    type: inp.type,
                    placeholder: inp.placeholder || '',
                    value: inp.value ? inp.value.substring(0, 50) : '',
                    visible: inp.offsetParent !== null
                });
            }
        });
        
        // 查找 AI 相关元素
        const aiSelectors = [
            '[class*="ai"]',
            '[class*="chat"]',
            '[class*="assistant"]',
            '[aria-label*="AI"]',
            '[aria-label*="Chat"]'
        ];
        
        aiSelectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0 && keyElements.aiRelated.length < 20) {
                    elements.forEach((elem, i) => {
                        if (i < 5 && keyElements.aiRelated.length < 20) {
                            keyElements.aiRelated.push({
                                selector: selector,
                                tag: elem.tagName.toLowerCase(),
                                classes: elem.className,
                                text: elem.textContent ? elem.textContent.trim().substring(0, 100) : '',
                                visible: elem.offsetParent !== null
                            });
                        }
                    });
                }
            } catch (e) {
                // 忽略无效选择器
            }
        });
        
        // 查找 Monaco Editor
        if (window.monaco && window.monaco.editor) {
            const editors = window.monaco.editor.getEditors();
            if (editors.length > 0) {
                const editor = editors[0];
                keyElements.monacoEditor = {
                    count: editors.length,
                    lineCount: editor.getModel().getLineCount(),
                    language: editor.getModel().getLanguageId(),
                    firstLine: editor.getModel().getLineContent(1).substring(0, 100)
                };
            }
        }
        
        return keyElements;
    }
    
    // 暴露 RPC 接口
    rpc.exports = {
        getDomStructure: function() {
            console.log('📄 获取 DOM 结构...');
            
            const result = {
                timestamp: new Date().toISOString(),
                title: document.title,
                url: window.location.href,
                bodyInfo: {
                    childrenCount: document.body.children.length,
                    classes: document.body.className
                },
                domTree: getElementInfo(document.body, 0, 4), // 深度限制为 4
                keyElements: findKeyElements(),
                summary: {
                    totalElements: document.querySelectorAll('*').length,
                    divCount: document.querySelectorAll('div').length,
                    textareaCount: document.querySelectorAll('textarea').length,
                    buttonCount: document.querySelectorAll('button').length,
                    inputCount: document.querySelectorAll('input').length
                }
            };
            
            console.log('✅ DOM 结构获取完成');
            return result;
        },
        
        getSimpleStructure: function() {
            // 简化版本，只返回关键元素
            return {
                title: document.title,
                keyElements: findKeyElements(),
                summary: {
                    totalElements: document.querySelectorAll('*').length,
                    textareaCount: document.querySelectorAll('textarea').length,
                    buttonCount: document.querySelectorAll('button').length
                }
            };
        }
    };
    
    console.log('✅ DOM 获取脚本已加载');
    """
    
    def on_message(message, data):
        if message['type'] == 'send':
            print(f"[Cursor] {message['payload']}")
        elif message['type'] == 'error':
            print(f"[错误] {message.get('stack', message)}")
    
    script = session.create_script(script_code)
    script.on('message', on_message)
    script.load()
    
    print("✅ DOM 获取脚本已加载")
    print()
    
    time.sleep(1)
    
    # 获取 DOM 结构
    print("📝 Step 4: 获取 DOM 结构")
    print("─" * 80)
    print()
    
    print("⏳ 正在获取 DOM 结构（这可能需要几秒钟）...")
    
    try:
        dom_data = script.exports.get_dom_structure()
        
        # 保存到文件
        output_file = "/Users/user/Documents/ cursorgirl/playwright-cursor/output/cursor_dom_structure.json"
        
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dom_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ DOM 结构已保存到: {output_file}")
        print()
        
        # 打印摘要
        print("=" * 80)
        print("  📊 DOM 结构摘要")
        print("=" * 80)
        print()
        
        print(f"📄 页面信息:")
        print(f"   标题: {dom_data['title']}")
        print(f"   URL: {dom_data['url']}")
        print()
        
        print(f"📈 元素统计:")
        summary = dom_data['summary']
        print(f"   总元素数: {summary['totalElements']}")
        print(f"   div 数量: {summary['divCount']}")
        print(f"   textarea 数量: {summary['textareaCount']}")
        print(f"   button 数量: {summary['buttonCount']}")
        print(f"   input 数量: {summary['inputCount']}")
        print()
        
        # 打印关键元素
        key_elements = dom_data['keyElements']
        
        print("🔍 关键元素:")
        print()
        
        if key_elements['textareas']:
            print(f"  📝 Textareas ({len(key_elements['textareas'])} 个):")
            for ta in key_elements['textareas']:
                visible = "✅" if ta['visible'] else "❌"
                print(f"     {visible} [{ta['index']}] placeholder: '{ta['placeholder'][:50]}'")
                if ta['classes']:
                    print(f"           classes: {ta['classes'][:100]}")
            print()
        
        if key_elements['monacoEditor']:
            monaco = key_elements['monacoEditor']
            print(f"  📝 Monaco Editor:")
            print(f"     编辑器数量: {monaco['count']}")
            print(f"     当前行数: {monaco['lineCount']}")
            print(f"     语言: {monaco['language']}")
            print(f"     第一行: {monaco['firstLine'][:50]}")
            print()
        
        if key_elements['aiRelated']:
            print(f"  🤖 AI 相关元素 ({len(key_elements['aiRelated'])} 个):")
            shown = 0
            for ai in key_elements['aiRelated']:
                if shown < 5:
                    visible = "✅" if ai['visible'] else "❌"
                    print(f"     {visible} {ai['tag']} - {ai['classes'][:60]}")
                    shown += 1
            if len(key_elements['aiRelated']) > 5:
                print(f"     ... 还有 {len(key_elements['aiRelated']) - 5} 个")
            print()
        
        print("=" * 80)
        print()
        print(f"✅ 完整 DOM 结构已保存到: {output_file}")
        print()
        print("📝 你可以用以下命令查看:")
        print(f"   cat '{output_file}'")
        print(f"   或")
        print(f"   code '{output_file}'")
        print()
        
    except Exception as e:
        print(f"❌ 获取 DOM 结构失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 清理
    session.detach()
    print("✅ 已断开 Frida 连接")

if __name__ == "__main__":
    main()

