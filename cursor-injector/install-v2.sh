#!/bin/bash
# ============================================================================
# Ortensia Cursor Injector v2 - 安装脚本
# 使用 CommonJS require() 版本
# ============================================================================

set -e

# ========== 颜色 ==========
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ========== 配置 ==========
CURSOR_APP="/Applications/Cursor.app"
CURSOR_RESOURCES="$CURSOR_APP/Contents/Resources/app"
OUT_DIR="$CURSOR_RESOURCES/out"
MAIN_JS="$OUT_DIR/main.js"
BACKUP_JS="$OUT_DIR/main.js.ortensia.backup"
INJECTOR_JS="$OUT_DIR/ortensia-injector.js"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_INJECTOR="$SCRIPT_DIR/ortensia-injector-v2.js"

# ========== 检查 ==========
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} Ortensia Cursor Injector v2${NC}"
echo -e "${BLUE} Installation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ ! -d "$CURSOR_APP" ]; then
    echo -e "${RED}❌ Cursor.app not found!${NC}"
    echo "   Expected: $CURSOR_APP"
    exit 1
fi

if [ ! -f "$MAIN_JS" ]; then
    echo -e "${RED}❌ main.js not found!${NC}"
    echo "   Expected: $MAIN_JS"
    exit 1
fi

echo -e "${GREEN}✅ Cursor found${NC}"
echo ""

# ========== 备份检查 ==========
if [ -f "$BACKUP_JS" ]; then
    echo -e "${YELLOW}⚠️  Previous backup found${NC}"
    echo "   Do you want to:"
    echo "   1) Use existing backup (recommended)"
    echo "   2) Create new backup (overwrite old)"
    echo ""
    read -p "   Choice (1/2): " choice
    
    if [ "$choice" = "2" ]; then
        echo -e "${BLUE}[1/6]${NC} Creating new backup..."
        cp "$MAIN_JS" "$BACKUP_JS"
        echo -e "${GREEN}✅ Backup created${NC}"
    else
        echo -e "${BLUE}[1/6]${NC} Using existing backup..."
    fi
else
    echo -e "${BLUE}[1/6]${NC} Backing up main.js..."
    cp "$MAIN_JS" "$BACKUP_JS"
    echo -e "${GREEN}✅ Backup created${NC}"
fi
echo ""

# ========== 复制注入器 ==========
echo -e "${BLUE}[2/6]${NC} Copying injector..."
cp "$SOURCE_INJECTOR" "$INJECTOR_JS"
echo -e "${GREEN}✅ Injector copied${NC}"
echo ""

# ========== 注入 main.js ==========
echo -e "${BLUE}[3/6]${NC} Injecting into main.js..."

# 由于 main.js 是 ES Module，我们需要特殊处理
# 在开头添加一个立即执行的动态 import
cat > "$MAIN_JS" << 'EOF'
// ============================================================================
// Ortensia Injector v2 - 注入点
// ============================================================================

// 使用 eval + require 绕过 ES Module 限制
try {
    const fs = eval('require')('fs');
    const path = eval('require')('path');
    const injectorPath = path.join(__dirname, 'ortensia-injector.js');
    const injectorCode = fs.readFileSync(injectorPath, 'utf8');
    eval(injectorCode);
} catch (err) {
    console.error('❌ Failed to load Ortensia Injector:', err);
}

// ============================================================================
// 原始 main.js 代码
// ============================================================================

EOF

cat "$BACKUP_JS" >> "$MAIN_JS"

echo -e "${GREEN}✅ Injection complete${NC}"
echo ""

# ========== 重签名 ==========
echo -e "${BLUE}[4/6]${NC} Re-signing Cursor.app..."

codesign --force --deep --sign - "$CURSOR_APP" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Code signing failed (this is usually OK)${NC}"
}

echo -e "${GREEN}✅ Done${NC}"
echo ""

# ========== 完成 ==========
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN} ✅ Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. ${YELLOW}Quit Cursor completely${NC} (Cmd+Q)"
echo "  2. ${YELLOW}Restart Cursor${NC}"
echo "  3. Open DevTools (Cmd+Shift+P → 'Toggle Developer Tools')"
echo "  4. Check Console for:"
echo "     ${GREEN}✅ Ortensia Cursor Injector v2${NC}"
echo ""
echo "  5. Test connection:"
echo "     ${BLUE}./ortensia-cursor.sh ping${NC}"
echo ""

# ========== 提示 ==========
echo -e "${YELLOW}💡 Troubleshooting:${NC}"
echo "  - If no logs appear: check DevTools Console for errors"
echo "  - To uninstall: ./uninstall.sh"
echo "  - Backup location: $BACKUP_JS"
echo ""

