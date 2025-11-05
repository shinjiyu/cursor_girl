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

# 停止其他可能的 websocket_server 进程
if pgrep -f "websocket_server.py" > /dev/null; then
    echo -e "${BLUE}🛑 清理其他 WebSocket 进程...${NC}"
    pkill -f "websocket_server.py"
    echo -e "${GREEN}✅ 已清理${NC}"
fi

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
echo "  - Cursor Hook 会在 Cursor 关闭时自动停止"
echo "  - 如需重启服务: ./scripts/START_ALL.sh"
echo ""
echo -e "${GREEN}✨ 完成！${NC}"
echo ""
