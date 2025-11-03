#!/bin/bash

# ============================================================================
# Ortensia Cursor Injector - 卸载脚本
# ============================================================================

set -e

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "============================================================================"
echo "  🗑️  Ortensia Cursor Injector - 卸载"
echo "============================================================================"
echo ""

# 配置
CURSOR_APP="/Applications/Cursor.app"
CURSOR_RESOURCES="$CURSOR_APP/Contents/Resources/app"
MAIN_JS="$CURSOR_RESOURCES/out/main.js"
BACKUP_JS="$MAIN_JS.backup"
INJECTOR_JS="$CURSOR_RESOURCES/out/ortensia-injector.js"

# 检查
if [ ! -d "$CURSOR_APP" ]; then
    echo -e "${RED}❌ 找不到 Cursor.app${NC}"
    exit 1
fi

# 确认
read -p "确定要卸载 Ortensia Injector 吗? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消卸载"
    exit 0
fi

echo ""

# 恢复 main.js
echo -e "${BLUE}[1/3]${NC} 恢复原始文件..."

if [ -f "$BACKUP_JS" ]; then
    cp "$BACKUP_JS" "$MAIN_JS"
    echo -e "${GREEN}✅ 已恢复 main.js${NC}"
    
    # 删除备份
    rm "$BACKUP_JS"
    echo -e "${GREEN}✅ 已删除备份文件${NC}"
else
    echo -e "${YELLOW}⚠️  找不到备份文件${NC}"
fi
echo ""

# 删除注入文件
echo -e "${BLUE}[2/3]${NC} 删除注入文件..."

if [ -f "$INJECTOR_JS" ]; then
    rm "$INJECTOR_JS"
    echo -e "${GREEN}✅ 已删除 ortensia-injector.js${NC}"
else
    echo -e "${YELLOW}⚠️  注入文件不存在${NC}"
fi
echo ""

# 重新签名
echo -e "${BLUE}[3/3]${NC} 重新签名..."

codesign --remove-signature "$CURSOR_APP" 2>/dev/null || true
if codesign --force --deep --sign - "$CURSOR_APP" 2>/dev/null; then
    echo -e "${GREEN}✅ 签名完成${NC}"
else
    echo -e "${YELLOW}⚠️  签名失败（不影响使用）${NC}"
fi
echo ""

# 完成
echo "============================================================================"
echo -e "${GREEN}✅ 卸载完成${NC}"
echo "============================================================================"
echo ""
echo "🚀 重启 Cursor 生效"
echo ""

