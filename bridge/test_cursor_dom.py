#!/usr/bin/env python3
"""
快速测试脚本 - 自动运行并关闭
Quick test script - runs automatically and closes
"""
import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from cursor_dom_inspector import CursorDOMInspector
import time


def main():
    """快速测试主函数"""
    print("🚀 Starting quick test...")
    print()
    
    inspector = CursorDOMInspector()
    
    try:
        # 启动 Cursor
        inspector.start()
        
        # 等待 5 秒让界面完全加载
        print("⏳ Waiting 5 seconds for UI to fully load...")
        time.sleep(5)
        print()
        
        # 获取页面信息
        inspector.get_page_info()
        
        # 分析 DOM 结构
        inspector.analyze_dom_structure()
        
        # 获取 DOM 树（较小的深度以加快速度）
        inspector.get_dom_tree(max_depth=3)
        
        # 获取完整 HTML
        inspector.get_full_html()
        
        # 截图
        inspector.take_screenshot()
        
        print()
        print("=" * 70)
        print("  ✅ Test completed successfully!")
        print("=" * 70)
        print()
        print("📁 Check the output files in: bridge/cursor_dom_output/")
        print()
        
        # 自动关闭（等待 3 秒）
        print("⏳ Closing in 3 seconds...")
        time.sleep(3)
        
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

