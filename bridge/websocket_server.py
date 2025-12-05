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
    """客户端信息（支持多角色）"""
    
    def __init__(self, websocket, client_id: str, client_types: set = None):
        self.websocket = websocket
        self.client_id = client_id
        self.client_types = client_types or set()  # 多角色集合
        self.registered_at = time.time()
        self.last_heartbeat = time.time()
        self.metadata = {}  # 额外的元数据
    
    def add_role(self, role: str):
        """添加角色"""
        self.client_types.add(role)
    
    def remove_role(self, role: str):
        """移除角色"""
        self.client_types.discard(role)
    
    def has_role(self, role: str) -> bool:
        """检查是否拥有某个角色"""
        return role in self.client_types
    
    @property
    def client_type(self) -> str:
        """向后兼容：返回第一个角色（如果只有一个角色）或主要角色"""
        if not self.client_types:
            return "unknown"
        # 优先级：cursor_inject > aituber_client > command_client > agent_hook
        priority = ['cursor_inject', 'aituber_client', 'command_client', 'agent_hook']
        for role in priority:
            if role in self.client_types:
                return role
        return list(self.client_types)[0]
    
    def update_heartbeat(self):
        """更新心跳时间"""
        self.last_heartbeat = time.time()
    
    def is_alive(self, timeout=120):
        """检查客户端是否存活（默认 120 秒超时）"""
        return (time.time() - self.last_heartbeat) < timeout
    
    def __repr__(self):
        roles = ", ".join(sorted(self.client_types)) if self.client_types else "none"
        return f"ClientInfo({self.client_id}, roles=[{roles}])"


