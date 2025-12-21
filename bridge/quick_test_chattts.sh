#!/bin/bash
#
# ChatTTS 快速测试脚本
#
# 快速测试 ChatTTS 是否正常工作

set -e

CHATTTS_VENV="/Users/user/Documents/tts/chattts/venv"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=========================================="
echo "🎤 ChatTTS 快速测试"
echo "=========================================="
echo ""

# 检查虚拟环境
if [ ! -d "$CHATTTS_VENV" ]; then
    echo "❌ ChatTTS 虚拟环境不存在: $CHATTTS_VENV"
    exit 1
fi

# 激活虚拟环境
source "$CHATTTS_VENV/bin/activate"
cd "$SCRIPT_DIR"

# 快速测试
python -c "
from tts_manager import TTSManager

print('初始化 ChatTTS...')
manager = TTSManager()
manager.initialize('chattts')

print('生成测试语音...')
audio = manager.generate('你好，ChatTTS 测试成功！')
print(f'✅ 生成成功: {audio}')
print('')
print('🎉 ChatTTS 工作正常！')
"

echo ""
echo "=========================================="
echo "✅ 测试完成"
echo "=========================================="




















