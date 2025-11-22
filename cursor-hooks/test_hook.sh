#!/bin/bash

# 测试 Agent Hooks 脚本

echo "=========================================="
echo "🧪 测试 Agent Hooks"
echo "=========================================="
echo ""

# 测试数据
TEST_DATA='{
  "conversation_id": "test-conversation-123",
  "generation_id": "test-generation-456",
  "command": "echo Hello World",
  "output": "Hello World",
  "cwd": "/tmp",
  "hook_event_name": "afterShellExecution",
  "cursor_version": "2.0.43",
  "workspace_roots": ["/tmp"]
}'

echo "📝 测试数据:"
echo "$TEST_DATA" | jq '.'
echo ""

echo "🚀 执行 afterShellExecution Hook..."
echo ""

# 直接执行（已经有内置超时机制）
echo "$TEST_DATA" | python3 ./hooks/afterShellExecution.py

EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Hook 执行成功"
else
    echo "❌ Hook 执行失败 (exit code: $EXIT_CODE)"
fi
echo "=========================================="