class ClientRegistry:
    """客户端注册表"""
    
    def __init__(self):
        self.clients: Dict[str, ClientInfo] = {}  # client_id -> ClientInfo
        self.ws_to_id: Dict = {}  # websocket -> client_id
        self.workspace_to_cursor: Dict[str, str] = {}  # workspace -> cursor_id (旧方案)
        
        # V10: conversation_id 映射
        self.conversation_id_to_inject_id: Dict[str, str] = {}  # conversation_id -> inject_id
        self.inject_id_to_conversation_id: Dict[str, str] = {}  # inject_id -> conversation_id
    
    def register(self, websocket, client_id: str, client_types: list, metadata: dict = None):
        """
        注册客户端（支持多角色）
        
        Args:
            websocket: WebSocket 连接
            client_id: 客户端 ID
            client_types: 角色列表，例如 ["aituber", "command_client"]
            metadata: 元数据字典
        
        Returns:
            ClientInfo 对象
        """
        if client_id in self.clients:
            # 客户端已存在，添加新角色
            client_info = self.clients[client_id]
            old_roles = client_info.client_types.copy()
            for role in client_types:
                client_info.add_role(role)
            new_roles = client_info.client_types - old_roles
            if new_roles:
                logger.info(f"🔄 [{client_id}] 添加角色: {sorted(new_roles)}")
            logger.info(f"📝 [{client_id}] 当前角色: {sorted(client_info.client_types)}")
        else:
            # 新客户端
            client_info = ClientInfo(websocket, client_id, set(client_types))
            self.clients[client_id] = client_info
            self.ws_to_id[websocket] = client_id
            logger.info(f"📝 注册客户端: {client_id}，角色: {sorted(client_types)}")
        
        if metadata:
            client_info.metadata.update(metadata)
        
        return client_info
    
    def unregister(self, websocket):
        """注销客户端"""
        if websocket in self.ws_to_id:
            client_id = self.ws_to_id[websocket]
            if client_id in self.clients:
                client_info = self.clients[client_id]
                roles_str = ", ".join(sorted(client_info.client_types)) if client_info.client_types else "none"
                
                # 如果是 cursor_hook 或 agent_hook，清理 workspace 映射
                if client_info.has_role('cursor_hook') or client_info.has_role('agent_hook'):
                    workspace = client_info.metadata.get('workspace')
                    if workspace and self.workspace_to_cursor.get(workspace) == client_id:
                        del self.workspace_to_cursor[workspace]
                        logger.info(f"🗑️  清理 workspace 映射: {workspace}")
                
                del self.clients[client_id]
                logger.info(f"📤 注销客户端: {client_id} (角色: [{roles_str}])")
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
        """获取拥有指定角色的所有客户端（支持多角色）"""
        return [c for c in self.clients.values() if c.has_role(client_type)]
    
    def update_heartbeat(self, client_id: str):
        """更新客户端心跳"""
        if client_id in self.clients:
            self.clients[client_id].update_heartbeat()
    
    def register_cursor_workspace(self, cursor_id: str, workspace: str):
        """注册 Cursor 的 workspace 映射"""
        if workspace:
            self.workspace_to_cursor[workspace] = cursor_id
            logger.info(f"🗺️  注册 workspace 映射: {workspace} → {cursor_id}")
    
    def get_cursor_by_workspace(self, workspace: str) -> Optional[str]:
        """根据 workspace 获取对应的 Cursor ID"""
        cursor_id = self.workspace_to_cursor.get(workspace)
        if cursor_id and cursor_id in self.clients:
            return cursor_id
        return None
    
    # ============================================================
    # V11: 移除映射管理，改用动态查询
    # ============================================================
    
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
        
        # 语义操作（V9 新增）
        elif msg_type == MessageType.AGENT_EXECUTE_PROMPT:
            await handle_agent_execute_prompt(client_info, message)
        
        elif msg_type == MessageType.AGENT_EXECUTE_PROMPT_RESULT:
            await route_message(message)
        
        elif msg_type == MessageType.AGENT_STOP_EXECUTION:
            await handle_agent_stop_execution(client_info, message)
        
        elif msg_type == MessageType.AGENT_STOP_EXECUTION_RESULT:
            await route_message(message)
        
        elif msg_type in [MessageType.AGENT_STATUS_CHANGED, MessageType.AGENT_COMPLETED, MessageType.AGENT_ERROR]:
            await broadcast_event(message)
        
        # AITuber 操作
        elif msg_type == MessageType.AITUBER_RECEIVE_TEXT:
            await handle_aituber_receive_text(client_info, message)
        
        elif msg_type == MessageType.AITUBER_SPEAK:
            await route_message(message)
        
        elif msg_type == MessageType.AITUBER_EMOTION:
            await route_message(message)
        
        elif msg_type == MessageType.AITUBER_STATUS:
            await route_message(message)
        
        # Cursor 输入操作
        elif msg_type == MessageType.CURSOR_INPUT_TEXT:
            await handle_cursor_input_text(client_info, message)
        
        elif msg_type == MessageType.CURSOR_INPUT_TEXT_RESULT:
            await route_message(message)  # 结果转发回发送者
        
        # 通用 JavaScript 执行
        elif msg_type == MessageType.EXECUTE_JS:
            await route_message(message)  # 转发给 inject
        
        elif msg_type == MessageType.EXECUTE_JS_RESULT:
            # 检查是否是 discovery 请求的结果
            if not await handle_execute_js_result_for_discovery(message):
                # 不是 discovery 请求，正常转发
                await route_message(message)
        
        # Conversation 发现（V11.3 新增）
        elif msg_type == MessageType.GET_CONVERSATION_ID:
            await handle_get_conversation_id(client_info, message)
        
        elif msg_type == MessageType.GET_CONVERSATION_ID_RESULT:
            await route_message(message)  # 结果转发回发送者（通常是 AITuber）
        
        else:
            logger.warning(f"⚠️  未知消息类型: {msg_type.value}")
    
    except Exception as e:
        logger.error(f"❌ 处理消息错误: {e}")
        import traceback
        traceback.print_exc()


