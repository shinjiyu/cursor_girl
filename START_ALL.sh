#!/bin/bash
# 一键启动 オルテンシア 完整系统

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║            💜 オルテンシア AI 助手 - 启动系统                    ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# 检查是否已有服务在运行
if lsof -i :3000 &> /dev/null; then
    echo -e "${YELLOW}⚠️  端口 3000 已被占用（Next.js 可能已在运行）${NC}"
fi

if lsof -i :8000 &> /dev/null; then
    echo -e "${GREEN}✅ WebSocket 服务器已在运行${NC}"
else
    echo -e "${BLUE}🚀 启动 WebSocket 服务器...${NC}"
    cd "/Users/user/Documents/ cursorgirl/bridge"
    source venv/bin/activate
    python websocket_server.py > /tmp/ortensia-websocket.log 2>&1 &
    sleep 2
    echo -e "${GREEN}✅ WebSocket 服务器已启动${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${PURPLE}📋 系统状态：${NC}"
echo ""

# 检查各个服务
if lsof -i :3000 &> /dev/null; then
    echo -e "  ${GREEN}✅${NC} Next.js 开发服务器 (端口 3000)"
else
    echo -e "  ${YELLOW}⚠️${NC}  Next.js 开发服务器 (需要手动启动)"
    echo -e "     ${BLUE}cd aituber-kit && npm run dev${NC}"
fi

if lsof -i :8000 &> /dev/null; then
    echo -e "  ${GREEN}✅${NC} WebSocket 服务器 (端口 8000)"
else
    echo -e "  ${YELLOW}⚠️${NC}  WebSocket 服务器未运行"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${PURPLE}🎯 下一步操作：${NC}"
echo ""
echo "  1️⃣  启动 Electron 悬浮窗（オルテンシア）："
echo -e "     ${BLUE}cd aituber-kit && npm run assistant${NC}"
echo ""
echo "  2️⃣  测试 Event Bridge："
echo -e "     ${BLUE}cd bridge && ./run_tests.sh${NC}"
echo ""
echo "  3️⃣  或运行快速测试："
echo -e "     ${BLUE}cd bridge && source venv/bin/activate && python test_single_events.py${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✨ 系统准备就绪！${NC}"
echo ""

