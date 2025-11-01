#!/usr/bin/env python3
"""
WebSocket 服务器 - 接收 AITuber Kit 和 Event Bridge 的连接
WebSocket Server - Receives connections from AITuber Kit and Event Bridge
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime
from tts_manager import TTSManager


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# 存储连接的客户端
aituber_clients = set()  # AITuber Kit 客户端

# 初始化 TTS 管理器
tts_manager = TTSManager()
try:
    tts_manager.initialize()
    logger.info(f"✅ TTS 初始化成功: {tts_manager.get_info()['name']}")
except Exception as e:
    logger.error(f"❌ TTS 初始化失败: {e}")
    logger.warning("⚠️  TTS 功能将不可用")


async def handle_client(websocket):
    """
    处理客户端连接
    
    Args:
        websocket: WebSocket 连接
    """
    client_addr = websocket.remote_address
    # 获取连接路径（如果需要）
    path = getattr(websocket, 'path', '/ws')
    logger.info(f"✅ Client connected from {client_addr}, path: {path}")
    
    # 将客户端添加到列表（假设所有连接都是 AITuber Kit）
    aituber_clients.add(websocket)
    logger.info(f"👥 Total connected clients: {len(aituber_clients)}")
    
    try:
        # 保持连接，接收消息
        async for message in websocket:
            try:
                # 解析消息
                data = json.loads(message)
                logger.info(f"📨 Received message: {data}")
                
                # 如果消息包含文本，生成 TTS
                # 支持 'text' 和 'message' 两种字段（兼容性）
                text = data.get('text') or data.get('message')
                if text and tts_manager.tts:
                    try:
                        emotion = data.get('emotion', 'neutral')
                        
                        logger.info(f"🎤 生成 TTS: {text} (emotion: {emotion})")
                        
                        # 生成音频文件
                        audio_file = await asyncio.to_thread(
                            tts_manager.generate_with_emotion,
                            text,
                            emotion
                        )
                        
                        # 将音频文件路径添加到消息中
                        data['audio_file'] = audio_file
                        logger.info(f"✅ TTS 生成成功: {audio_file}")
                        
                    except Exception as e:
                        logger.error(f"❌ TTS 生成失败: {e}")
                        # 即使 TTS 失败，也继续发送消息
                
                # 广播给所有其他客户端（除了发送者）
                await broadcast_to_aituber(data, exclude=websocket)
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON: {e}")
            except Exception as e:
                logger.error(f"❌ Error processing message: {e}")
    
    except websockets.exceptions.ConnectionClosed as e:
        logger.warning(f"⚠️  Connection closed: {e}")
    except Exception as e:
        logger.error(f"❌ Error in handle_client: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 移除客户端
        if websocket in aituber_clients:
            aituber_clients.remove(websocket)
        logger.info(f"👋 Client disconnected, remaining: {len(aituber_clients)}")


async def broadcast_to_aituber(message: dict, exclude=None):
    """
    向所有 AITuber Kit 客户端广播消息
    
    Args:
        message: 要发送的消息字典
        exclude: 要排除的客户端（通常是发送者自己）
    """
    # 筛选目标客户端（排除发送者）
    target_clients = [c for c in aituber_clients if c != exclude]
    
    if not target_clients:
        logger.warning("⚠️  No AITuber clients to broadcast to")
        return False
    
    message_json = json.dumps(message)
    
    # 向所有目标客户端发送
    results = await asyncio.gather(
        *[client.send(message_json) for client in target_clients],
        return_exceptions=True
    )
    
    # 统计成功数量
    success_count = sum(1 for r in results if not isinstance(r, Exception))
    logger.info(f"📤 Broadcast to {success_count}/{len(target_clients)} clients")
    
    return success_count > 0


# 全局变量，用于从其他地方调用
_server_instance = None
_broadcast_queue = asyncio.Queue()


async def message_broadcaster():
    """
    消息广播协程 - 从队列中获取消息并广播
    """
    logger.info("🔄 Message broadcaster started")
    
    while True:
        try:
            # 从队列获取消息
            message = await _broadcast_queue.get()
            
            # 广播消息
            await broadcast_to_aituber(message)
            
            # 标记任务完成
            _broadcast_queue.task_done()
        
        except Exception as e:
            logger.error(f"❌ Error in broadcaster: {e}")
            await asyncio.sleep(0.1)


def queue_message(text: str, emotion: str = 'neutral', role: str = 'assistant', event_type: str = 'assistant'):
    """
    将消息添加到广播队列（可以从同步代码调用）
    
    Args:
        text: 消息文本
        emotion: 表情类型
        role: 角色
        event_type: 事件类型
    """
    message = {
        'text': text,
        'role': role,
        'emotion': emotion,
        'type': event_type
    }
    
    try:
        # 尝试同步方式添加到队列
        _broadcast_queue.put_nowait(message)
        logger.info(f"📝 Message queued: [{emotion}] {text}")
    except Exception as e:
        logger.error(f"❌ Failed to queue message: {e}")


async def main():
    """主函数"""
    global _server_instance
    
    logger.info("=" * 70)
    logger.info("  🎨 オルテンシア WebSocket Server")
    logger.info("=" * 70)
    logger.info("")
    logger.info("服务器配置：")
    logger.info("  - 地址: ws://localhost:8000/ws")
    logger.info("  - 协议: WebSocket")
    logger.info("  - 功能: 接收 AITuber Kit 连接，转发 Event Bridge 消息")
    logger.info("")
    logger.info("=" * 70)
    
    # 启动消息广播器
    broadcaster_task = asyncio.create_task(message_broadcaster())
    
    # 启动 WebSocket 服务器
    async with websockets.serve(handle_client, "localhost", 8000):
        logger.info("✅ WebSocket server started at ws://localhost:8000")
        logger.info("🎯 Path: ws://localhost:8000/ws")
        logger.info("")
        logger.info("等待 AITuber Kit 连接...")
        logger.info("按 Ctrl+C 停止服务器")
        logger.info("")
        
        _server_instance = True
        
        try:
            # 永久运行
            await asyncio.Future()
        except asyncio.CancelledError:
            logger.info("🛑 Server shutting down...")
            broadcaster_task.cancel()
            try:
                await broadcaster_task
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️  Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

