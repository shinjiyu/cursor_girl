#!/usr/bin/env python3
"""
验证 Playwright 安装
Verify Playwright installation
"""
from playwright.sync_api import sync_playwright
import sys


def main():
    print("=" * 70)
    print("  🔍 Verifying Playwright Installation")
    print("=" * 70)
    print()
    
    try:
        print("✅ Playwright module imported successfully")
        
        with sync_playwright() as p:
            print("✅ Playwright context created successfully")
            
            # 检查 Electron 支持
            if hasattr(p._impl_obj, 'electron'):
                print("✅ Electron support available")
            else:
                print("❌ Electron support NOT available")
                print("   This might be a version issue")
            
            # 检查浏览器
            print()
            print("📦 Installed browsers:")
            
            try:
                browser = p.chromium.launch(headless=False)
                print("   ✅ Chromium")
                browser.close()
            except Exception as e:
                print(f"   ❌ Chromium: {e}")
            
            try:
                browser = p.firefox.launch(headless=False)
                print("   ✅ Firefox")
                browser.close()
            except Exception as e:
                print(f"   ❌ Firefox: {e}")
            
            try:
                browser = p.webkit.launch(headless=False)
                print("   ✅ WebKit")
                browser.close()
            except Exception as e:
                print(f"   ❌ WebKit: {e}")
        
        print()
        print("=" * 70)
        print("  ✅ Verification Complete!")
        print("=" * 70)
        
    except ImportError as e:
        print(f"❌ Failed to import Playwright: {e}")
        print()
        print("💡 Try installing:")
        print("   pip install playwright")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

