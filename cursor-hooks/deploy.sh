#!/bin/bash
# Cursor Hooks 部署脚本
# 将 cursor-hooks/.cursor 部署到目标项目

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/.cursor"

# 默认目标目录为当前目录
TARGET_DIR="${1:-.}"
TARGET_CURSOR_DIR="${TARGET_DIR}/.cursor"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║        🎣 Cursor Hooks 部署脚本                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 检查源目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}❌ 错误: 源目录不存在: ${SOURCE_DIR}${NC}"
    exit 1
fi

# 显示部署信息
echo -e "${BLUE}📁 源目录:${NC} ${SOURCE_DIR}"
echo -e "${BLUE}📁 目标目录:${NC} ${TARGET_DIR}"
echo -e "${BLUE}📁 目标 Cursor 目录:${NC} ${TARGET_CURSOR_DIR}"
echo ""

# 检查目标目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}❌ 错误: 目标目录不存在: ${TARGET_DIR}${NC}"
    exit 1
fi

# 如果目标 .cursor 目录已存在，询问是否覆盖
if [ -d "$TARGET_CURSOR_DIR" ]; then
    echo -e "${YELLOW}⚠️  目标目录 .cursor/ 已存在${NC}"
    echo -e "${YELLOW}   是否覆盖? [y/N]${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}ℹ️  部署已取消${NC}"
        exit 0
    fi
    echo ""
    echo -e "${YELLOW}🗑️  删除现有 .cursor/ 目录...${NC}"
    rm -rf "$TARGET_CURSOR_DIR"
fi

# 复制 hooks 到目标目录
echo -e "${GREEN}📦 复制 Cursor Hooks...${NC}"
cp -r "$SOURCE_DIR" "$TARGET_DIR/"

# 设置可执行权限
echo -e "${GREEN}🔧 设置可执行权限...${NC}"
chmod +x "${TARGET_CURSOR_DIR}/hooks/"*

# 验证部署
echo ""
echo -e "${GREEN}✅ 部署完成！${NC}"
echo ""
echo "📊 部署的 Hooks:"
ls -lh "${TARGET_CURSOR_DIR}/hooks/" | grep -v "^total" | awk '{print "   • " $9 " (" $5 ")"}'

# 统计 hooks 数量
HOOK_COUNT=$(ls -1 "${TARGET_CURSOR_DIR}/hooks/" | grep -v config.sh | wc -l | tr -d ' ')
echo ""
echo -e "${GREEN}📈 总计: ${HOOK_COUNT} 个 Hooks${NC}"

# 显示使用说明
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                   📚 使用说明                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "1. 确保オルテンシア服务运行中:"
echo "   cd /Users/user/Documents/ cursorgirl"
echo "   ./START_ALL.sh"
echo ""
echo "2. 在 Cursor 中打开项目:"
echo "   cursor ${TARGET_DIR}"
echo ""
echo "3. 正常编码，オルテンシア 会自动响应:"
echo "   💾 保存文件 → \"保存成功~\" 😊"
echo "   🔄 Git commit → \"太棒了！代码提交成功~\" 🎉"
echo "   🏗️ 构建成功 → \"构建成功！\" 😊"
echo "   🧪 测试通过 → \"测试通过！你真厉害！\" 🎊"
echo ""
echo "4. 查看日志:"
echo "   tail -f /tmp/cursor-hooks.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  版本: 1.2.0"
echo "  Hooks: ${HOOK_COUNT} 个"
echo "  状态: ✅ 部署成功"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