async def handle_register(client_info: ClientInfo, message: Message):
    """处理注册消息（支持多角色）"""
    payload = message.payload
    client_id = message.from_
    old_id = client_info.client_id  # 保存旧 ID
    
    # 🆕 兼容新旧协议
    if 'client_types' in payload:
        # 新协议：多角色列表
        client_types = payload['client_types']
        if not isinstance(client_types, list):
            client_types = [client_types]
    elif 'client_type' in payload:
        # 旧协议：单角色字符串
        client_types = [payload['client_type']]
    else:
        client_types = ['unknown']
    
    # 更新客户端信息
    client_info.client_id = client_id
    
    # 更新角色（如果已存在，添加新角色；否则设置角色）
    if client_id in registry.clients and client_id != old_id:
        # 这是已存在的客户端重新注册，添加新角色
        existing_info = registry.clients[client_id]
        for role in client_types:
            existing_info.add_role(role)
        client_info = existing_info
    else:
        # 新客户端或ID未变
        for role in client_types:
            client_info.add_role(role)
    
    client_info.metadata.update(payload)
    client_info.update_heartbeat()
    
    # 更新注册表（ID 可能变了）
    if old_id and old_id in registry.clients and old_id != client_id:
        del registry.clients[old_id]
    
    registry.clients[client_id] = client_info
    registry.ws_to_id[client_info.websocket] = client_id
    
    # 如果是 cursor_hook 或 agent_hook，注册 workspace 映射
    if client_info.has_role('cursor_hook') or client_info.has_role('agent_hook') or client_info.has_role('cursor_inject'):
        workspace = payload.get('workspace')
        if workspace:
            registry.register_cursor_workspace(client_id, workspace)
    
    roles_str = ", ".join(sorted(client_info.client_types))
    logger.info(f"✅ [{client_id}] 注册成功，角色: [{roles_str}]")
    
    # 发送确认
    ack_msg = MessageBuilder.register_ack(
        to_id=client_id,
        success=True,
        assigned_id=client_id,
        server_info={
            "version": "2.0",
            "supported_protocols": ["v1"],
            "multi_role": True,  # 🆕 标记服务器支持多角色
            "server_time": int(time.time())
        }
    )
    
    await client_info.websocket.send(ack_msg.to_json())
    
    # V11: 不再主动请求 conversation_id，改用动态查询


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


async def find_inject_for_hook(message: Message) -> Optional[ClientInfo]:
    """
    根据 hook 消息找到对应的 inject
    
    使用场景：
    - hook 发送 "complete" 事件
    - 想给对应的 inject 发送新任务
    
    返回：对应的 inject ClientInfo，如果找不到则返回 None
    """
    payload = message.payload
    inject_id = payload.get('inject_id')
    
    if not inject_id:
        logger.warning(f"⚠️  hook 消息缺少 inject_id 字段")
        logger.warning(f"   这通常意味着 inject 未正确设置环境变量 ORTENSIA_INJECT_ID")
        return None
    
    # 直接通过 inject_id 查找
    inject_client = registry.get_by_id(inject_id)
    
    if not inject_client:
        logger.warning(f"⚠️  inject 客户端不存在或已断开: {inject_id}")
        return None
    
    logger.info(f"✅ 找到对应的 inject: {inject_id}")
    return inject_client


async def handle_composer_send_prompt(client_info: ClientInfo, message: Message):
    """处理 Composer 发送提示词命令"""
    # 路由到目标 Cursor Hook
    await route_message(message)


async def handle_composer_query_status(client_info: ClientInfo, message: Message):
    """处理 Composer 查询状态命令"""
    # 路由到目标 Cursor Hook
    await route_message(message)


async def handle_agent_execute_prompt(client_info: ClientInfo, message: Message):
    """处理 Agent 执行提示词命令（语义操作）"""
    # V9 新增：语义操作，直接路由到目标 Cursor Hook
    await route_message(message)


async def handle_agent_stop_execution(client_info: ClientInfo, message: Message):
    """处理 Agent 停止执行命令（语义操作）"""
    # V9 新增：语义操作，直接路由到目标 Cursor Hook
    await route_message(message)


