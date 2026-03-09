"""
订阅提醒系统 - 管理订阅续费提醒和通知
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import logging


class ReminderType(Enum):
    """提醒类型"""
    UPCOMING_RENEWAL = "upcoming_renewal"  # 即将续费
    TRIAL_ENDING = "trial_ending"  # 试用期结束
    PRICE_CHANGE = "price_change"  # 价格变动
    PAYMENT_FAILED = "payment_failed"  # 支付失败
    CUSTOM = "custom"  # 自定义提醒


class ReminderPriority(Enum):
    """提醒优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ReminderSystem:
    """订阅提醒系统"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_next_billing_date(
        self,
        start_date: datetime,
        billing_cycle: str,
        occurrences: int = 1
    ) -> datetime:
        """
        计算下次账单日期

        Args:
            start_date: 开始日期（首次订阅或上次续费日期）
            billing_cycle: 计费周期 (daily/weekly/monthly/yearly)
            occurrences: 发生次数（默认1，表示下一次）

        Returns:
            下次账单日期
        """
        if billing_cycle == "daily":
            return start_date + timedelta(days=1 * occurrences)
        elif billing_cycle == "weekly":
            return start_date + timedelta(weeks=1 * occurrences)
        elif billing_cycle == "monthly":
            # 处理月份边界情况
            month = start_date.month + occurrences
            year = start_date.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1

            # 处理日期溢出（如1月31日 + 1月 = 2月28/29日）
            day = min(start_date.day, self._get_days_in_month(year, month))

            return datetime(year, month, day, start_date.hour, start_date.minute)
        elif billing_cycle == "yearly":
            year = start_date.year + occurrences
            # 处理闰年2月29日的情况
            if start_date.month == 2 and start_date.day == 29:
                day = 28 if not self._is_leap_year(year) else 29
            else:
                day = start_date.day
            return datetime(year, start_date.month, day, start_date.hour, start_date.minute)
        else:
            raise ValueError(f"不支持的计费周期: {billing_cycle}")

    def _is_leap_year(self, year: int) -> bool:
        """判断是否为闰年"""
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    def _get_days_in_month(self, year: int, month: int) -> int:
        """获取某月的天数"""
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        elif month == 2:
            return 29 if self._is_leap_year(year) else 28
        else:
            raise ValueError(f"无效的月份: {month}")

    def calculate_days_until_renewal(
        self,
        next_billing_date: datetime
    ) -> int:
        """
        计算距离下次续费的天数

        Args:
            next_billing_date: 下次账单日期

        Returns:
            剩余天数（负数表示已过期）
        """
        now = datetime.now()
        delta = next_billing_date - now
        return delta.days

    def generate_reminders(
        self,
        subscriptions: List[Dict[str, Any]],
        reminder_days: List[int] = [7, 3, 1, 0]
    ) -> List[Dict[str, Any]]:
        """
        生成订阅提醒列表

        Args:
            subscriptions: 订阅列表
            reminder_days: 提醒天数列表（在账单日前N天提醒）

        Returns:
            提醒列表
        """
        reminders = []
        now = datetime.now()

        for sub in subscriptions:
            # 跳过非活跃订阅
            if sub.get("status") != "active":
                continue

            # 获取或计算首次订阅日期
            start_date_str = sub.get("start_date") or sub.get("created_at")
            if not start_date_str:
                # 如果没有日期，使用当前日期
                start_date = now
            else:
                # 解析日期字符串
                try:
                    start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
                except:
                    start_date = now

            # 计算下次账单日期
            billing_cycle = sub.get("billing_cycle", "monthly")

            # 如果订阅刚创建，下次账单是一个周期后
            # 否则，需要计算已经过了多少个周期
            next_billing = self._calculate_next_billing_from_start(
                start_date, billing_cycle, now
            )

            # 计算剩余天数
            days_until = self.calculate_days_until_renewal(next_billing)

            # 生成提醒
            for reminder_day in reminder_days:
                if days_until == reminder_day:
                    priority = self._get_priority_by_days(days_until)

                    reminder = {
                        "subscription_id": sub.get("id"),
                        "service_name": sub.get("service_name"),
                        "type": ReminderType.UPCOMING_RENEWAL.value,
                        "priority": priority.value,
                        "days_until_renewal": days_until,
                        "next_billing_date": next_billing.isoformat(),
                        "amount": sub.get("price", 0),
                        "currency": sub.get("currency", "CNY"),
                        "message": self._generate_reminder_message(
                            sub.get("service_name"),
                            days_until,
                            sub.get("price", 0),
                            sub.get("currency", "CNY")
                        ),
                        "created_at": now.isoformat()
                    }
                    reminders.append(reminder)

        return reminders

    def _calculate_next_billing_from_start(
        self,
        start_date: datetime,
        billing_cycle: str,
        current_date: datetime
    ) -> datetime:
        """从开始日期计算下一个账单日期"""
        next_billing = start_date

        # 找到第一个在当前日期之后的账单日期
        occurrences = 1
        while next_billing <= current_date:
            occurrences += 1
            next_billing = self.calculate_next_billing_date(
                start_date, billing_cycle, occurrences - 1
            )

        return next_billing

    def _get_priority_by_days(self, days_until: int) -> ReminderPriority:
        """根据剩余天数确定优先级"""
        if days_until < 0:
            return ReminderPriority.URGENT
        elif days_until == 0:
            return ReminderPriority.HIGH
        elif days_until <= 3:
            return ReminderPriority.MEDIUM
        else:
            return ReminderPriority.LOW

    def _generate_reminder_message(
        self,
        service_name: str,
        days_until: int,
        amount: float,
        currency: str
    ) -> str:
        """生成提醒消息"""
        if days_until < 0:
            return f"⚠️ {service_name} 订阅已过期 {abs(days_until)} 天"
        elif days_until == 0:
            return f"🔔 {service_name} 今天续费，金额 {currency}{amount:.2f}"
        elif days_until == 1:
            return f"📅 {service_name} 明天续费，金额 {currency}{amount:.2f}"
        elif days_until <= 3:
            return f"📌 {service_name} {days_until}天后续费，金额 {currency}{amount:.2f}"
        else:
            return f"ℹ️ {service_name} {days_until}天后续费，金额 {currency}{amount:.2f}"

    def get_upcoming_renewals(
        self,
        subscriptions: List[Dict[str, Any]],
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """
        获取未来N天内需要续费的订阅

        Args:
            subscriptions: 订阅列表
            days_ahead: 查看未来多少天（默认30天）

        Returns:
            即将续费的订阅列表（包含续费日期）
        """
        upcoming = []
        now = datetime.now()

        for sub in subscriptions:
            if sub.get("status") != "active":
                continue

            # 获取开始日期
            start_date_str = sub.get("start_date") or sub.get("created_at")
            if not start_date_str:
                start_date = now
            else:
                try:
                    start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
                except:
                    start_date = now

            # 计算下次账单日期
            billing_cycle = sub.get("billing_cycle", "monthly")
            next_billing = self._calculate_next_billing_from_start(
                start_date, billing_cycle, now
            )

            # 检查是否在指定天数内
            days_until = self.calculate_days_until_renewal(next_billing)

            if 0 <= days_until <= days_ahead:
                upcoming.append({
                    **sub,
                    "next_billing_date": next_billing.isoformat(),
                    "days_until_renewal": days_until
                })

        # 按日期排序
        upcoming.sort(key=lambda x: x["days_until_renewal"])

        return upcoming

    def get_reminder_statistics(
        self,
        subscriptions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        获取提醒统计信息

        Args:
            subscriptions: 订阅列表

        Returns:
            统计数据
        """
        reminders = self.generate_reminders(subscriptions, [7, 3, 1, 0, -1])

        stats = {
            "total_reminders": len(reminders),
            "by_priority": {
                "urgent": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "upcoming_7days": 0,
            "upcoming_3days": 0,
            "due_today": 0,
            "overdue": 0,
            "total_amount_due": 0
        }

        for reminder in reminders:
            # 按优先级统计
            priority = reminder.get("priority", "low")
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

            # 按时间统计
            days = reminder.get("days_until_renewal", 0)
            if days < 0:
                stats["overdue"] += 1
            elif days == 0:
                stats["due_today"] += 1
                stats["total_amount_due"] += reminder.get("amount", 0)
            elif days <= 3:
                stats["upcoming_3days"] += 1
                stats["total_amount_due"] += reminder.get("amount", 0)
            elif days <= 7:
                stats["upcoming_7days"] += 1

        return stats


# 创建全局实例
reminder_system = ReminderSystem()