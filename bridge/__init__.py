"""
Event Bridge - オルテンシア情感控制系统
Converts coding events to Ortensia's emotions and dialogues
"""

__version__ = '1.0.0'
__author__ = 'CursorGirl Team'

from .emotion_mapper import EmotionMapper, EmotionEvent
from .websocket_client import WebSocketClient, get_client

__all__ = [
    'EmotionMapper',
    'EmotionEvent',
    'WebSocketClient',
    'get_client',
]

