#!/bin/bash

# Cursor DOM 获取脚本 - 使用 sudo 权限运行
# 这个脚本会要求你输入管理员密码

echo "======================================================================="
echo "  🔥 Cursor DOM 获取器（高权限模式）"
echo "======================================================================="
echo ""
echo "⚠️  此脚本需要管理员权限来访问 Cursor 进程"
echo "    系统会提示你输入密码（这是正常的）"
echo ""
echo "按 Enter 继续，或 Ctrl+C 取消..."
read

# 激活虚拟环境
cd "/Users/user/Documents/ cursorgirl/bridge"
source venv/bin/activate

# 使用 sudo 运行 Python 脚本
echo ""
echo "🔐 请输入管理员密码:"
cd "/Users/user/Documents/ cursorgirl"
sudo "$(which python3)" playwright-cursor/dump-cursor-dom-sudo.py

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================="
    echo "  ✅ DOM 数据获取成功！"
    echo "======================================================================="
    echo ""
    echo "📁 数据已保存到:"
    echo "   /Users/user/Documents/ cursorgirl/playwright-cursor/output/cursor_dom_structure.json"
    echo ""
    echo "📝 查看数据:"
    echo "   cat '/Users/user/Documents/ cursorgirl/playwright-cursor/output/cursor_dom_structure.json'"
    echo ""
else
    echo ""
    echo "❌ 获取失败，请检查:"
    echo "   1. Cursor 是否正在运行"
    echo "   2. 是否输入了正确的密码"
    echo "   3. 是否打开了一个代码文件"
fi

echo ""
echo "按 Enter 退出..."
read

