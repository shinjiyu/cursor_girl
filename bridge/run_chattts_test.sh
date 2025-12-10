#!/bin/bash
#
# 运行 ChatTTS 集成测试
# 
# 使用 ChatTTS 的虚拟环境来运行测试

set -e

# ChatTTS 虚拟环境路径
CHATTTS_VENV="/Users/user/Documents/tts/chattts/venv"

# 检查虚拟环境是否存在
if [ ! -d "$CHATTTS_VENV" ]; then
    echo "❌ 错误: ChatTTS 虚拟环境不存在: $CHATTTS_VENV"
    echo "   请先安装 ChatTTS"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=" 
echo "🎤 使用 ChatTTS 虚拟环境运行测试"
echo "="
echo ""
echo "虚拟环境: $CHATTTS_VENV"
echo "测试脚本: $SCRIPT_DIR/test_chattts_integration.py"
echo ""

# 激活虚拟环境并运行测试
source "$CHATTTS_VENV/bin/activate"
cd "$SCRIPT_DIR"
python test_chattts_integration.py

echo ""
echo "✅ 测试完成"









