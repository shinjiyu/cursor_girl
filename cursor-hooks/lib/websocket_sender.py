#!/usr/bin/env python3
"""
WebSocket 消息发送器 - 用于 Cursor Hooks
从命令行接收事件数据，发送到 Ortensia 中央服务器

完全独立的实现，不依赖其他模块
"""

import asyncio
import json
import sys
import argparse
import os
from pathlib import Path
from datetime import datetime

try:
    import websockets
except ImportError:
    print("❌ 缺少 websockets 库，请安装: pip install websockets", file=sys.stderr)
    sys.exit(1)

def _read_server_url_from_file() -> str | None:
    """
    读取中央服务器地址（用于 GUI 启动/无环境变量场景）。

    优先尝试：
    - ~/Library/Application Support/Ortensia/central_server.txt (macOS 推荐)
    - %APPDATA%\\Ortensia\\central_server.txt (Windows 推荐)
    - %LOCALAPPDATA%\\Ortensia\\central_server.txt (Windows 备选)
    - ~/.ortensia_server
    - ~/.config/ortensia/central_server.txt
    """
    try:
        home = Path.home()
        appdata = os.environ.get("APPDATA")
        localappdata = os.environ.get("LOCALAPPDATA")
        candidates = [
            home / "Library" / "Application Support" / "Ortensia" / "central_server.txt",
            Path(appdata) / "Ortensia" / "central_server.txt" if appdata else None,
            Path(localappdata) / "Ortensia" / "central_server.txt" if localappdata else None,
            home / ".ortensia_server",
            home / ".config" / "ortensia" / "central_server.txt",
        ]
        for p in candidates:
            try:
                if p is None:
                    continue
                if not p.exists():
                    continue
                url = p.read_text(encoding="utf-8").strip()
                if url:
                    return url
            except Exception:
                continue
    except Exception:
        pass
    return None


async def send_hook_event(event_type: str, event_data: dict, server_url: str = None):
    """
    发送 Hook 事件到 Ortensia 中央服务器
    
    使用 Ortensia 协议格式直接发送消息
    
    Args:
        event_type: 事件类型（如 'file_save', 'git_commit'）
        event_data: 事件数据字典
        server_url: WebSocket 服务器地址（默认从环境变量或配置读取）
    """
    # 获取服务器地址
    if server_url is None:
        server_url = (
            os.environ.get("WS_SERVER")
            or os.environ.get("ORTENSIA_SERVER")
            or _read_server_url_from_file()
            or "ws://localhost:8765"
        )
    
    try:
        # 连接到服务器
        async with websockets.connect(server_url) as websocket:
            # 生成客户端 ID
            client_id = f"cursor-hook-{os.getpid()}"
            
            # 根据事件类型确定消息内容和情绪
            text, emotion = get_message_for_event(event_type, event_data)
            
            # 构造 Ortensia 协议消息
            message = {
                "type": "aituber_receive_text",  # AITuber 接收文本消息
                "from": client_id,
                "to": "broadcast",  # 广播给所有客户端
                "timestamp": int(datetime.now().timestamp()),
                "payload": {
                    "text": text,
                    "role": "assistant",
                    "emotion": emotion,
                    "type": "hook_event",
                    "event_type": event_type,
                    "event_data": event_data
                }
            }
            
            # 发送消息
            await websocket.send(json.dumps(message))
            print(f"✅ 事件已发送: {event_type} -> {text}")
            
            # 等待确认（可选）
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                print(f"📨 服务器响应: {response[:100]}...")
            except asyncio.TimeoutError:
                # 没有响应也没关系，消息已发送
                pass
        
    except ConnectionRefusedError:
        print(f"❌ 无法连接到服务器: {server_url}", file=sys.stderr)
        print(f"   请确保 Ortensia 中央服务器正在运行", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发送失败: {e}", file=sys.stderr)
        sys.exit(1)


def get_message_for_event(event_type: str, event_data: dict) -> tuple[str, str]:
    """
    根据事件类型生成消息和情绪
    
    Args:
        event_type: 事件类型
        event_data: 事件数据
        
    Returns:
        (消息文本, 情绪类型)
    """
    # 默认消息
    messages = {
        'file_save': ('保存成功~', 'neutral'),
        'git_commit': ('太棒了！代码提交成功~', 'happy'),
        'git_push': ('Push 完成！辛苦了~', 'happy'),
        'build_success': ('构建成功！', 'happy'),
        'build_error': ('构建失败了...别担心，我们一起修复它~', 'sad'),
        'test_pass': ('测试通过！你真厉害！', 'excited'),
        'test_fail': ('测试失败了...我们再检查一下~', 'sad'),
    }
    
    # 如果有自定义消息，使用自定义消息
    if 'message' in event_data:
        return (event_data['message'], 'neutral')
    
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

