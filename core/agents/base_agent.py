"""
BaseAgent - 所有AI Agent的基类
"""
print("--- [DEBUG] Loading core/agents/base_agent.py ---")

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging


# Forward declaration to avoid circular import
_activity_logger = None

def _get_activity_logger():
    """懒加载activity_logger以避免循环导入"""
    global _activity_logger
    if _activity_logger is None:
        from .activity_logger import activity_logger
        _activity_logger = activity_logger
    return _activity_logger


class AgentType(Enum):
    """Agent类型枚举"""
    BUTLER = "butler"  # 管家Agent - 中央协调者
    MONITORING = "monitoring"  # 监控Agent
    OPTIMIZATION = "optimization"  # 优化Agent
    NEGOTIATION = "negotiation"  # 谈判Agent


class MessageType(Enum):
    """消息类型"""
    TASK = "task"  # 任务
    RESULT = "result"  # 结果
    NOTIFICATION = "notification"  # 通知
    QUERY = "query"  # 查询
    COMMAND = "command"  # 命令


@dataclass
class AgentMessage:
    """Agent间通信消息"""
    from_agent: str
    to_agent: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: f"msg_{datetime.now().timestamp()}")
    priority: int = 0  # 0=normal, 1=high, 2=urgent


@dataclass
class AgentContext:
    """Agent执行上下文"""
    user_id: str
    subscriptions: List[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    automation_level: str = 'manual'  # 'manual', 'semi_auto', 'full_auto'
    current_time: datetime = field(default_factory=datetime.now)
    budget_limit: Optional[float] = None


class BaseAgent(ABC):
    """所有Agent的抽象基类"""

    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self._message_queue: List[AgentMessage] = []
        self._current_user_id: Optional[str] = None  # 用于活动日志记录

    @abstractmethod
    async def process_message(self, message: AgentMessage, context: AgentContext) -> Optional[AgentMessage]:
        """
        处理接收到的消息

        Args:
            message: 接收的消息
            context: 执行上下文

        Returns:
            响应消息（如果有）
        """
        pass

    @abstractmethod
    async def execute_task(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """
        执行具体任务

        Args:
            task: 任务描述
            context: 执行上下文

        Returns:
            任务执行结果
        """
        pass

    def send_message(self, to_agent: str, message_type: MessageType,
                    content: Dict[str, Any], priority: int = 0) -> AgentMessage:
        """
        发送消息到其他Agent

        Args:
            to_agent: 目标Agent ID
            message_type: 消息类型
            content: 消息内容
            priority: 优先级

        Returns:
            创建的消息对象
        """
        message = AgentMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            priority=priority
        )
        self.logger.info(f"Sent {message_type.value} to {to_agent}: {message.message_id}")
        return message

    def receive_message(self, message: AgentMessage):
        """
        接收消息到队列

        Args:
            message: 接收的消息
        """
        self._message_queue.append(message)
        self._message_queue.sort(key=lambda m: (-m.priority, m.timestamp))
        self.logger.info(f"Received {message.message_type.value} from {message.from_agent}")

    async def process_queue(self, context: AgentContext) -> List[AgentMessage]:
        """
        处理消息队列

        Args:
            context: 执行上下文

        Returns:
            响应消息列表
        """
        responses = []
        while self._message_queue:
            message = self._message_queue.pop(0)
            try:
                response = await self.process_message(message, context)
                if response:
                    responses.append(response)
            except Exception as e:
                self.logger.error(f"Error processing message {message.message_id}: {e}")
                # 发送错误响应
                error_response = self.send_message(
                    to_agent=message.from_agent,
                    message_type=MessageType.RESULT,
                    content={
                        "status": "error",
                        "error": str(e),
                        "original_message_id": message.message_id
                    }
                )
                responses.append(error_response)
        return responses

    def log_action(self, action: str, details: Dict[str, Any], status: str = "success"):
        """
        记录Agent动作（用于审计和可解释性）

        Args:
            action: 动作名称
            status: 状态 (success, failed, pending)
            details: 动作详情
        """
        self.logger.info(f"Action: {action}", extra={
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

        # 同时记录到活动日志系统
        try:
            from .activity_logger import ActivityType
            logger = _get_activity_logger()

            logger.log_activity(
                agent_id=self.agent_id,
                agent_type=self.agent_type.value,
                activity_type=ActivityType.ACTION_TAKEN,
                description=action,
                details=details,
                user_id=self._current_user_id,
                status=status
            )
        except Exception as e:
            self.logger.error(f"Failed to log to activity logger: {e}")