async def handle_aituber_receive_text(client_info: ClientInfo, message: Message):
    """处理 Hook 发来的 aituber_receive_text 消息
    
    V11: 移除映射管理，改用动态查询
    
    功能：
    1. 生成 TTS 音频（如果 TTS 可用）
    2. 将消息（含音频）转发给所有 AITuber 客户端
    
    工作流程:
    1. 提取文本和情绪
    2. 使用 TTS 生成音频文件
    3. 将音频文件路径添加到消息中
    4. 转发给所有 AITuber 客户端
    """
    hook_id = message.from_
    payload = message.payload
    
    # 1. 从 hook ID 提取 conversation_id
    conversation_id = "unknown"
    if hook_id.startswith("hook-"):
        conversation_id = hook_id[5:]
    
    logger.info(f"📨 [AITuber] Hook 消息，conversation_id: {conversation_id}")
    
    # 2. 获取所有 AITuber 客户端
    aituber_clients = registry.get_by_type('aituber_client')
    
    if not aituber_clients:
        logger.warning(f"⚠️  目标客户端不存在: aituber")
        return
    
    # 4. 生成 TTS 音频（如果 TTS 可用）
    text = payload.get('text', '')
    emotion = payload.get('emotion', 'neutral')
    
    if text and tts_manager:
        try:
            logger.info(f"🎤 生成 TTS: {text[:30]}... (emotion: {emotion})")
            
            # 生成音频文件（在线程池中执行，避免阻塞）
            audio_file = await asyncio.to_thread(
                tts_manager.generate_with_emotion,
                text,
                emotion
            )
            
            # 将音频文件路径添加到消息的 payload 中
            message.payload['audio_file'] = audio_file
            logger.info(f"✅ TTS 生成成功: {audio_file}")
            
        except Exception as e:
            logger.error(f"❌ TTS 生成失败: {e}")
            # TTS 失败不影响消息转发，继续执行
    
    # ✨ 将 conversation_id 添加到 payload 中
    message.payload['conversation_id'] = conversation_id
    
    # 5. 转发给所有 AITuber 客户端
    for aituber in aituber_clients:
        try:
            await aituber.websocket.send(message.to_json())
            logger.info(f"📤 [AITuber] 消息已转发: {hook_id} → {aituber.client_id}")
        except Exception as e:
            logger.error(f"❌ [AITuber] 转发失败: {aituber.client_id}, {e}")


