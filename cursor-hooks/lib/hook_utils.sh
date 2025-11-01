#!/bin/bash
# Cursor Hooks 工具函数库

# 获取 hooks 根目录
get_hooks_dir() {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
}

# 加载配置
load_config() {
    local hooks_dir=$(get_hooks_dir)
    local config_file="${hooks_dir}/.cursor/hooks/config.sh"
    
    if [ -f "$config_file" ]; then
        source "$config_file"
    else
        echo "⚠️  配置文件不存在: $config_file" >&2
        return 1
    fi
}

# 日志函数
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 加载配置获取日志路径
    load_config
    
    # 输出到控制台
    if [ "$DEBUG" = true ]; then
        echo "[${timestamp}] [${level}] ${message}"
    fi
    
    # 输出到日志文件
    echo "[${timestamp}] [${level}] ${message}" >> "${LOG_FILE}"
}

log_info() {
    log "INFO" "$@"
}

log_error() {
    log "ERROR" "$@"
}

log_debug() {
    if [ "$DEBUG" = true ]; then
        log "DEBUG" "$@"
    fi
}

# 发送事件到 WebSocket
send_to_websocket() {
    local event_type=$1
    local event_data=$2
    
    load_config
    
    if [ "$ENABLE_WEBSOCKET" != true ]; then
        log_debug "WebSocket 已禁用，跳过发送"
        return 0
    fi
    
    log_info "发送事件到オルテンシア: ${event_type}"
    
    # 使用 Python 脚本发送
    local python_script="${BRIDGE_PATH}/websocket_client.py"
    
    if [ ! -f "$python_script" ]; then
        log_error "WebSocket 客户端脚本不存在: ${python_script}"
        return 1
    fi
    
    # 激活虚拟环境并发送
    if [ -f "${VENV_PATH}/bin/activate" ]; then
        source "${VENV_PATH}/bin/activate"
        
        # 调用 Python 发送消息
        timeout ${HOOK_TIMEOUT} python "${python_script}" \
            --event "${event_type}" \
            --data "${event_data}" \
            2>> "${LOG_FILE}"
        
        local result=$?
        deactivate
        
        if [ $result -eq 0 ]; then
            log_info "✅ 事件发送成功"
        else
            log_error "❌ 事件发送失败 (exit code: ${result})"
        fi
        
        return $result
    else
        log_error "Python 虚拟环境不存在: ${VENV_PATH}"
        return 1
    fi
}

# 获取文件类型
get_file_type() {
    local filepath=$1
    echo "${filepath##*.}"
}

# 获取文件名
get_filename() {
    local filepath=$1
    echo "$(basename "${filepath}")"
}

# 获取相对路径
get_relative_path() {
    local filepath=$1
    local basepath=$2
    
    # 使用 realpath 如果可用
    if command -v realpath > /dev/null 2>&1; then
        realpath --relative-to="${basepath}" "${filepath}" 2>/dev/null || echo "${filepath}"
    else
        echo "${filepath}"
    fi
}

# 检查是否在 Git 仓库中
is_git_repo() {
    git rev-parse --git-dir > /dev/null 2>&1
    return $?
}

# 获取 Git 信息
get_git_info() {
    if is_git_repo; then
        local branch=$(git branch --show-current 2>/dev/null)
        local commit=$(git rev-parse --short HEAD 2>/dev/null)
        echo "branch=${branch},commit=${commit}"
    else
        echo "not_a_git_repo"
    fi
}

# JSON 转义
json_escape() {
    local string="$1"
    # 转义特殊字符
    string="${string//\\/\\\\}"  # 反斜杠
    string="${string//\"/\\\"}"  # 双引号
    string="${string//$'\n'/\\n}"  # 换行
    string="${string//$'\r'/\\r}"  # 回车
    string="${string//$'\t'/\\t}"  # 制表符
    echo "$string"
}

# 构建 JSON 消息
build_json_message() {
    local event_type=$1
    shift
    
    local json='{'
    json+="\"type\":\"${event_type}\","
    json+="\"timestamp\":$(date +%s),"
    json+="\"data\":{"
    
    # 添加键值对
    local first=true
    while [ $# -gt 0 ]; do
        if [ "$first" = true ]; then
            first=false
        else
            json+=","
        fi
        
        local key=$1
        local value=$(json_escape "$2")
        json+="\"${key}\":\"${value}\""
        
        shift 2
    done
    
    json+="}}"
    echo "$json"
}

# 初始化日志
init_log() {
    load_config
    
    # 确保日志目录存在
    local log_dir=$(dirname "${LOG_FILE}")
    mkdir -p "${log_dir}" 2>/dev/null
    
    # 创建日志文件
    touch "${LOG_FILE}" 2>/dev/null
    
    log_info "========================================="
    log_info "Cursor Hook 启动"
    log_info "========================================="
}

