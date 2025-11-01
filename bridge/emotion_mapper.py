"""
情感映射器 - 将编程事件映射到表情和对话
Emotion Mapper - Maps coding events to emotions and messages
"""
import yaml
import random
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EmotionEvent:
    """表情事件数据类"""
    event_type: str
    emotion: str
    message: str
    priority: int
    timestamp: datetime
    metadata: Dict = None


class EmotionMapper:
    """情感映射器"""
    
    def __init__(self, config_path: str = 'config/emotion_rules.yaml'):
        """
        初始化映射器
        
        Args:
            config_path: 配置文件路径
        """
        config_file = Path(__file__).parent / config_path
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.event_history: List[EmotionEvent] = []
        self.last_emotion: Optional[str] = 'neutral'
        self.emotion_change_time: Optional[datetime] = None
        
        print("🎨 EmotionMapper initialized")
        print(f"📋 Loaded {len(self.config['events'])} event types")
    
    def map_event(self, event_type: str, metadata: Dict = None) -> EmotionEvent:
        """
        将事件映射到表情和消息
        
        Args:
            event_type: 事件类型（如 'git_commit', 'syntax_error'）
            metadata: 事件元数据（如文件名、错误信息等）
        
        Returns:
            EmotionEvent: 包含表情和消息的事件对象
        """
        metadata = metadata or {}
        
        # 获取事件配置
        event_config = self.config['events'].get(event_type)
        if not event_config:
            # 未知事件，使用默认配置
            print(f"⚠️  Unknown event type: {event_type}, using default")
            return EmotionEvent(
                event_type=event_type,
                emotion='neutral',
                message=f"收到事件: {event_type}",
                priority=1,
                timestamp=datetime.now(),
                metadata=metadata
            )
        
        # 选择消息（随机）
        messages = event_config['messages']
        message = random.choice(messages)
        
        # 替换消息模板中的变量
        message = self._format_message(message, metadata)
        
        # 检查上下文规则
        emotion = event_config['emotion']
        if event_config.get('context_aware'):
            context_emotion, context_message = self._check_context_rules(event_type)
            if context_emotion:
                emotion = context_emotion
                message = context_message or message
        
        # 创建事件
        event = EmotionEvent(
            event_type=event_type,
            emotion=emotion,
            message=message,
            priority=event_config['priority'],
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        # 记录事件历史
        self.event_history.append(event)
        
        # 限制历史记录长度
        if len(self.event_history) > 100:
            self.event_history = self.event_history[-100:]
        
        print(f"✅ Mapped: {event_type} -> [{emotion}] {message}")
        
        return event
    
    def _format_message(self, template: str, metadata: Dict) -> str:
        """格式化消息模板"""
        try:
            return template.format(**metadata)
        except KeyError:
            # 如果缺少某些键，返回原始模板
            return template
    
    def _check_context_rules(self, event_type: str) -> tuple[Optional[str], Optional[str]]:
        """检查上下文规则，返回 (emotion, message) 或 (None, None)"""
        context_rules = self.config.get('context_rules', {})
        
        # 检查连续成功
        if 'consecutive_success' in context_rules:
            rule = context_rules['consecutive_success']
            success_events = ['git_commit', 'test_pass', 'ai_complete', 'bug_fixed']
            recent_successes = [
                e for e in self.event_history[-10:]
                if e.event_type in success_events
            ]
            if len(recent_successes) >= rule['threshold']:
                message = random.choice(rule['messages']).format(count=len(recent_successes))
                return rule['emotion'], message
        
        # 检查连续失败
        if 'consecutive_failure' in context_rules:
            rule = context_rules['consecutive_failure']
            failure_events = ['syntax_error', 'runtime_error', 'test_fail', 'build_error']
            recent_failures = [
                e for e in self.event_history[-10:]
                if e.event_type in failure_events
            ]
            if len(recent_failures) >= rule['threshold']:
                message = random.choice(rule['messages']).format(count=len(recent_failures))
                return rule['emotion'], message
        
        return None, None
    
    def should_interrupt(self, new_event: EmotionEvent) -> bool:
        """判断新事件是否应该打断当前表情"""
        if not self.emotion_change_time:
            return True
        
        # 获取当前表情的持续时间配置
        duration_config = self.config.get('emotion_duration', {})
        current_duration = duration_config.get(self.last_emotion, 5)
        
        # 如果当前表情还没结束
        elapsed = (datetime.now() - self.emotion_change_time).total_seconds()
        if elapsed < current_duration:
            # 只有更高优先级的事件才能打断
            if self.event_history:
                last_priority = self.event_history[-1].priority
                if new_event.priority > last_priority:
                    print(f"⚡ Interrupting with higher priority: {new_event.priority} > {last_priority}")
                    return True
                return False
        
        return True
    
    def get_statistics(self) -> Dict:
        """获取事件统计信息"""
        total = len(self.event_history)
        if total == 0:
            return {'total': 0}
        
        # 统计各种表情的次数
        emotion_counts = {}
        for event in self.event_history:
            emotion_counts[event.emotion] = emotion_counts.get(event.emotion, 0) + 1
        
        # 统计各种事件类型的次数
        event_counts = {}
        for event in self.event_history:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        
        return {
            'total': total,
            'emotions': emotion_counts,
            'events': event_counts,
            'recent': [
                {'type': e.event_type, 'emotion': e.emotion, 'message': e.message}
                for e in self.event_history[-5:]
            ]
        }


if __name__ == '__main__':
    # 测试代码
    print("=" * 60)
    print("🧪 Testing EmotionMapper")
    print("=" * 60)
    
    mapper = EmotionMapper()
    
    # 测试几个事件
    test_cases = [
        ('file_save', {'filename': 'test.py'}),
        ('git_commit', {'files': 3}),
        ('test_pass', {'passed': 10}),
        ('syntax_error', {'error': 'undefined variable'}),
        ('celebration', {}),
    ]
    
    print("\n📝 Testing event mapping:\n")
    
    for event_type, metadata in test_cases:
        event = mapper.map_event(event_type, metadata)
        print(f"  [{event.emotion:10s}] {event.message}")
    
    print("\n" + "=" * 60)
    print("📊 Statistics:")
    print("=" * 60)
    stats = mapper.get_statistics()
    print(f"Total events: {stats['total']}")
    print(f"Emotions: {stats['emotions']}")
    print("\n✅ Test completed!")