async def handle_cursor_input_text(client_info: ClientInfo, message: Message):
    """处理从 AITuber 发来的 cursor_input_text 消息
    
    V11.2: 生成包含 conversation_id 检查的 JavaScript 代码，广播到所有窗口
    只有匹配的窗口会真正执行输入操作
    """
    from_id = message.from_
    text = message.payload.get('text', '')
    conversation_id = message.payload.get('conversation_id')
    execute = message.payload.get('execute', False)
    
    action_text = "输入并执行" if execute else "输入"
    logger.info(f"📝 [Cursor Input] 收到{action_text}请求: {text[:50]}... (conv: {conversation_id})")
    
    # 获取所有 cursor_inject 客户端
    inject_clients = registry.get_by_type('cursor_inject')
    
    if not inject_clients:
        logger.warning(f"⚠️  没有可用的 Cursor inject 客户端")
        error_msg = MessageBuilder.cursor_input_text_result(
            from_id="server",
            to_id=from_id,
            success=False,
            error="没有可用的 Cursor inject 客户端"
        )
        await client_info.websocket.send(error_msg.to_json())
        return
    
    # 使用第一个可用的 inject（一般情况下只有一个）
    target_inject = inject_clients[0]
    
    if target_inject:
        try:
            # 生成 JavaScript 代码来输入文本
            # V11.2: 代码包含 conversation_id 检查，只在匹配的窗口执行
            import json
            
            # 如果指定了 conversation_id，添加检查逻辑
            conv_check_code = ""
            if conversation_id:
                conv_check_code = f"""
                    // 🔍 检查当前窗口的 conversation_id
                    const expectedConvId = {json.dumps(conversation_id)};
                    const convElement = document.querySelector('[id^="composer-bottom-add-context-"]');
                    
                    if (!convElement) {{
                        return JSON.stringify({{
                            skipped: true,
                            reason: '未找到 conversation_id 元素'
                        }});
                    }}
                    
                    const match = convElement.id.match(/composer-bottom-add-context-([a-f0-9-]+)/);
                    const currentConvId = match ? match[1] : null;
                    
                    if (currentConvId !== expectedConvId) {{
                        return JSON.stringify({{
                            skipped: true,
                            reason: 'conversation_id 不匹配',
                            expected: expectedConvId,
                            current: currentConvId
                        }});
                    }}
                    
                    // ✅ conversation_id 匹配，继续执行
                """
            
            js_code = f"""
            (async function() {{
                try {{
                    {conv_check_code}
                    
                    // 查找 Composer 输入框
                    const inputSelector = 'div[contenteditable="true"][role="textbox"],' +
                                         'div[contenteditable="true"][aria-label*="composer"],' +
                                         'textarea[placeholder*="Ask"]';
                    
                    const inputElement = document.querySelector(inputSelector);
                    
                    if (!inputElement) {{
                        return JSON.stringify({{
                            success: false,
                            error: '找不到 Cursor 输入框'
                        }});
                    }}
                    
                    // 聚焦输入框
                    inputElement.focus();
                    
                    // 清空现有内容（如果有）
                    if (inputElement.tagName === 'TEXTAREA' || inputElement.tagName === 'INPUT') {{
                        inputElement.value = '';
                    }} else {{
                        // 对于 contenteditable，选中所有内容并删除
                        const range = document.createRange();
                        range.selectNodeContents(inputElement);
                        const selection = window.getSelection();
                        selection.removeAllRanges();
                        selection.addRange(range);
                        document.execCommand('delete', false);
                    }}
                    
                    // 模拟键盘输入
                    const textToInput = {json.dumps(text)};
                    
                    // 使用 document.execCommand insertText（对 Lexical 等编辑器有效）
                    document.execCommand('insertText', false, textToInput);
                    
                    // 备用方法：逐字符模拟输入事件
                    if (!inputElement.textContent && !inputElement.value) {{
                        for (let char of textToInput) {{
                            const keyboardEvent = new KeyboardEvent('keypress', {{
                                key: char,
                                code: 'Key' + char.toUpperCase(),
                                charCode: char.charCodeAt(0),
                                keyCode: char.charCodeAt(0),
                                bubbles: true,
                                cancelable: true
                            }});
                            inputElement.dispatchEvent(keyboardEvent);
                            
                            const inputEvent = new InputEvent('input', {{
                                data: char,
                                inputType: 'insertText',
                                bubbles: true,
                                cancelable: false
                            }});
                            inputElement.dispatchEvent(inputEvent);
                        }}
                    }}
                    
                    // 验证内容是否输入成功
                    let currentContent = '';
                    if (inputElement.tagName === 'TEXTAREA' || inputElement.tagName === 'INPUT') {{
                        currentContent = inputElement.value;
                    }} else {{
                        currentContent = inputElement.textContent || inputElement.innerText || '';
                    }}
                    
                    const shouldExecute = {json.dumps(execute)};
                    
                    // 如果需要执行，模拟按 Enter 键
                    if (shouldExecute) {{
                        // 等待一小段时间确保输入已处理
                        await new Promise(resolve => setTimeout(resolve, 100));
                        
                        // 模拟按下 Enter 键
                        const enterEvent = new KeyboardEvent('keydown', {{
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true,
                            cancelable: true
                        }});
                        inputElement.dispatchEvent(enterEvent);
                        
                        const enterUpEvent = new KeyboardEvent('keyup', {{
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true,
                            cancelable: true
                        }});
                        inputElement.dispatchEvent(enterUpEvent);
                        
                        // 也尝试查找并点击发送按钮（备用方案）
                        const sendButton = document.querySelector('button[aria-label*="Send"]') ||
                                          document.querySelector('button[title*="Send"]') ||
                                          document.querySelector('button[type="submit"]');
                        if (sendButton) {{
                            sendButton.click();
                        }}
                    }}
                    
                    return JSON.stringify({{
                        success: currentContent.includes(textToInput) || currentContent.length > 0,
                        message: shouldExecute ? '文本已输入并执行' : '文本已输入到 Cursor',
                        executed: shouldExecute,
                        inputLength: textToInput.length,
                        currentLength: currentContent.length,
                        preview: currentContent.substring(0, 50)
                    }});
                }} catch (error) {{
                    return JSON.stringify({{
                        success: false,
                        error: error.message
                    }});
                }}
            }})()
            """
            
            # 发送 execute_js 消息给 inject（广播模式，不指定任何窗口参数）
            # V11.2: conversation_id 检查逻辑已在 js_code 中，无需传递给 inject
            execute_msg = MessageBuilder.execute_js(
                from_id="server",
                to_id=target_inject.client_id,
                code=js_code,
                request_id=f"input_text_{from_id}_{int(time.time())}"
                # 不传递 window_index 和 conversation_id，让 inject 广播到所有窗口
            )
            
            await target_inject.websocket.send(execute_msg.to_json())
            logger.info(f"📤 [Cursor Input] JS 代码已发送: server → {target_inject.client_id}")
            
            # 注意：这里不等待结果，直接返回成功（异步模式）
            # 如果需要等待结果，需要实现一个回调机制
            success_msg = MessageBuilder.cursor_input_text_result(
                from_id="server",
                to_id=from_id,
                success=True,
                message="输入请求已发送"
            )
            await client_info.websocket.send(success_msg.to_json())
            
        except Exception as e:
            logger.error(f"❌ [Cursor Input] 处理失败: {e}")
            # 发送失败响应
            error_msg = MessageBuilder.cursor_input_text_result(
                from_id="server",
                to_id=from_id,
                success=False,
                error=str(e)
            )
            await client_info.websocket.send(error_msg.to_json())
    else:
        logger.warning(f"⚠️  找不到目标 inject")
        error_msg = MessageBuilder.cursor_input_text_result(
            from_id="server",
            to_id=from_id,
            success=False,
            error="找不到目标 Cursor inject"
        )
        await client_info.websocket.send(error_msg.to_json())


