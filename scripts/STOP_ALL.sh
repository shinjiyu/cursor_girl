#!/bin/bash
# Ortensia V9 - 停止所有服务

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║          🌸 Ortensia V9 - 停止服务                               ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# 停止中央服务器
if lsof -i :8765 &> /dev/null; then
    echo -e "${BLUE}🛑 正在停止中央服务器...${NC}"
    
    # 获取 PID
    PID=$(lsof -ti :8765)
    
    if [ ! -z "$PID" ]; then
        kill -15 $PID 2>/dev/null
        sleep 1
        
        # 如果还在运行，强制杀死
        if lsof -i :8765 &> /dev/null; then
            kill -9 $PID 2>/dev/null
            echo -e "${YELLOW}   使用强制停止${NC}"
        fi
        
        echo -e "${GREEN}✅ 中央服务器已停止${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  中央服务器未运行${NC}"
fi

echo ""

# 停止所有 WebSocket 服务器进程（包括 ChatTTS 虚拟环境）
if pgrep -f "websocket_server.py" > /dev/null; then
    echo -e "${BLUE}🛑 停止 WebSocket 服务器 (TTS)...${NC}"
    # 使用精确匹配，只杀死 websocket_server.py 进程，不影响 Cursor
    pkill -f "python.*websocket_server.py"
    sleep 1
    
    # 确认已停止
    if pgrep -f "websocket_server.py" > /dev/null; then
        echo -e "${YELLOW}   使用强制停止${NC}"
        pkill -9 -f "python.*websocket_server.py"
    fi
    
    echo -e "${GREEN}✅ WebSocket 服务器已停止${NC}"
else
    echo -e "${YELLOW}⚠️  WebSocket 服务器未运行${NC}"
fi

echo ""
echo -e "${YELLOW}ℹ️  注意: 此脚本不会关闭 Cursor IDE${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}📋 当前状态：${NC}"
echo ""

# 检查端口
if lsof -i :8765 &> /dev/null; then
    echo -e "  ${RED}❌${NC} 端口 8765 仍被占用"
else
    echo -e "  ${GREEN}✅${NC} 端口 8765 已释放"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}💡 提示：${NC}"
echo ""
echo "  - ✅ Cursor IDE 不会被关闭（只停止中央服务器）"
echo "  - 💡 Cursor Hook 会在 Cursor 关闭时自动停止"
echo "  - 🔄 如需重启服务: ./scripts/START_ALL.sh"
echo "  - ⚠️  如需关闭 Cursor: Cmd+Q 或 pkill -f Cursor.app"
echo ""
echo -e "${GREEN}✨ 完成！${NC}"
echo ""
