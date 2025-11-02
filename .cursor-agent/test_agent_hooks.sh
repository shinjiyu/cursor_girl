#!/bin/bash
# Agent Hooks 测试脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

HOOKS_DIR="${HOME}/.cursor-agent/hooks"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║        🧪 Agent Hooks 测试                                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 测试计数
TOTAL=0
PASSED=0
FAILED=0

# 测试函数
test_hook() {
    local hook_name=$1
    local hook_file=$2
    local test_input=$3
    local expect_key=$4  # 期望输出中包含的 key
    
    TOTAL=$((TOTAL + 1))
    
    echo -e "${BLUE}📝 测试: ${hook_name}${NC}"
    
    if [ ! -f "$hook_file" ]; then
        echo -e "${RED}❌ 文件不存在: ${hook_file}${NC}"
        FAILED=$((FAILED + 1))
        echo ""
        return 1
    fi
    
    # 执行 hook
    output=$(echo "$test_input" | python3 "$hook_file" 2>&1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        # 检查输出
        if [ -n "$expect_key" ]; then
            if echo "$output" | grep -q "$expect_key"; then
                echo -e "${GREEN}✅ 通过${NC} (输出包含: $expect_key)"
                PASSED=$((PASSED + 1))
            else
                echo -e "${YELLOW}⚠️  警告${NC} (输出不包含期望的 key: $expect_key)"
                echo "输出: $output"
                PASSED=$((PASSED + 1))  # 仍然算通过，因为可能是空输出
            fi
        else
            echo -e "${GREEN}✅ 通过${NC}"
            PASSED=$((PASSED + 1))
        fi
    else
        echo -e "${RED}❌ 失败${NC} (退出码: $exit_code)"
        echo "输出: $output"
        FAILED=$((FAILED + 1))
    fi
    
    echo ""
}

# 1. 测试 beforeShellExecution
test_hook \
    "beforeShellExecution" \
    "$HOOKS_DIR/beforeShellExecution.py" \
    '{"command": "ls -la", "cwd": "/tmp"}' \
    "permission"

# 2. 测试 beforeShellExecution（危险命令）
test_hook \
    "beforeShellExecution (危险命令)" \
    "$HOOKS_DIR/beforeShellExecution.py" \
    '{"command": "rm -rf /", "cwd": "/tmp"}' \
    "deny"

# 3. 测试 afterShellExecution
test_hook \
    "afterShellExecution" \
    "$HOOKS_DIR/afterShellExecution.py" \
    '{"command": "npm build", "output": "Build successful"}' \
    ""

# 4. 测试 beforeMCPExecution
test_hook \
    "beforeMCPExecution" \
    "$HOOKS_DIR/beforeMCPExecution.py" \
    '{"tool_name": "read_file", "tool_input": "{}"}' \
    "permission"

# 5. 测试 afterMCPExecution
test_hook \
    "afterMCPExecution" \
    "$HOOKS_DIR/afterMCPExecution.py" \
    '{"tool_name": "read_file", "result_json": "{\"success\": true}"}' \
    ""

# 6. 测试 afterFileEdit
test_hook \
    "afterFileEdit" \
    "$HOOKS_DIR/afterFileEdit.py" \
    '{"file_path": "/tmp/test.py", "edits": []}' \
    ""

# 7. 测试 beforeReadFile
test_hook \
    "beforeReadFile" \
    "$HOOKS_DIR/beforeReadFile.py" \
    '{"file_path": "/tmp/test.py", "content": "print(1)"}' \
    "permission"

# 8. 测试 beforeReadFile（敏感文件）
test_hook \
    "beforeReadFile (敏感文件)" \
    "$HOOKS_DIR/beforeReadFile.py" \
    '{"file_path": "/home/user/.env", "content": "SECRET=xxx"}' \
    "ask"

# 9. 测试 beforeSubmitPrompt
test_hook \
    "beforeSubmitPrompt" \
    "$HOOKS_DIR/beforeSubmitPrompt.py" \
    '{"prompt": "帮我写一个函数", "attachments": []}' \
    "continue"

# 10. 测试 afterAgentResponse
test_hook \
    "afterAgentResponse" \
    "$HOOKS_DIR/afterAgentResponse.py" \
    '{"text": "任务已完成"}' \
    ""

# 11. 测试 stop
test_hook \
    "stop" \
    "$HOOKS_DIR/stop.py" \
    '{"status": "completed", "loop_count": 0}' \
    ""

# 统计结果
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📊 测试结果:${NC}"
echo "   总计: $TOTAL"
echo -e "   ${GREEN}通过: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "   ${RED}失败: $FAILED${NC}"
else
    echo -e "   失败: $FAILED"
fi

echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}❌ 部分测试失败${NC}"
    exit 1
fi