async def handle_get_conversation_id(client_info: ClientInfo, message: Message):
    """
    处理 GET_CONVERSATION_ID 请求（V11.3 新增）
    通过生成 JavaScript 代码来查询所有窗口的 conversation_id
    """
    from_id = message.from_
    request_id = message.payload.get('request_id', f"discover_{int(time.time())}")
    
    logger.info(f"🔍 [Discovery] 收到 conversation_id 查询请求: {request_id} (from={from_id})")
    
    # 找到一个 inject 客户端
    inject_clients = registry.get_by_type("cursor_inject")
    
    if not inject_clients:
        logger.warning(f"⚠️  找不到 Cursor inject 客户端")
        # 返回空结果
        error_msg = MessageBuilder.get_conversation_id_result(
            from_id="server",
            to_id=from_id,
            request_id=request_id,
            success=False,
            conversation_id=None,
            error="没有可用的 Cursor inject"
        )
        await client_info.websocket.send(error_msg.to_json())
        return
    
    # 使用第一个 inject 客户端（广播模式）
    target_inject = inject_clients[0]
    
    # 生成 JavaScript 代码来查询所有窗口的 conversation_id
    js_code = """
    (async function() {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        
        if (windows.length === 0) {
            return JSON.stringify({
                success: false,
                conversations: [],
                error: '没有打开的窗口'
            });
        }
        
        const results = [];
        const extractConvIdCode = `(() => {
            const el = document.querySelector('[id^="composer-bottom-add-context-"]');
            if (!el) return null;
            const match = el.id.match(/composer-bottom-add-context-([a-f0-9-]+)/);
            return match ? match[1] : null;
        })()`;
        
        for (let i = 0; i < windows.length; i++) {
            try {
                const conversationId = await windows[i].webContents.executeJavaScript(extractConvIdCode);
                if (conversationId) {
                    results.push({
                        conversation_id: conversationId,
                        window_index: i
                    });
                }
            } catch (err) {
                // 忽略查询失败的窗口
            }
        }
        
        return JSON.stringify({
            success: true,
            conversations: results,
            total_windows: windows.length
        });
    })()
    """
    
    # 通过 EXECUTE_JS 发送
    execute_msg = MessageBuilder.execute_js(
        from_id="server",
        to_id=target_inject.client_id,
        code=js_code,
        request_id=f"get_conv_id_{request_id}",
        window_index=None,
        conversation_id=None
    )
    
    # 存储原始请求者信息，用于转发结果
    # 使用 request_id 作为 key，存储发送者信息
    if not hasattr(handle_get_conversation_id, 'pending_requests'):
        handle_get_conversation_id.pending_requests = {}
    
    handle_get_conversation_id.pending_requests[f"get_conv_id_{request_id}"] = {
        'requester_id': from_id,
        'original_request_id': request_id
    }
    
    await target_inject.websocket.send(execute_msg.to_json())
    logger.info(f"📤 [Discovery] 已发送查询脚本到 inject: {target_inject.client_id}")


