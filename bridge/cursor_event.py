#!/usr/bin/env python3
"""
Cursor Event Handler - 处理来自 Cursor Hooks 的事件
Command-line tool to handle events from Cursor IDE hooks
"""
import sys
import argparse
import asyncio
import logging
from pathlib import Path

from emotion_mapper import EmotionMapper
from websocket_client import get_client


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


async def handle_event(event_type: str, metadata: dict = None):
    """
    处理单个事件
    
    Args:
        event_type: 事件类型（如 'file_save', 'git_commit'）
        metadata: 事件元数据
    """
    try:
        logger.info("=" * 60)
        logger.info(f"📥 Handling event: {event_type}")
        if metadata:
            logger.info(f"📋 Metadata: {metadata}")
        
        # 创建映射器
        mapper = EmotionMapper()
        
        # 映射事件到表情
        event = mapper.map_event(event_type, metadata)
        
        logger.info(f"🎭 Emotion: {event.emotion}")
        logger.info(f"💬 Message: {event.message}")
        
        # 获取 WebSocket 客户端
        client = await get_client()
        
        # 发送到 AITuber Kit
        success = await client.send_emotion(
            text=event.message,
            emotion=event.emotion,
            event_type=event_type
        )
        
        if success:
            logger.info("✅ Event handled successfully")
        else:
            logger.error("❌ Failed to send to AITuber Kit")
        
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error handling event: {e}")
        import traceback
        traceback.print_exc()


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='Cursor Event Handler - Send events to AITuber Kit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file_save --file="test.py"
  %(prog)s git_commit --message="feat: add feature" --files=3
  %(prog)s syntax_error --error="undefined variable"
  %(prog)s celebration
        """
    )
    
    parser.add_argument(
        'event_type',
        help='Event type (e.g., file_save, git_commit, test_pass)'
    )
    parser.add_argument('--file', help='File path')
    parser.add_argument('--filename', help='File name')
    parser.add_argument('--message', help='Commit/error message')
    parser.add_argument('--files', type=int, help='Number of files')
    parser.add_argument('--lines', type=int, help='Number of lines')
    parser.add_argument('--error', help='Error message')
    parser.add_argument('--passed', type=int, help='Number of passed tests')
    parser.add_argument('--failed', type=int, help='Number of failed tests')
    
    args = parser.parse_args()
    
    # 构建元数据
    metadata = {}
    
    if args.file:
        metadata['file'] = args.file
        metadata['filename'] = Path(args.file).name
    
    if args.filename:
        metadata['filename'] = args.filename
    
    if args.message:
        metadata['message'] = args.message
    
    if args.files:
        metadata['files'] = args.files
    
    if args.lines:
        metadata['lines'] = args.lines
    
    if args.error:
        metadata['error'] = args.error
    
    if args.passed:
        metadata['passed'] = args.passed
    
    if args.failed:
        metadata['failed'] = args.failed
    
    # 处理事件
    try:
        asyncio.run(handle_event(args.event_type, metadata))
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(1)


if __name__ == '__main__':
    main()

