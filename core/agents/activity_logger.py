"""
Agent活动日志系统 - 记录和管理Agent活动
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json


class ActivityType(Enum):
    """活动类型"""
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    DECISION_MADE = "decision_made"
    ACTION_TAKEN = "action_taken"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class AgentActivity:
    """Agent活动记录"""
    activity_id: str
    agent_id: str
    agent_type: str
    activity_type: ActivityType
    timestamp: datetime
    description: str
    details: Dict[str, Any]
    user_id: Optional[str] = None
    related_subscription_id: Optional[str] = None
    status: str = "success"  # success, failed, pending

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["activity_type"] = self.activity_type.value
        data["timestamp"] = self.timestamp.isoformat()
        return data


class AgentActivityLogger:
    """Agent活动日志记录器"""

    def __init__(self, max_logs: int = 1000):
        self.activities: List[AgentActivity] = []
        self.max_logs = max_logs
        self._activity_counter = 0

    def log_activity(
        self,
        agent_id: str,
        agent_type: str,
        activity_type: ActivityType,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        related_subscription_id: Optional[str] = None,
        status: str = "success"
    ) -> str:
        """
        记录Agent活动

        Args:
            agent_id: Agent ID
            agent_type: Agent类型
            activity_type: 活动类型
            description: 活动描述
            details: 详细信息
            user_id: 相关用户ID
            related_subscription_id: 相关订阅ID
            status: 状态

        Returns:
            活动ID
        """
        self._activity_counter += 1
        activity_id = f"activity_{self._activity_counter}_{int(datetime.now().timestamp())}"

        activity = AgentActivity(
            activity_id=activity_id,
            agent_id=agent_id,
            agent_type=agent_type,
            activity_type=activity_type,
            timestamp=datetime.now(),
            description=description,
            details=details or {},
            user_id=user_id,
            related_subscription_id=related_subscription_id,
            status=status
        )

        self.activities.append(activity)

        # 限制日志数量
        if len(self.activities) > self.max_logs:
            self.activities = self.activities[-self.max_logs:]

        return activity_id

    def get_activities(
        self,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        activity_type: Optional[ActivityType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AgentActivity]:
        """
        获取活动记录

        Args:
            agent_id: 筛选特定Agent
            user_id: 筛选特定用户
            activity_type: 筛选活动类型
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回数量限制

        Returns:
            活动记录列表
        """
        filtered = self.activities

        # 应用筛选条件
        if agent_id:
            filtered = [a for a in filtered if a.agent_id == agent_id]

        if user_id:
            filtered = [a for a in filtered if a.user_id == user_id]

        if activity_type:
            filtered = [a for a in filtered if a.activity_type == activity_type]

        if start_time:
            filtered = [a for a in filtered if a.timestamp >= start_time]

        if end_time:
            filtered = [a for a in filtered if a.timestamp <= end_time]

        # 按时间倒序排序
        filtered.sort(key=lambda x: x.timestamp, reverse=True)

        return filtered[:limit]

    def get_activity_stats(
        self,
        user_id: Optional[str] = None,
        time_window: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """
        获取活动统计

        Args:
            user_id: 用户ID
            time_window: 统计时间窗口

        Returns:
            统计信息
        """
        start_time = datetime.now() - time_window
        activities = self.get_activities(
            user_id=user_id,
            start_time=start_time,
            limit=10000
        )

        # 按Agent类型统计
        by_agent_type = {}
        by_activity_type = {}
        by_status = {"success": 0, "failed": 0, "pending": 0}

        for activity in activities:
            # Agent类型统计
            agent_type = activity.agent_type
            if agent_type not in by_agent_type:
                by_agent_type[agent_type] = 0
            by_agent_type[agent_type] += 1

            # 活动类型统计
            activity_type = activity.activity_type.value
            if activity_type not in by_activity_type:
                by_activity_type[activity_type] = 0
            by_activity_type[activity_type] += 1

            # 状态统计
            status = activity.status
            if status in by_status:
                by_status[status] += 1

        return {
            "total_activities": len(activities),
            "time_window_days": time_window.days,
            "by_agent_type": by_agent_type,
            "by_activity_type": by_activity_type,
            "by_status": by_status,
            "most_active_agent": max(by_agent_type.items(), key=lambda x: x[1])[0] if by_agent_type else None,
            "success_rate": by_status["success"] / len(activities) * 100 if activities else 0
        }

    def get_recent_errors(self, limit: int = 10) -> List[AgentActivity]:
        """获取最近的错误记录"""
        errors = [
            a for a in self.activities
            if a.activity_type == ActivityType.ERROR_OCCURRED or a.status == "failed"
        ]
        errors.sort(key=lambda x: x.timestamp, reverse=True)
        return errors[:limit]

    def clear_old_logs(self, days_to_keep: int = 30):
        """清理旧日志"""
        cutoff_time = datetime.now() - timedelta(days=days_to_keep)
        self.activities = [
            a for a in self.activities
            if a.timestamp >= cutoff_time
        ]

    def export_logs(
        self,
        filepath: str,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ):
        """导出日志到文件"""
        activities = self.get_activities(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            limit=10000
        )

        data = [a.to_dict() for a in activities]

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# 全局活动日志记录器实例
activity_logger = AgentActivityLogger(max_logs=5000)
