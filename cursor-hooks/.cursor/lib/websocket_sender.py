#!/usr/bin/env python3
"""
WebSocket 消息发送器 - 用于 Cursor Hooks
从命令行接收事件数据，发送到オルテンシア的 WebSocket 服务器
"""

import asyncio
import json
import sys
import argparse
from pathlib import Path

# 添加 bridge 路径以导入 websocket_client
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "bridge"))

try:
    from websocket_client import WebSocketClient
except ImportError:
    print("❌ 无法导入 WebSocketClient，请确保 bridge/websocket_client.py 存在", file=sys.stderr)
    sys.exit(1)


async def send_hook_event(event_type: str, event_data: dict):
    """
    发送 Hook 事件到 WebSocket 服务器
    
    Args:
        event_type: 事件类型（如 'file_save', 'git_commit'）
        event_data: 事件数据字典
    """
    client = WebSocketClient()
    
    try:
        # 连接到服务器
        await client.connect()
        
        # 根据事件类型确定消息内容和情绪
        text, emotion = get_message_for_event(event_type, event_data)
        
        # 使用 send_emotion 方法发送
        success = await client.send_emotion(
            text=text,
            emotion=emotion,
            role='assistant',
            event_type=event_type
        )
        
        if success:
            print(f"✅ 事件已发送: {event_type}")
        else:
            print(f"❌ 事件发送失败: {event_type}", file=sys.stderr)
            sys.exit(1)
        
        # 等待一小段时间确保消息发送
        await asyncio.sleep(0.5)
        
    except Exception as e:
        print(f"❌ 发送失败: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await client.close()


def get_message_for_event(event_type: str, event_data: dict) -> tuple[str, str]:
    """
    根据事件类型生成消息和情绪
    
    Args:
        event_type: 事件类型
        event_data: 事件数据
        
    Returns:
        (消息文本, 情绪类型)
    """
    # 默认消息和情绪
    messages = {
        # 文件操作
        'file_save': ('保存成功~', 'neutral'),
        'file_create': ('新文件创建成功！', 'happy'),
        'file_delete': ('文件已删除', 'neutral'),
        
        # Git 操作
        'pre_commit': ('准备提交...', 'neutral'),
        'git_commit': ('太棒了！代码提交成功~', 'happy'),
        'post_push': ('Push 完成！辛苦了~', 'happy'),
        'git_merge': ('分支合并成功！', 'happy'),
        'git_conflict': ('遇到冲突了...我们一起解决~', 'sad'),
        
        # 构建
        'build_start': ('开始构建...', 'neutral'),
        'build_success': ('构建成功！', 'happy'),
        'build_error': ('构建失败了...别担心，我们一起修复它~', 'sad'),
        
        # 测试
        'test_start': ('开始测试...', 'neutral'),
        'test_pass': ('测试通过！你真厉害！', 'excited'),
        'test_fail': ('测试失败了...我们再检查一下~', 'sad'),
        
        # 错误
        'syntax_error': ('语法错误...让我帮你看看~', 'sad'),
        'runtime_error': ('运行时错误...别担心，我们一起调试~', 'sad'),
        'error': ('出错了...别担心，我们一起修复它~', 'sad'),
        
        # 调试
        'debug_start': ('开始调试...', 'neutral'),
        'bug_found': ('找到 Bug 了！', 'surprised'),
        'bug_fixed': ('Bug 修复成功！', 'happy'),
        
        # AI 操作
        'ai_start': ('AI 开始工作了...', 'neutral'),
        'ai_complete': ('AI 完成了！', 'happy'),
        'ai_accept': ('接受 AI 建议~', 'happy'),
        'ai_reject': ('拒绝 AI 建议', 'neutral'),
        
        # 性能
        'performance_slow': ('性能有点慢...我们优化一下~', 'sad'),
        'performance_improved': ('性能提升了！', 'happy'),
        
        # 其他
        'work_start': ('开始工作！加油~', 'happy'),
        'work_break': ('休息一下吧~', 'relaxed'),
        'work_complete': ('工作完成！辛苦了~', 'happy'),
        'celebration': ('太棒了！值得庆祝！', 'excited'),
    }
    
    # 如果有自定义消息，使用自定义消息
    if 'message' in event_data:
        # 根据事件类型推断情绪
        emotion = 'neutral'
        if 'error' in event_type or 'fail' in event_type:
            emotion = 'sad'
        elif 'success' in event_type or 'pass' in event_type or 'complete' in event_type:
            emotion = 'happy'
        return (event_data['message'], emotion)
    
    # 从预定义消息中获取
    if event_type in messages:
        return messages[event_type]
    
    # 默认消息
    return (f'收到事件: {event_type}', 'neutral')


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='发送 Cursor Hook 事件到オルテンシア')
    
    parser.add_argument(
        '--event',
        required=True,
        help='事件类型（如 file_save, git_commit）'
    )
    
    parser.add_argument(
        '--file',
        help='文件路径'
    )
    
    parser.add_argument(
        '--message',
        help='消息内容'
    )
    
    parser.add_argument(
        '--data',
        help='JSON 格式的额外数据'
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 构建事件数据
    event_data = {}
    
    if args.file:
        event_data['file'] = args.file
        event_data['filename'] = Path(args.file).name
        event_data['extension'] = Path(args.file).suffix
    
    if args.message:
        event_data['message'] = args.message
    
    # 如果有额外的 JSON 数据，合并进去
    if args.data:
        try:
            extra_data = json.loads(args.data)
            event_data.update(extra_data)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}", file=sys.stderr)
            sys.exit(1)
    
    # 发送事件
    try:
        asyncio.run(send_hook_event(args.event, event_data))
    except KeyboardInterrupt:
        print("\n⚠️  操作已取消", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()

