#!/bin/bash
# Cursor Hooks 卸载脚本
# 从项目中移除 Cursor Hooks

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认目标目录为当前目录
TARGET_DIR="${1:-.}"
TARGET_CURSOR_DIR="${TARGET_DIR}/.cursor"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║        🗑️  Cursor Hooks 卸载脚本                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 显示卸载信息
echo -e "${BLUE}📁 目标目录:${NC} ${TARGET_DIR}"
echo -e "${BLUE}📁 将删除:${NC} ${TARGET_CURSOR_DIR}"
echo ""

# 检查目标 .cursor 目录是否存在
if [ ! -d "$TARGET_CURSOR_DIR" ]; then
    echo -e "${YELLOW}⚠️  .cursor/ 目录不存在，无需卸载${NC}"
    exit 0
fi

# 显示要删除的内容
echo -e "${YELLOW}📊 将要删除的 Hooks:${NC}"
if [ -d "${TARGET_CURSOR_DIR}/hooks" ]; then
    ls -lh "${TARGET_CURSOR_DIR}/hooks/" | grep -v "^total" | awk '{print "   • " $9 " (" $5 ")"}'
    HOOK_COUNT=$(ls -1 "${TARGET_CURSOR_DIR}/hooks/" | grep -v config.sh | wc -l | tr -d ' ')
    echo ""
    echo -e "${YELLOW}   总计: ${HOOK_COUNT} 个 Hooks${NC}"
else
    echo -e "${YELLOW}   (hooks 目录不存在)${NC}"
fi

# 确认删除
echo ""
echo -e "${RED}⚠️  确认删除 .cursor/ 目录? [y/N]${NC}"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${BLUE}ℹ️  卸载已取消${NC}"
    exit 0
fi

# 删除 .cursor 目录
echo ""
echo -e "${YELLOW}🗑️  删除 .cursor/ 目录...${NC}"
rm -rf "$TARGET_CURSOR_DIR"

# 验证卸载
echo ""
if [ ! -d "$TARGET_CURSOR_DIR" ]; then
    echo -e "${GREEN}✅ 卸载完成！${NC}"
    echo ""
    echo "Cursor Hooks 已从项目中移除。"
else
    echo -e "${RED}❌ 卸载失败: 目录仍然存在${NC}"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  状态: ✅ 卸载成功"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