async def handle_execute_js_result_for_discovery(message: Message):
    """
    处理 conversation_id 查询的结果
    """
    request_id = message.payload.get('request_id', '')
    
    # 检查是否是 discovery 请求的结果
    if not request_id.startswith('get_conv_id_'):
        return False
    
    if not hasattr(handle_get_conversation_id, 'pending_requests'):
        return False
    
    pending = handle_get_conversation_id.pending_requests.get(request_id)
    if not pending:
        return False
    
    # 移除待处理请求
    del handle_get_conversation_id.pending_requests[request_id]
    
    requester_id = pending['requester_id']
    original_request_id = pending['original_request_id']
    
    # 解析结果
    success = message.payload.get('success', False)
    result_str = message.payload.get('result', '{}')
    
    logger.info(f"📨 [Discovery] 收到查询结果: success={success}")
    
    if not success:
        # 执行失败
        error_msg = MessageBuilder.get_conversation_id_result(
            from_id="server",
            to_id=requester_id,
            request_id=original_request_id,
            success=False,
            conversation_id=None,
            error=message.payload.get('error', '查询失败')
        )
        
        requester = registry.get_by_id(requester_id)
        if requester:
            await requester.websocket.send(error_msg.to_json())
        return True
    
    # 解析返回的 JSON
    try:
        import json
        result_data = json.loads(result_str)
        conversations = result_data.get('conversations', [])
        
        logger.info(f"✅ [Discovery] 找到 {len(conversations)} 个对话")
        
        # 为每个 conversation_id 发送一个结果消息
        requester = registry.get_by_id(requester_id)
        if requester:
            for conv in conversations:
                conv_id = conv.get('conversation_id')
                window_index = conv.get('window_index')
                
                result_msg = MessageBuilder.get_conversation_id_result(
                    from_id="server",
                    to_id=requester_id,
                    request_id=original_request_id,
                    success=True,
                    conversation_id=conv_id,
                    window_index=window_index
                )
                await requester.websocket.send(result_msg.to_json())
                logger.info(f"  📤 发送结果: {conv_id} (window {window_index})")
        
        return True
    except Exception as e:
        logger.error(f"❌ [Discovery] 解析结果失败: {e}")
        error_msg = MessageBuilder.get_conversation_id_result(
            from_id="server",
            to_id=requester_id,
            request_id=original_request_id,
            success=False,
            conversation_id=None,
            error=f"解析结果失败: {str(e)}"
        )
        requester = registry.get_by_id(requester_id)
        if requester:
            await requester.websocket.send(error_msg.to_json())
        return True


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

async def handle_client(websocket):
    """处理客户端连接"""
    client_addr = websocket.remote_address
    logger.info(f"✅ 新连接: {client_addr}")
    
    # 创建临时客户端信息（等待注册）
    temp_id = f"temp-{id(websocket)}"
    client_info = ClientInfo(websocket, temp_id, {"unknown"})  # 🆕 使用 set 而不是字符串
    
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
