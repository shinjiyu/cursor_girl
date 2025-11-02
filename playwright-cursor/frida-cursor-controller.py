#!/usr/bin/env python3
"""
Frida Cursor Controller - 使用 Frida 动态注入控制 Cursor
"""
import frida
import sys
import time


class FridaCursorController:
    """通过 Frida 控制 Cursor"""
    
    def __init__(self, process_name='Cursor'):
        self.process_name = process_name
        self.session = None
        self.script = None
    
    def attach(self):
        """附加到 Cursor 进程"""
        print(f"🔗 Attaching to {self.process_name}...")
        
        try:
            # 方法 1: 通过进程名附加
            self.session = frida.attach(self.process_name)
            print(f"✅ Attached to {self.process_name}")
            return True
        except frida.ProcessNotFoundError:
            print(f"❌ Process '{self.process_name}' not found")
            print("💡 Make sure Cursor is running")
            return False
        except Exception as e:
            print(f"❌ Failed to attach: {e}")
            return False
    
    def load_script(self, script_path='frida-inject-cursor.js'):
        """加载注入脚本"""
        print(f"📜 Loading script: {script_path}")
        
        try:
            with open(script_path, 'r') as f:
                script_code = f.read()
            
            # 创建脚本
            self.script = self.session.create_script(script_code)
            
            # 设置消息处理器
            self.script.on('message', self._on_message)
            
            # 加载脚本
            self.script.load()
            print("✅ Script loaded")
            
            # 等待脚本初始化
            time.sleep(2)
            return True
            
        except FileNotFoundError:
            print(f"❌ Script file not found: {script_path}")
            return False
        except Exception as e:
            print(f"❌ Failed to load script: {e}")
            return False
    
    def _on_message(self, message, data):
        """处理来自 Frida 脚本的消息"""
        if message['type'] == 'send':
            payload = message['payload']
            print(f"📨 Message from Frida: {payload}")
        elif message['type'] == 'error':
            print(f"❌ Error from Frida: {message['stack']}")
    
    def inject(self):
        """执行注入"""
        print("💉 Injecting control code...")
        
        try:
            result = self.script.exports.inject()
            print(f"✅ Injection result: {result}")
            return result
        except Exception as e:
            print(f"❌ Injection failed: {e}")
            return None
    
    def execute_js(self, code):
        """在 Cursor 中执行 JavaScript"""
        print(f"🔧 Executing JS: {code[:50]}...")
        
        try:
            result = self.script.exports.execute_js(code)
            print(f"✅ Result: {result}")
            return result
        except Exception as e:
            print(f"❌ Execution failed: {e}")
            return None
    
    def find_cursor_ai(self):
        """查找 Cursor AI 的 API"""
        print("🔍 Searching for Cursor AI...")
        
        try:
            result = self.script.exports.find_cursor_ai()
            print(f"✅ Result: {result}")
            return result
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return None
    
    def detach(self):
        """分离"""
        if self.session:
            print("👋 Detaching...")
            self.session.detach()
            print("✅ Detached")


def main():
    """主函数"""
    print("=" * 70)
    print("  🔥 Frida Cursor Controller")
    print("=" * 70)
    print()
    
    # 创建控制器
    controller = FridaCursorController()
    
    # 附加到进程
    if not controller.attach():
        return 1
    
    # 加载脚本
    if not controller.load_script('frida-inject-cursor.js'):
        return 1
    
    print()
    print("=" * 70)
    print("  🎮 Interactive Mode")
    print("=" * 70)
    print()
    print("Commands:")
    print("  inject          - Inject control code")
    print("  exec <code>     - Execute JavaScript")
    print("  find            - Find Cursor AI API")
    print("  test            - Run test injection")
    print("  quit            - Exit")
    print()
    
    # 交互循环
    try:
        while True:
            cmd = input("frida> ").strip()
            
            if not cmd:
                continue
            
            if cmd == 'quit':
                break
            elif cmd == 'inject':
                controller.inject()
            elif cmd == 'find':
                controller.find_cursor_ai()
            elif cmd == 'test':
                # 测试注入
                test_code = '''
                    console.log("🧪 Test injection from Frida");
                    window.fridaTest = {
                        version: "1.0",
                        timestamp: new Date().toISOString()
                    };
                '''
                controller.execute_js(test_code)
            elif cmd.startswith('exec '):
                code = cmd[5:].strip()
                controller.execute_js(code)
            else:
                print(f"❌ Unknown command: {cmd}")
    
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        controller.detach()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

