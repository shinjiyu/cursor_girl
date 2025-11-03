#!/bin/bash
# Ortensia Cursor Client 启动脚本
# 使用 bridge/venv 的 Python 环境

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$PROJECT_ROOT/bridge/venv/bin/python3"

# 检查虚拟环境
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ 找不到虚拟环境: $VENV_PYTHON"
    echo "请先创建虚拟环境:"
    echo "  cd $PROJECT_ROOT/bridge"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install websockets"
    exit 1
fi

# 运行客户端
exec "$VENV_PYTHON" "$SCRIPT_DIR/ortensia_cursor_client.py" "$@"

