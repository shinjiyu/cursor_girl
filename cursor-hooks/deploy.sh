#!/bin/bash
# Cursor Agent Hooks 部署脚本
# 将 Agent Hooks 部署到 ~/.cursor-agent/（全局安装）

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}"

# 目标目录（全局安装）
TARGET_DIR="${HOME}/.cursor-agent"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║        🤖 Cursor Agent Hooks 部署脚本                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

echo -e "${BLUE}📁 源目录:${NC} ${SOURCE_DIR}"
echo -e "${BLUE}📁 目标目录:${NC} ${TARGET_DIR}"
echo ""

# 检查目标目录
if [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}⚠️  目标目录 ~/.cursor-agent/ 已存在${NC}"
    echo -e "${YELLOW}   是否覆盖? [y/N]${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}ℹ️  部署已取消${NC}"
        exit 0
    fi
    echo ""
    echo -e "${YELLOW}🗑️  删除现有目录...${NC}"
    rm -rf "$TARGET_DIR"
fi

# 创建目标目录
echo -e "${GREEN}📦 创建目录结构...${NC}"
mkdir -p "$TARGET_DIR/hooks"
mkdir -p "$TARGET_DIR/lib"

# 复制文件
echo -e "${GREEN}📦 复制 Agent Hooks...${NC}"
cp -r "$SOURCE_DIR/hooks/"* "$TARGET_DIR/hooks/"
cp -r "$SOURCE_DIR/lib/"* "$TARGET_DIR/lib/"
cp "$SOURCE_DIR/hooks.json" "$TARGET_DIR/"

# 复制包装脚本（如果存在）
if [ -f "$SOURCE_DIR/run_hook.sh" ]; then
    echo -e "${GREEN}📦 复制包装脚本...${NC}"
    cp "$SOURCE_DIR/run_hook.sh" "$TARGET_DIR/"
fi

# 设置可执行权限
echo -e "${GREEN}🔧 设置可执行权限...${NC}"
chmod +x "$TARGET_DIR/hooks/"*.py
chmod +x "$TARGET_DIR/lib/"*.py 2>/dev/null || true

# 设置包装脚本权限
if [ -f "$TARGET_DIR/run_hook.sh" ]; then
    chmod +x "$TARGET_DIR/run_hook.sh"
    echo -e "${GREEN}✅ 包装脚本已部署: run_hook.sh${NC}"
fi

# 创建 ~/.cursor/hooks.json 符号链接
CURSOR_DIR="${HOME}/.cursor"
mkdir -p "$CURSOR_DIR"

if [ -f "$CURSOR_DIR/hooks.json" ] && [ ! -L "$CURSOR_DIR/hooks.json" ]; then
    echo -e "${YELLOW}⚠️  ~/.cursor/hooks.json 已存在${NC}"
    echo -e "${YELLOW}   创建备份: hooks.json.backup${NC}"
    cp "$CURSOR_DIR/hooks.json" "$CURSOR_DIR/hooks.json.backup"
fi

echo -e "${GREEN}🔗 创建配置符号链接...${NC}"
ln -sf "$TARGET_DIR/hooks.json" "$CURSOR_DIR/hooks.json"

echo ""
echo -e "${GREEN}✅ 部署完成！${NC}"
echo ""

# 显示已部署的 hooks
echo "📊 部署的 Agent Hooks:"
for hook in "$TARGET_DIR/hooks/"*.py; do
    if [ -f "$hook" ]; then
        hook_name=$(basename "$hook")
        hook_size=$(ls -lh "$hook" | awk '{print $5}')
        echo "   • $hook_name ($hook_size)"
    fi
done

hook_count=$(ls -1 "$TARGET_DIR/hooks/"*.py 2>/dev/null | wc -l)
echo ""
echo -e "${GREEN}📈 总计: $hook_count 个 Agent Hooks${NC}"
echo ""

# 使用说明
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                   📚 使用说明                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "1. 确保オルテンシア中央服务器运行中:"
echo "   cd <your-project>"
echo "   ./scripts/START_ALL.sh"
echo ""
echo "2. 重启 Cursor:"
echo "   完全退出 Cursor 并重新打开"
echo ""
echo "3. Agent Hooks 会自动激活:"
echo "   🤖 Agent 执行命令 → 自动审核"
echo "   📝 Agent 编辑文件 → 自动格式化"
echo "   🔐 Agent 读取敏感文件 → 需要确认"
echo "   🎉 Agent 完成任务 → オルテンシア 庆祝"
echo ""
echo "4. 查看日志:"
echo "   tail -f /tmp/cursor-agent-hooks.log"
echo ""
echo "5. 查看配置:"
echo "   cat ~/.cursor/hooks.json"
echo ""
echo "6. 测试 Hook:"
echo "   echo '{\"command\":\"ls -la\"}' | python3 ~/.cursor-agent/hooks/beforeShellExecution.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  状态: ✅ 部署成功"
echo "  配置: ~/.cursor/hooks.json"
echo "  日志: /tmp/cursor-agent-hooks.log"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
