#!/bin/bash
# 设置中央 Server 模式并重新注入

set -e

echo "========================================================================"
echo "  🌸 设置 Ortensia 中央 Server 模式"
echo "========================================================================"
echo ""

# 1. 设置环境变量
echo "📝 步骤 1: 设置环境变量..."
export ORTENSIA_SERVER=ws://localhost:8765
echo "export ORTENSIA_SERVER=ws://localhost:8765" >> ~/.zshrc
echo "✅ 环境变量已设置并保存到 ~/.zshrc"
echo ""

# 2. 重新注入 V9
echo "📝 步骤 2: 重新注入 V9 (将连接到中央 Server)..."
cd "$(dirname "$0")/cursor-injector"
./install-v9.sh
echo ""

# 3. 提示重启
echo "========================================================================"
echo "  ⚠️  重要：请手动完成以下步骤"
echo "========================================================================"
echo ""
echo "1️⃣  完全退出 Cursor (Cmd+Q)"
echo "2️⃣  重新启动 Cursor"
echo "3️⃣  等待 10 秒"
echo "4️⃣  查看连接日志:"
echo "    cat /tmp/cursor_ortensia.log | grep '中央'"
echo ""
echo "5️⃣  找到 Cursor Hook ID:"
echo "    cat /tmp/cursor_ortensia.log | grep 'Cursor ID'"
echo ""
echo "6️⃣  运行测试:"
echo "    cd cursor-injector"
echo "    python3 test_central_server.py"
echo ""
echo "========================================================================"
echo ""
echo "提示: 中央 Server 已在后台运行（查看另一个终端）"
echo ""







