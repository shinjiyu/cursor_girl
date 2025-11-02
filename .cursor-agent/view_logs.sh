#!/bin/bash
# Agent Hooks 日志查看工具

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

LOG_FILE="/tmp/cursor-agent-hooks.log"

show_menu() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║        📊 Agent Hooks 日志查看工具                       ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "1. 📄 查看最新 20 条日志"
    echo "2. 📜 查看所有日志"
    echo "3. 👁️  实时监控日志 (tail -f)"
    echo "4. 🔍 搜索日志"
    echo "5. 📊 统计调用次数"
    echo "6. ⏱️  查看最近一次调用"
    echo "7. 🧹 清空日志"
    echo "0. 🚪 退出"
    echo ""
    echo -n "请选择 [0-7]: "
}

view_recent() {
    echo ""
    echo -e "${CYAN}📄 最新 20 条日志:${NC}"
    echo ""
    tail -20 "$LOG_FILE" 2>/dev/null || echo "暂无日志"
}

view_all() {
    echo ""
    echo -e "${CYAN}📜 所有日志:${NC}"
    echo ""
    cat "$LOG_FILE" 2>/dev/null | less || echo "暂无日志"
}

monitor_live() {
    echo ""
    echo -e "${CYAN}👁️  实时监控日志 (Ctrl+C 停止):${NC}"
    echo ""
    tail -f "$LOG_FILE" 2>/dev/null
}

search_logs() {
    echo ""
    echo -n "🔍 请输入搜索关键词: "
    read keyword
    echo ""
    echo -e "${CYAN}搜索结果:${NC}"
    echo ""
    grep -i "$keyword" "$LOG_FILE" 2>/dev/null || echo "未找到匹配项"
}

show_stats() {
    echo ""
    echo -e "${CYAN}📊 Hooks 调用统计:${NC}"
    echo ""
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "暂无日志"
        return
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${YELLOW}Hook 名称                      调用次数${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    grep -o "\[.*\] Agent Hook 启动" "$LOG_FILE" | \
    sed 's/.*\[\(.*\)\] Agent Hook 启动/\1/' | \
    sort | uniq -c | \
    awk '{printf "%-30s %d\n", $2, $1}'
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    total=$(grep -c "Agent Hook 启动" "$LOG_FILE" 2>/dev/null || echo "0")
    success=$(grep -c "Hook 执行成功" "$LOG_FILE" 2>/dev/null || echo "0")
    failed=$(grep -c "Hook 执行失败" "$LOG_FILE" 2>/dev/null || echo "0")
    
    echo -e "${GREEN}总调用次数: $total${NC}"
    echo -e "${GREEN}成功: $success${NC}"
    if [ "$failed" -gt 0 ]; then
        echo -e "${RED}失败: $failed${NC}"
    else
        echo -e "失败: $failed"
    fi
}

show_last_call() {
    echo ""
    echo -e "${CYAN}⏱️  最近一次 Hook 调用:${NC}"
    echo ""
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "暂无日志"
        return
    fi
    
    # 查找最后一个"接收到 Cursor 调用"
    last_start=$(grep -n "接收到 Cursor 调用" "$LOG_FILE" | tail -1 | cut -d: -f1)
    
    if [ -z "$last_start" ]; then
        echo "未找到 Hook 调用记录"
        return
    fi
    
    # 从最后一次调用开始显示所有日志
    tail -n +$last_start "$LOG_FILE" | sed -n '/接收到 Cursor 调用/,/Hook 执行成功\|Hook 执行失败/p'
}

clear_logs() {
    echo ""
    echo -e "${YELLOW}⚠️  确认清空日志？ [y/N]${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        > "$LOG_FILE"
        echo -e "${GREEN}✅ 日志已清空${NC}"
    else
        echo "已取消"
    fi
}

# 主循环
while true; do
    show_menu
    read choice
    
    case $choice in
        1) view_recent ;;
        2) view_all ;;
        3) monitor_live ;;
        4) search_logs ;;
        5) show_stats ;;
        6) show_last_call ;;
        7) clear_logs ;;
        0) 
            echo ""
            echo -e "${GREEN}👋 再见！${NC}"
            echo ""
            exit 0
            ;;
        *)
            echo ""
            echo -e "${RED}❌ 无效选择，请重试${NC}"
            ;;
    esac
    
    echo ""
    echo -e "${BLUE}按 Enter 继续...${NC}"
    read
done

