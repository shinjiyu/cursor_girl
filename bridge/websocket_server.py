#!/usr/bin/env python3
"""
Ortensia 中央 WebSocket Server

支持：
1. 新协议客户端（Cursor Hook, Command Client等）
2. 旧协议客户端（AITuber Kit - 向后兼容）

版本: 2.0 (with Protocol Support)
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Dict, Set, Optional
import time

# 导入新协议
from protocol import (
    Message,
    MessageBuilder,
    MessageType,
    ClientType,
    AgentStatus,
    Platform
)

# 导入 TTS 管理器
try:
    from tts_manager import TTSManager
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logging.warning("⚠️  TTS Manager 不可用，TTS 功能将被禁用")


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 客户端管理
# ============================================================================

class ClientInfo:
    """客户端信息"""
    
    def __init__(self, websocket, client_id: str, client_type: str):
        self.websocket = websocket
        self.client_id = client_id
        self.client_type = client_type
        self.registered_at = time.time()
        self.last_heartbeat = time.time()
        self.metadata = {}  # 额外的元数据
    
    def update_heartbeat(self):
        """更新心跳时间"""
        self.last_heartbeat = time.time()
    
    def is_alive(self, timeout=120):
        """检查客户端是否存活（默认 120 秒超时）"""
        return (time.time() - self.last_heartbeat) < timeout
    
    def __repr__(self):
        return f"ClientInfo({self.client_id}, {self.client_type})"


class ClientRegistry:
    """客户端注册表"""
    
    def __init__(self):
        self.clients: Dict[str, ClientInfo] = {}  # client_id -> ClientInfo
        self.ws_to_id: Dict = {}  # websocket -> client_id
    
    def register(self, websocket, client_id: str, client_type: str, metadata: dict = None):
        """注册客户端"""
        client_info = ClientInfo(websocket, client_id, client_type)
        
        if metadata:
            client_info.metadata = metadata
        
        self.clients[client_id] = client_info
        self.ws_to_id[websocket] = client_id
        
        logger.info(f"📝 注册客户端: {client_id} ({client_type})")
        return client_info
    
    def unregister(self, websocket):
        """注销客户端"""
        if websocket in self.ws_to_id:
            client_id = self.ws_to_id[websocket]
            if client_id in self.clients:
                client_type = self.clients[client_id].client_type
                del self.clients[client_id]
                logger.info(f"📤 注销客户端: {client_id} ({client_type})")
            del self.ws_to_id[websocket]
    
    def get_by_id(self, client_id: str) -> Optional[ClientInfo]:
        """根据 ID 获取客户端"""
        return self.clients.get(client_id)
    
    def get_by_websocket(self, websocket) -> Optional[ClientInfo]:
        """根据 WebSocket 获取客户端"""
        client_id = self.ws_to_id.get(websocket)
        if client_id:
            return self.clients.get(client_id)
        return None
    
    def get_by_type(self, client_type: str) -> list:
        """获取指定类型的所有客户端"""
        return [c for c in self.clients.values() if c.client_type == client_type]
    
    def update_heartbeat(self, client_id: str):
        """更新客户端心跳"""
        if client_id in self.clients:
            self.clients[client_id].update_heartbeat()
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        stats = {}
        for client in self.clients.values():
            stats[client.client_type] = stats.get(client.client_type, 0) + 1
        return stats


# 全局客户端注册表
registry = ClientRegistry()

# TTS 管理器（兼容旧协议）
tts_manager = None
if TTS_AVAILABLE:
    try:
        tts_manager = TTSManager()
        tts_manager.initialize()
        logger.info(f"✅ TTS 初始化成功: {tts_manager.get_info()['name']}")
    except Exception as e:
        logger.error(f"❌ TTS 初始化失败: {e}")
        tts_manager = None


# ============================================================================
# 消息处理
# ============================================================================

async def handle_new_protocol_message(client_info: ClientInfo, message: Message):
    """处理新协议消息"""
    msg_type = message.type
    
    logger.info(f"📨 [{client_info.client_id}] {msg_type.value}")
    
    try:
        if msg_type == MessageType.REGISTER:
            await handle_register(client_info, message)
        
        elif msg_type == MessageType.HEARTBEAT:
            await handle_heartbeat(client_info, message)
        
        elif msg_type == MessageType.DISCONNECT:
            await handle_disconnect(client_info, message)
        
        elif msg_type == MessageType.COMPOSER_SEND_PROMPT:
            await handle_composer_send_prompt(client_info, message)
        
        elif msg_type == MessageType.COMPOSER_QUERY_STATUS:
            await handle_composer_query_status(client_info, message)
        
        elif msg_type == MessageType.COMPOSER_SEND_PROMPT_RESULT:
            await route_message(message)
        
        elif msg_type == MessageType.COMPOSER_STATUS_RESULT:
            await route_message(message)
        
        elif msg_type in [MessageType.AGENT_STATUS_CHANGED, MessageType.AGENT_COMPLETED, MessageType.AGENT_ERROR]:
            await broadcast_event(message)
        
        else:
            logger.warning(f"⚠️  未知消息类型: {msg_type.value}")
    
    except Exception as e:
        logger.error(f"❌ 处理消息错误: {e}")
        import traceback
        traceback.print_exc()


async def handle_register(client_info: ClientInfo, message: Message):
    """处理注册消息"""
    payload = message.payload
    client_id = message.from_
    
    # 更新客户端信息
    client_info.client_id = client_id
    client_info.client_type = payload.get('client_type', 'unknown')
    client_info.metadata = payload
    client_info.update_heartbeat()
    
    # 重新注册（可能 ID 变了）
    if message.from_ != client_info.client_id:
        # 更新注册表
        old_id = None
        for ws, cid in list(registry.ws_to_id.items()):
            if ws == client_info.websocket:
                old_id = cid
                break
        
        if old_id and old_id in registry.clients:
            del registry.clients[old_id]
        
        registry.clients[client_id] = client_info
        registry.ws_to_id[client_info.websocket] = client_id
    
    logger.info(f"✅ [{client_id}] 注册成功: {client_info.client_type}")
    
    # 发送确认
    ack_msg = MessageBuilder.register_ack(
        to_id=client_id,
        success=True,
        assigned_id=client_id,
        server_info={
            "version": "2.0",
            "supported_protocols": ["v1"],
            "server_time": int(time.time())
        }
    )
    
    await client_info.websocket.send(ack_msg.to_json())


async def handle_heartbeat(client_info: ClientInfo, message: Message):
    """处理心跳消息"""
    client_info.update_heartbeat()
    
    # 发送心跳响应
    ack_msg = MessageBuilder.heartbeat_ack(to_id=client_info.client_id)
    await client_info.websocket.send(ack_msg.to_json())


async def handle_disconnect(client_info: ClientInfo, message: Message):
    """处理断开连接消息"""
    payload = message.payload
    reason = payload.get('reason', 'unknown')
    
    logger.info(f"👋 [{client_info.client_id}] 主动断开: {reason}")


async def handle_composer_send_prompt(client_info: ClientInfo, message: Message):
    """处理 Composer 发送提示词命令"""
    # 路由到目标 Cursor Hook
    await route_message(message)


async def handle_composer_query_status(client_info: ClientInfo, message: Message):
    """处理 Composer 查询状态命令"""
    # 路由到目标 Cursor Hook
    await route_message(message)


async def route_message(message: Message):
    """路由消息到指定客户端"""
    target_id = message.to
    
    if not target_id or target_id == "":
        logger.warning(f"⚠️  消息没有指定目标，忽略")
        return
    
    target_client = registry.get_by_id(target_id)
    
    if not target_client:
        logger.warning(f"⚠️  目标客户端不存在: {target_id}")
        
        # 发送错误响应（如果是命令消息）
        if message.type in [MessageType.COMPOSER_SEND_PROMPT, MessageType.COMPOSER_QUERY_STATUS]:
            error_msg = MessageBuilder.composer_send_prompt_result(
                from_id="server",
                to_id=message.from_,
                success=False,
                agent_id=message.payload.get('agent_id', 'default'),
                error=f"目标客户端不存在: {target_id}"
            )
            
            sender = registry.get_by_id(message.from_)
            if sender:
                await sender.websocket.send(error_msg.to_json())
        
        return
    
    # 发送消息
    try:
        await target_client.websocket.send(message.to_json())
        logger.info(f"📤 路由消息: {message.from_} → {target_id} ({message.type.value})")
    except Exception as e:
        logger.error(f"❌ 发送消息失败: {e}")


async def broadcast_event(message: Message):
    """广播事件到所有客户端（除了发送者）"""
    sender_id = message.from_
    
    # 获取所有客户端（排除发送者）
    targets = [c for c in registry.clients.values() if c.client_id != sender_id]
    
    if not targets:
        logger.info(f"ℹ️  没有其他客户端，跳过广播")
        return
    
    message_json = message.to_json()
    
    # 发送到所有目标
    results = await asyncio.gather(
        *[client.websocket.send(message_json) for client in targets],
        return_exceptions=True
    )
    
    success_count = sum(1 for r in results if not isinstance(r, Exception))
    logger.info(f"📡 广播事件: {message.type.value} → {success_count}/{len(targets)} 客户端")


async def handle_legacy_message(websocket, data: dict):
    """处理旧协议消息（AITuber Kit 兼容）"""
    logger.info(f"📨 [旧协议] 收到消息: {data.get('type', 'unknown')}")
    
    # 如果消息包含文本，生成 TTS
    text = data.get('text') or data.get('message')
    if text and tts_manager:
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
    
    # 广播给所有 AITuber 客户端（旧协议）
    aituber_clients = [c for c in registry.clients.values() 
                       if c.client_type == 'aituber_legacy']
    
    message_json = json.dumps(data)
    
    # 发送到所有 AITuber 客户端（除了发送者）
    targets = [c for c in aituber_clients if c.websocket != websocket]
    
    if targets:
        results = await asyncio.gather(
            *[client.websocket.send(message_json) for client in targets],
            return_exceptions=True
        )
        
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        logger.info(f"📤 广播旧协议消息: {success_count}/{len(targets)} 客户端")


# ============================================================================
# 客户端连接处理
# ============================================================================

async def handle_client(websocket, path):
    """处理客户端连接"""
    client_addr = websocket.remote_address
    logger.info(f"✅ 新连接: {client_addr}")
    
    # 创建临时客户端信息（等待注册）
    temp_id = f"temp-{id(websocket)}"
    client_info = ClientInfo(websocket, temp_id, "unknown")
    
    # 临时注册
    registry.clients[temp_id] = client_info
    registry.ws_to_id[websocket] = temp_id
    
    is_new_protocol = False  # 标记是否使用新协议
    
    try:
        async for message_str in websocket:
            try:
                data = json.loads(message_str)
                
                # 检测协议类型
                if 'type' in data and 'from' in data and 'payload' in data:
                    # 新协议
                    is_new_protocol = True
                    message = Message.from_dict(data)
                    
                    # 如果是第一条消息且不是 REGISTER，自动注册为旧协议客户端
                    if client_info.client_type == "unknown" and message.type != MessageType.REGISTER:
                        # 转换为旧协议处理
                        is_new_protocol = False
                        await handle_legacy_message(websocket, data)
                    else:
                        await handle_new_protocol_message(client_info, message)
                
                else:
                    # 旧协议（AITuber Kit）
                    if client_info.client_type == "unknown":
                        # 首次识别为旧协议客户端
                        client_info.client_type = "aituber_legacy"
                        client_info.client_id = f"aituber-{id(websocket)}"
                        logger.info(f"🔄 识别为旧协议客户端: {client_info.client_id}")
                    
                    await handle_legacy_message(websocket, data)
            
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON 解析错误: {e}")
            except Exception as e:
                logger.error(f"❌ 消息处理错误: {e}")
                import traceback
                traceback.print_exc()
    
    except websockets.exceptions.ConnectionClosed as e:
        logger.info(f"🔌 连接关闭: {client_addr}")
    except Exception as e:
        logger.error(f"❌ 连接错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理注册
        registry.unregister(websocket)
        logger.info(f"👋 客户端断开: {client_addr}")
        logger.info(f"📊 当前连接: {registry.get_stats()}")


# ============================================================================
# 心跳检测
# ============================================================================

async def heartbeat_monitor():
    """心跳监控协程"""
    logger.info("💓 心跳监控已启动")
    
    while True:
        try:
            await asyncio.sleep(60)  # 每分钟检查一次
            
            # 检查所有客户端
            dead_clients = []
            
            for client_id, client_info in registry.clients.items():
                if not client_info.is_alive(timeout=120):
                    dead_clients.append(client_id)
            
            # 移除死连接
            for client_id in dead_clients:
                client_info = registry.clients.get(client_id)
                if client_info:
                    logger.warning(f"⚠️  客户端超时: {client_id}")
                    try:
                        await client_info.websocket.close()
                    except:
                        pass
                    registry.unregister(client_info.websocket)
        
        except Exception as e:
            logger.error(f"❌ 心跳监控错误: {e}")
            await asyncio.sleep(1)


# ============================================================================
# 主函数
# ============================================================================

async def main():
    """主函数"""
    logger.info("=" * 70)
    logger.info("  🌸 Ortensia 中央 WebSocket Server v2.0")
    logger.info("=" * 70)
    logger.info("")
    logger.info("服务器配置:")
    logger.info("  - 地址: ws://localhost:8765")
    logger.info("  - 协议: Ortensia Protocol v1 + 旧协议兼容")
    logger.info("  - 支持客户端:")
    logger.info("    • Cursor Hook")
    logger.info("    • Command Client")
    logger.info("    • AITuber Client (新/旧)")
    logger.info("")
    logger.info("=" * 70)
    logger.info("")
    
    # 启动心跳监控
    heartbeat_task = asyncio.create_task(heartbeat_monitor())
    
    # 启动 WebSocket 服务器
    async with websockets.serve(handle_client, "localhost", 8765):
        logger.info("✅ WebSocket 服务器已启动: ws://localhost:8765")
        logger.info("")
        logger.info("等待客户端连接...")
        logger.info("按 Ctrl+C 停止服务器")
        logger.info("")
        
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            logger.info("🛑 正在关闭服务器...")
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️  服务器已停止")
    except Exception as e:
        logger.error(f"❌ 致命错误: {e}")
        import traceback
        traceback.print_exc()
