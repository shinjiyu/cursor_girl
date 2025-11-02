#!/usr/bin/env python3
"""
Cursor DOM Inspector - 使用 Playwright 检查 Cursor 的 DOM 结构
Cursor DOM Inspector - Inspect Cursor's DOM structure using Playwright
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


class CursorDOMInspector:
    """Cursor DOM 结构检查器"""
    
    def __init__(self, cursor_path: str = None):
        """
        初始化检查器
        
        Args:
            cursor_path: Cursor 应用的路径（默认为 macOS 标准路径）
        """
        if cursor_path is None:
            # 根据操作系统确定默认路径
            if sys.platform == 'darwin':  # macOS
                self.cursor_path = '/Applications/Cursor.app/Contents/MacOS/Cursor'
            elif sys.platform == 'win32':  # Windows
                self.cursor_path = 'C:/Users/user/AppData/Local/Programs/cursor/Cursor.exe'
            else:  # Linux
                self.cursor_path = '/usr/local/bin/cursor'
        else:
            self.cursor_path = cursor_path
        
        self.playwright = None
        self.app = None
        self.page = None
        self.output_dir = Path(__file__).parent / 'cursor_dom_output'
        self.output_dir.mkdir(exist_ok=True)
    
    def start(self):
        """启动 Cursor 并建立连接"""
        print("=" * 70)
        print("  🔍 Cursor DOM Inspector")
        print("=" * 70)
        print()
        print(f"📍 Cursor Path: {self.cursor_path}")
        
        # 检查 Cursor 是否存在
        if sys.platform == 'darwin':
            app_path = self.cursor_path.replace('/Contents/MacOS/Cursor', '')
            if not os.path.exists(app_path):
                print(f"❌ Cursor not found at {app_path}")
                print("💡 Please install Cursor or provide the correct path")
                sys.exit(1)
        
        print("🚀 Starting Cursor with Playwright...")
        
        try:
            self.playwright = sync_playwright().start()
            
            # 启动 Electron 应用
            print("⏳ Launching Electron app...")
            self.app = self.playwright._impl_obj.electron.launch(
                executable_path=self.cursor_path,
                # 可选的启动参数
                # args=['--no-sandbox']
            )
            
            # 获取主窗口
            print("⏳ Waiting for main window...")
            self.page = self.app.first_window()
            
            # 等待页面加载
            print("⏳ Waiting for page to load...")
            # 等待任何内容加载（宽松的选择器）
            try:
                self.page.wait_for_selector('body', timeout=30000)
                print("✅ Cursor started successfully!")
                print()
            except PlaywrightTimeoutError:
                print("⚠️  Timeout waiting for page, but continuing...")
                print()
            
        except Exception as e:
            print(f"❌ Failed to start Cursor: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def get_page_info(self):
        """获取页面基本信息"""
        print("=" * 70)
        print("  📊 Page Information")
        print("=" * 70)
        print()
        
        try:
            title = self.page.title()
            url = self.page.url
            
            print(f"🏷️  Title: {title}")
            print(f"🔗 URL: {url}")
            print()
            
            return {
                'title': title,
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️  Could not get page info: {e}")
            return {}
    
    def get_full_html(self):
        """获取完整的 HTML"""
        print("=" * 70)
        print("  📄 Full HTML Content")
        print("=" * 70)
        print()
        
        try:
            html = self.page.content()
            
            # 保存到文件
            output_file = self.output_dir / f'cursor_full_dom_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"✅ Full HTML saved to: {output_file}")
            print(f"📏 Size: {len(html):,} characters")
            print()
            
            return html
        except Exception as e:
            print(f"❌ Failed to get HTML: {e}")
            return ""
    
    def analyze_dom_structure(self):
        """分析 DOM 结构"""
        print("=" * 70)
        print("  🔍 DOM Structure Analysis")
        print("=" * 70)
        print()
        
        try:
            # 执行 JavaScript 来分析 DOM
            result = self.page.evaluate('''() => {
                // 统计各种元素
                const stats = {
                    total_elements: document.querySelectorAll('*').length,
                    divs: document.querySelectorAll('div').length,
                    buttons: document.querySelectorAll('button').length,
                    inputs: document.querySelectorAll('input').length,
                    textareas: document.querySelectorAll('textarea').length,
                    images: document.querySelectorAll('img').length,
                    links: document.querySelectorAll('a').length,
                    forms: document.querySelectorAll('form').length,
                    iframes: document.querySelectorAll('iframe').length
                };
                
                // 获取所有按钮的信息
                const buttons = Array.from(document.querySelectorAll('button')).map(btn => ({
                    text: btn.textContent.trim().substring(0, 50),
                    aria_label: btn.getAttribute('aria-label'),
                    class: btn.className,
                    id: btn.id
                }));
                
                // 获取所有输入框的信息
                const inputs = Array.from(document.querySelectorAll('input, textarea')).map(inp => ({
                    type: inp.type || inp.tagName.toLowerCase(),
                    placeholder: inp.placeholder,
                    name: inp.name,
                    class: inp.className,
                    id: inp.id
                }));
                
                // 获取主要容器的 class 名
                const main_containers = Array.from(document.querySelectorAll('body > *')).map(el => ({
                    tag: el.tagName.toLowerCase(),
                    class: el.className,
                    id: el.id
                }));
                
                // 查找可能的编辑器元素
                const editors = Array.from(document.querySelectorAll('[class*="editor"], [class*="monaco"]')).map(el => ({
                    tag: el.tagName.toLowerCase(),
                    class: el.className.substring(0, 100),
                    id: el.id
                }));
                
                // 查找可能的 AI 相关元素
                const ai_elements = Array.from(document.querySelectorAll('[class*="ai"], [class*="chat"], [aria-label*="AI"], [aria-label*="Chat"]')).map(el => ({
                    tag: el.tagName.toLowerCase(),
                    class: el.className.substring(0, 100),
                    id: el.id,
                    aria_label: el.getAttribute('aria-label')
                }));
                
                return {
                    stats,
                    buttons: buttons.slice(0, 20),  // 前 20 个按钮
                    inputs: inputs.slice(0, 20),    // 前 20 个输入框
                    main_containers,
                    editors: editors.slice(0, 10),
                    ai_elements: ai_elements.slice(0, 10)
                };
            }''')
            
            # 打印统计信息
            print("📊 Element Statistics:")
            for key, value in result['stats'].items():
                print(f"   {key.replace('_', ' ').title()}: {value}")
            print()
            
            # 打印按钮信息
            if result['buttons']:
                print("🔘 Buttons (first 20):")
                for i, btn in enumerate(result['buttons'], 1):
                    label = btn['aria_label'] or btn['text'] or btn['class'][:30]
                    print(f"   {i}. {label}")
            print()
            
            # 打印输入框信息
            if result['inputs']:
                print("⌨️  Inputs (first 20):")
                for i, inp in enumerate(result['inputs'], 1):
                    label = inp['placeholder'] or inp['name'] or inp['class'][:30]
                    print(f"   {i}. [{inp['type']}] {label}")
            print()
            
            # 打印主容器
            if result['main_containers']:
                print("📦 Main Containers:")
                for i, cont in enumerate(result['main_containers'], 1):
                    label = cont['id'] or cont['class'][:50]
                    print(f"   {i}. <{cont['tag']}> {label}")
            print()
            
            # 打印编辑器元素
            if result['editors']:
                print("📝 Editor Elements:")
                for i, editor in enumerate(result['editors'], 1):
                    print(f"   {i}. <{editor['tag']}> {editor['class']}")
            print()
            
            # 打印 AI 相关元素
            if result['ai_elements']:
                print("🤖 AI-related Elements:")
                for i, ai in enumerate(result['ai_elements'], 1):
                    label = ai['aria_label'] or ai['class']
                    print(f"   {i}. <{ai['tag']}> {label}")
            print()
            
            # 保存分析结果到 JSON
            output_file = self.output_dir / f'cursor_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Analysis saved to: {output_file}")
            print()
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to analyze DOM: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_dom_tree(self, max_depth=5):
        """获取 DOM 树结构"""
        print("=" * 70)
        print(f"  🌳 DOM Tree (max depth: {max_depth})")
        print("=" * 70)
        print()
        
        try:
            # 执行 JavaScript 生成 DOM 树
            tree = self.page.evaluate(f'''(maxDepth) => {{
                function buildTree(element, depth) {{
                    if (depth > maxDepth || !element) return null;
                    
                    const node = {{
                        tag: element.tagName.toLowerCase(),
                        id: element.id || null,
                        class: element.className.toString().substring(0, 80) || null,
                        text: element.childNodes.length === 1 && element.childNodes[0].nodeType === 3 
                              ? element.textContent.trim().substring(0, 50) 
                              : null,
                        children_count: element.children.length,
                        children: []
                    }};
                    
                    // 只展示前 5 个子元素（避免太大）
                    const children = Array.from(element.children).slice(0, 5);
                    for (const child of children) {{
                        const childNode = buildTree(child, depth + 1);
                        if (childNode) {{
                            node.children.push(childNode);
                        }}
                    }}
                    
                    return node;
                }}
                
                return buildTree(document.body, 0);
            }}''', max_depth)
            
            # 打印树形结构
            def print_tree(node, indent=0):
                if not node:
                    return
                
                prefix = "  " * indent + "├─ "
                tag = node['tag']
                id_str = f"#{node['id']}" if node['id'] else ""
                class_str = f".{node['class'][:30]}" if node['class'] else ""
                text_str = f' "{node["text"]}"' if node['text'] else ""
                
                print(f"{prefix}<{tag}>{id_str}{class_str}{text_str}")
                
                for child in node.get('children', []):
                    print_tree(child, indent + 1)
            
            print_tree(tree)
            print()
            
            # 保存树结构到 JSON
            output_file = self.output_dir / f'cursor_tree_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tree, f, indent=2, ensure_ascii=False)
            
            print(f"✅ DOM tree saved to: {output_file}")
            print()
            
            return tree
            
        except Exception as e:
            print(f"❌ Failed to get DOM tree: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def take_screenshot(self):
        """截图"""
        print("=" * 70)
        print("  📸 Screenshot")
        print("=" * 70)
        print()
        
        try:
            output_file = self.output_dir / f'cursor_screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            self.page.screenshot(path=str(output_file))
            print(f"✅ Screenshot saved to: {output_file}")
            print()
            return output_file
        except Exception as e:
            print(f"❌ Failed to take screenshot: {e}")
            return None
    
    def stop(self):
        """停止并关闭"""
        print("=" * 70)
        print("  🛑 Stopping")
        print("=" * 70)
        print()
        
        if self.app:
            self.app.close()
            print("✅ Cursor closed")
        
        if self.playwright:
            self.playwright.stop()
            print("✅ Playwright stopped")
        
        print()
        print("=" * 70)
        print(f"  📁 All outputs saved to: {self.output_dir}")
        print("=" * 70)


def main():
    """主函数"""
    inspector = CursorDOMInspector()
    
    try:
        # 启动 Cursor
        inspector.start()
        
        # 获取页面信息
        inspector.get_page_info()
        
        # 分析 DOM 结构
        inspector.analyze_dom_structure()
        
        # 获取 DOM 树
        inspector.get_dom_tree(max_depth=4)
        
        # 获取完整 HTML
        inspector.get_full_html()
        
        # 截图
        inspector.take_screenshot()
        
        # 等待用户按键（保持窗口打开）
        print()
        print("=" * 70)
        print("  ⏸️  Press Enter to close Cursor and exit...")
        print("=" * 70)
        input()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 停止
        inspector.stop()


if __name__ == '__main__':
    main()

