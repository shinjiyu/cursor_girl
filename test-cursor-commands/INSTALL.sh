#!/bin/bash

echo "🔧 安装 Test Cursor Commands 扩展"
echo ""

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误: 请在 test-cursor-commands 目录中运行此脚本"
    exit 1
fi

# 检查 vsce 是否安装
if ! command -v vsce &> /dev/null; then
    echo "📦 安装 @vscode/vsce..."
    npm install -g @vscode/vsce
fi

# 打包扩展
echo "📦 打包扩展..."
vsce package --allow-missing-repository

# 查找生成的 .vsix 文件
VSIX_FILE=$(ls -t *.vsix 2>/dev/null | head -1)

if [ -z "$VSIX_FILE" ]; then
    echo "❌ 打包失败"
    exit 1
fi

echo "✅ 生成文件: $VSIX_FILE"
echo ""
echo "📝 下一步:"
echo ""
echo "1. 在 Cursor 中打开 Extensions 面板"
echo "2. 点击右上角的 '...' 菜单"
echo "3. 选择 'Install from VSIX...'"
echo "4. 选择: $(pwd)/$VSIX_FILE"
echo "5. 重启 Cursor"
echo ""
echo "或者运行:"
echo "  open -a Cursor $VSIX_FILE"
echo ""

