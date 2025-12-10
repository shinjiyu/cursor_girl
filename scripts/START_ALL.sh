#!/bin/bash
# Ortensia V9 - 一键启动中央服务器

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║          🌸 Ortensia V9 - 中央服务器启动                         ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# 检查中央服务器是否已在运行
if lsof -i :8765 &> /dev/null; then
    echo -e "${YELLOW}⚠️  端口 8765 已被占用（服务器可能已在运行）${NC}"
    echo ""
    echo "如需重启，请先运行: ./scripts/STOP_ALL.sh"
    exit 0
fi

# 启动中央服务器（使用 ChatTTS 虚拟环境）
echo -e "${BLUE}🚀 启动中央 WebSocket 服务器 (ChatTTS)...${NC}"
cd "$PROJECT_DIR/bridge"

# ChatTTS 虚拟环境路径
CHATTTS_VENV="/Users/user/Documents/tts/chattts/venv"

# 检查虚拟环境是否存在
if [ ! -d "$CHATTTS_VENV" ]; then
    echo -e "${RED}❌ ChatTTS 虚拟环境未找到: $CHATTTS_VENV${NC}"
    echo -e "${YELLOW}请先安装 ChatTTS 或修改路径${NC}"
    exit 1
fi

# 启动服务器（使用 ChatTTS 虚拟环境）
source "$CHATTTS_VENV/bin/activate"
python websocket_server.py > /tmp/ws_server.log 2>&1 &
SERVER_PID=$!

# 等待服务器启动（ChatTTS 加载模型需要 4-6 秒）
echo -e "${YELLOW}⏳ 等待 ChatTTS 模型加载...${NC}"
for i in {1..10}; do
    if lsof -i :8765 &> /dev/null; then
        break
    fi
    sleep 1
done

# 检查服务器是否成功启动
if lsof -i :8765 &> /dev/null; then
    echo -e "${GREEN}✅ 中央服务器已启动 (PID: $SERVER_PID)${NC}"
    echo -e "${BLUE}   监听端口: 8765${NC}"
    echo -e "${BLUE}   日志文件: /tmp/ws_server.log${NC}"
else
    echo -e "${RED}❌ 服务器启动失败${NC}"
    echo ""
    echo "请查看日志: tail /tmp/ws_server.log"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}📋 系统状态：${NC}"
echo ""
echo -e "  ${GREEN}✅${NC} 中央服务器运行中 (端口 8765)"
echo ""

# 检查 Cursor Hook 是否已安装
if [ -f "$PROJECT_DIR/cursor-injector/.installed" ]; then
    echo -e "  ${GREEN}✅${NC} Cursor Hook 已安装"
else
    echo -e "  ${YELLOW}⚠️${NC}  Cursor Hook 未安装"
    echo -e "     运行: ${BLUE}cd cursor-injector && ./install-v9.sh${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}🎯 下一步操作：${NC}"
echo ""
echo "  1️⃣  启动 Cursor IDE"
echo "     （Hook 会自动连接到服务器）"
echo ""
echo "  2️⃣  查看连接日志："
echo -e "     ${BLUE}tail -f /tmp/cursor_ortensia.log${NC}"
echo ""
echo "  3️⃣  发送测试命令："
echo -e "     ${BLUE}cd tests && python3 quick_test_central.py${NC}"
echo ""
echo "  4️⃣  查看服务器日志："
echo -e "     ${BLUE}tail -f /tmp/ws_server.log${NC}"
echo ""
echo "  5️⃣  停止所有服务："
echo -e "     ${BLUE}./scripts/STOP_ALL.sh${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✨ 中央服务器已就绪！${NC}"
echo ""
