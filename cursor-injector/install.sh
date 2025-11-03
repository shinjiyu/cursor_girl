#!/bin/bash

# ============================================================================
# Ortensia Cursor Injector - 安装脚本
# ============================================================================

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "============================================================================"
echo "  🎉 Ortensia Cursor Injector - 安装"
echo "============================================================================"
echo ""

# ========== 配置 ==========

CURSOR_APP="/Applications/Cursor.app"
CURSOR_RESOURCES="$CURSOR_APP/Contents/Resources/app"
MAIN_JS="$CURSOR_RESOURCES/out/main.js"
BACKUP_JS="$MAIN_JS.backup"
INJECTOR_JS="$CURSOR_RESOURCES/out/ortensia-injector.js"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_INJECTOR="$SCRIPT_DIR/ortensia-injector.js"

# ========== 检查 ==========

echo -e "${BLUE}[1/6]${NC} 检查 Cursor..."

if [ ! -d "$CURSOR_APP" ]; then
    echo -e "${RED}❌ 找不到 Cursor.app${NC}"
    echo "   请确认 Cursor 已安装在 /Applications/"
    exit 1
fi

echo -e "${GREEN}✅ 找到 Cursor.app${NC}"

if [ ! -f "$MAIN_JS" ]; then
    echo -e "${RED}❌ 找不到 main.js${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 找到 main.js${NC}"
echo ""

# ========== 检查是否已安装 ==========

if grep -q "ortensia-injector" "$MAIN_JS" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Ortensia Injector 已经安装${NC}"
    echo ""
    read -p "是否重新安装? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消安装"
        exit 0
    fi
    
    # 恢复备份
    if [ -f "$BACKUP_JS" ]; then
        echo -e "${BLUE}♻️  恢复备份...${NC}"
        cp "$BACKUP_JS" "$MAIN_JS"
    fi
fi

# ========== 备份 ==========

echo -e "${BLUE}[2/6]${NC} 备份原始文件..."

if [ ! -f "$BACKUP_JS" ]; then
    cp "$MAIN_JS" "$BACKUP_JS"
    echo -e "${GREEN}✅ 已备份到: main.js.backup${NC}"
else
    echo -e "${YELLOW}⚠️  备份已存在，跳过${NC}"
fi
echo ""

# ========== 复制注入文件 ==========

echo -e "${BLUE}[3/6]${NC} 复制注入文件..."

if [ ! -f "$SOURCE_INJECTOR" ]; then
    echo -e "${RED}❌ 找不到 ortensia-injector.js${NC}"
    exit 1
fi

cp "$SOURCE_INJECTOR" "$INJECTOR_JS"
echo -e "${GREEN}✅ 已复制到: $INJECTOR_JS${NC}"
echo ""

# ========== 注入 main.js ==========

echo -e "${BLUE}[4/6]${NC} 注入 main.js..."

# 在 main.js 开头添加动态导入
cat > "$MAIN_JS" << EOF
// ============================================================================
// Ortensia Injector - 注入点
// 安装时间: $(date)
// ============================================================================

// ES Module 兼容：使用动态 import
import('./ortensia-injector.js').catch(err => {
    console.error('❌ Failed to load Ortensia Injector:', err);
});

// ============================================================================
// 原始 main.js 代码
// ============================================================================

EOF

cat "$BACKUP_JS" >> "$MAIN_JS"

echo -e "${GREEN}✅ 注入完成${NC}"
echo ""

# ========== 重新签名 ==========

echo -e "${BLUE}[5/6]${NC} 重新签名应用..."

# 移除旧签名
codesign --remove-signature "$CURSOR_APP" 2>/dev/null || true

# 重新签名（ad-hoc 签名）
if codesign --force --deep --sign - "$CURSOR_APP" 2>/dev/null; then
    echo -e "${GREEN}✅ 签名完成${NC}"
else
    echo -e "${YELLOW}⚠️  签名失败（不影响使用）${NC}"
fi
echo ""

# ========== 完成 ==========

echo -e "${BLUE}[6/6]${NC} 安装完成！"
echo ""
echo "============================================================================"
echo -e "${GREEN}✅ Ortensia Injector 已成功安装${NC}"
echo "============================================================================"
echo ""
echo "📝 安装信息:"
echo "   - 注入文件: $INJECTOR_JS"
echo "   - 备份文件: $BACKUP_JS"
echo "   - WebSocket 端口: 9224"
echo ""
echo "🚀 下一步:"
echo "   1. 重启 Cursor"
echo "   2. 打开 DevTools (Cmd+Shift+P → Toggle Developer Tools)"
echo "   3. 查看 Console，应该看到 Ortensia Injector 启动信息"
echo "   4. 运行 Python 客户端连接:"
echo "      cd ../cursor-injector"
echo "      python3 ortensia_cursor_client.py"
echo ""
echo "💡 测试命令:"
echo "   python3 ortensia_cursor_client.py ping"
echo ""
echo "🗑️  卸载:"
echo "   ./uninstall.sh"
echo ""

