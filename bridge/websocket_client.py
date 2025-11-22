"""
WebSocket 客户端 - 与 AITuber Kit 通信
WebSocket Client - Communicates with AITuber Kit
"""
import asyncio
import websockets
import json
import logging
from typing import Optional
from datetime import datetime


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class WebSocketClient:
    """WebSocket 客户端 - 与 AITuber Kit 通信"""
    
    def __init__(self, uri: str = 'ws://localhost:8765'):
        """
        初始化 WebSocket 客户端
        
        Args:
            uri: WebSocket 服务器地址（默认连接到 Ortensia 中央服务器）
        """
        self.uri = uri
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.reconnect_interval = 3  # 秒
        self.message_queue = asyncio.Queue()
        self.keep_alive_task: Optional[asyncio.Task] = None
        
        logger.info(f"🔌 WebSocketClient initialized (target: {uri})")
    
    async def connect(self) -> bool:
        """
        建立连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 简化连接，移除可能导致问题的参数
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            logger.info(f"✅ Connected to {self.uri}")
            return True
        except ConnectionRefusedError:
            logger.error(f"❌ Connection refused: WebSocket server not running at {self.uri}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Connection failed: {e.__class__.__name__}: {e}")
            self.connected = False
            return False
    
    async def send_emotion(
        self, 
        text: str, 
        emotion: str = 'neutral', 
        role: str = 'assistant', 
        event_type: str = 'assistant'
    ) -> bool:
        """
        发送表情控制消息
        
        Args:
            text: 消息文本
            emotion: 表情类型 (neutral/happy/sad/angry/relaxed/surprised)
            role: 角色 (assistant/user/system)
            event_type: 事件类型
        
        Returns:
            bool: 发送是否成功
        """
        # 检查连接状态
        if not self.connected or not self.websocket:
            logger.warning("⚠️  Not connected, attempting to reconnect...")
            success = await self.connect()
            if not success:
                return False
        
        message = {
            'text': text,
            'role': role,
            'emotion': emotion,
            'type': event_type
        }
        
        # 尝试发送，如果失败则重试一次
        max_retries = 2
        for attempt in range(max_retries):
            try:
                await self.websocket.send(json.dumps(message))
                logger.info(f"💬 Sent: [{emotion}] {text}")
                return True
            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"⚠️  Connection closed: {e}")
                self.connected = False
                
                # 如果不是最后一次尝试，重新连接
                if attempt < max_retries - 1:
                    logger.info("🔄 Reconnecting...")
                    success = await self.connect()
                    if not success:
                        return False
                else:
                    logger.error("❌ Max retries reached")
                    return False
            except Exception as e:
                logger.error(f"❌ Send failed: {e}")
                self.connected = False
                return False
        
        return False
    
    async def send_queued(self) -> bool:
        """从队列发送消息"""
        try:
            text, emotion = await asyncio.wait_for(
                self.message_queue.get(), 
                timeout=0.1
            )
            return await self.send_emotion(text, emotion)
        except asyncio.TimeoutError:
            return True  # 队列为空，不算错误
    
    async def keep_alive(self):
        """保持连接并处理消息队列"""
        logger.info("🔄 Starting keep-alive loop...")
        
        while True:
            if not self.connected:
                logger.info("⏳ Attempting to reconnect...")
                await self.connect()
                await asyncio.sleep(self.reconnect_interval)
                continue
            
            try:
                # 处理队列中的消息
                await self.send_queued()
                
                # 短暂休眠
                await asyncio.sleep(0.1)
                
            except websockets.exceptions.ConnectionClosed:
                logger.warning("⚠️  Connection closed")
                self.connected = False
            except Exception as e:
                logger.error(f"❌ Error in keep_alive: {e}")
                await asyncio.sleep(1)
    
    async def start_keep_alive(self):
        """启动 keep-alive 任务"""
        if self.keep_alive_task is None or self.keep_alive_task.done():
            self.keep_alive_task = asyncio.create_task(self.keep_alive())
            logger.info("🚀 Keep-alive task started")
    
    async def close(self):
        """关闭连接"""
        if self.keep_alive_task and not self.keep_alive_task.done():
            self.keep_alive_task.cancel()
            try:
                await self.keep_alive_task
            except asyncio.CancelledError:
                pass
        
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("👋 Connection closed")
    
    def add_to_queue(self, text: str, emotion: str = 'neutral'):
        """添加消息到队列"""
        self.message_queue.put_nowait((text, emotion))


# 全局单例客户端
_global_client: Optional[WebSocketClient] = None


async def get_client(uri: str = 'ws://localhost:8765') -> WebSocketClient:
    """
    获取全局 WebSocket 客户端（单例）
    
    Args:
        uri: WebSocket 服务器地址
    
    Returns:
        WebSocketClient: 客户端实例
    """
    global _global_client
    
    if _global_client is None:
        _global_client = WebSocketClient(uri)
        await _global_client.connect()
    
    return _global_client


async def test_client():
    """测试 WebSocket 客户端"""
    logger.info("=" * 60)
    logger.info("🧪 Testing WebSocketClient")
    logger.info("=" * 60)
    
    client = WebSocketClient()
    
    # 连接
    logger.info("\n1. Testing connection...")
    success = await client.connect()
    
    if not success:
        logger.error("❌ Connection failed, cannot continue test")
        return
    
    # 发送测试消息
    logger.info("\n2. Sending test messages...")
    
    test_messages = [
        ("你好！我是オルテンシア 👋", "happy"),
        ("准备开始测试~", "neutral"),
        ("这是一条开心的消息！", "happy"),
        ("这是一条难过的消息...", "sad"),
        ("惊喜！", "surprised"),
    ]
    
    for text, emotion in test_messages:
        await client.send_emotion(text, emotion)
        await asyncio.sleep(2)  # 等待 2 秒
    
    logger.info("\n3. Closing connection...")
    await client.close()
    
    logger.info("\n✅ Test completed!")


if __name__ == '__main__':
    # 运行测试
    try:
        asyncio.run(test_client())
    except KeyboardInterrupt:
        logger.info("\n⚠️  Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

