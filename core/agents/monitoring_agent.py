"""
MonitoringAgent - 订阅监控Agent
负责24/7监控订阅状态、价格变化、使用情况等
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base_agent import BaseAgent, AgentType, AgentMessage, AgentContext, MessageType
from core.database.data_interface import data_manager


class MonitoringAgent(BaseAgent):
    """监控Agent - 持续监控订阅状态"""

    def __init__(self, agent_id: str = "monitoring_agent"):
        super().__init__(agent_id, AgentType.MONITORING)
        self.monitoring_rules = {
            "price_change_threshold": 0.05,  # 价格变动5%触发通知
            "renewal_alert_days": 7,  # 续费前7天提醒
            "unused_days_threshold": 30,  # 30天未使用标记为闲置
            "cost_spike_threshold": 1.5  # 月度支出超过1.5倍平均值触发预警
        }

    async def process_message(self, message: AgentMessage, context: AgentContext) -> Optional[AgentMessage]:
        """处理接收到的消息"""
        if message.message_type == MessageType.COMMAND:
            command = message.content.get("command")

            if command == "scan_all":
                result = await self.scan_all_subscriptions(context)
                return self.send_message(
                    to_agent=message.from_agent,
                    message_type=MessageType.RESULT,
                    content=result
                )

            elif command == "check_renewals":
                result = await self.check_upcoming_renewals(context)
                return self.send_message(
                    to_agent=message.from_agent,
                    message_type=MessageType.RESULT,
                    content=result
                )

        elif message.message_type == MessageType.QUERY:
            query_type = message.content.get("query_type")

            if query_type == "subscription_health":
                result = await self.analyze_subscription_health(
                    context,
                    message.content.get("subscription_id")
                )
                return self.send_message(
                    to_agent=message.from_agent,
                    message_type=MessageType.RESULT,
                    content=result
                )

        return None

    async def execute_task(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """执行监控任务"""
        task_type = task.get("type")

        if task_type == "daily_scan":
            return await self.scan_all_subscriptions(context)
        elif task_type == "price_monitoring":
            return await self.monitor_price_changes(context)
        elif task_type == "usage_analysis":
            return await self.analyze_usage_patterns(context)
        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}

    async def scan_all_subscriptions(self, context: AgentContext) -> Dict[str, Any]:
        """
        扫描所有订阅，识别异常和需要关注的项

        Returns:
            扫描结果和发现的问题
        """
        issues = []
        insights = []

        for subscription in context.subscriptions:
            # 检查即将续费
            renewal_issue = self._check_renewal_alert(subscription)
            if renewal_issue:
                issues.append(renewal_issue)

            # 检查价格异常
            price_issue = self._check_price_anomaly(subscription)
            if price_issue:
                issues.append(price_issue)

            # 检查使用情况
            usage_insight = self._analyze_usage(subscription, context)
            if usage_insight:
                insights.append(usage_insight)

        self.log_action("scan_all_subscriptions", {
            "subscriptions_scanned": len(context.subscriptions),
            "issues_found": len(issues),
            "insights_generated": len(insights)
        })

        return {
            "status": "success",
            "scan_time": datetime.now().isoformat(),
            "subscriptions_count": len(context.subscriptions),
            "issues": issues,
            "insights": insights
        }

    async def check_upcoming_renewals(self, context: AgentContext) -> Dict[str, Any]:
        """
        检查即将到期的订阅

        Returns:
            即将续费的订阅列表
        """
        upcoming_renewals = []

        for subscription in context.subscriptions:
            if subscription.get("status") != "active":
                continue

            next_billing = self._calculate_next_billing(subscription)
            if not next_billing:
                continue

            days_until_renewal = (next_billing - datetime.now()).days

            if 0 <= days_until_renewal <= self.monitoring_rules["renewal_alert_days"]:
                upcoming_renewals.append({
                    "subscription_id": subscription["id"],
                    "service_name": subscription["service_name"],
                    "next_billing_date": next_billing.isoformat(),
                    "days_until_renewal": days_until_renewal,
                    "amount": subscription["price"],
                    "currency": subscription["currency"]
                })

        self.log_action("check_upcoming_renewals", {
            "upcoming_count": len(upcoming_renewals)
        })

        return {
            "status": "success",
            "upcoming_renewals": upcoming_renewals
        }

    async def monitor_price_changes(self, context: AgentContext) -> Dict[str, Any]:
        """
        监控价格变化（需要历史价格数据）

        Returns:
            价格变化报告
        """
        # 这里需要历史价格数据，当前版本返回占位符
        # 未来需要实现价格历史记录功能

        self.log_action("monitor_price_changes", {
            "note": "Price monitoring requires historical data - to be implemented"
        })

        return {
            "status": "pending",
            "message": "Price monitoring requires historical price data",
            "action_required": "Implement price history tracking"
        }

    async def analyze_usage_patterns(self, context: AgentContext) -> Dict[str, Any]:
        """
        分析使用模式（需要使用数据）

        Returns:
            使用模式分析
        """
        # 这里需要使用数据，当前版本返回占位符
        # 未来需要集成使用跟踪功能

        self.log_action("analyze_usage_patterns", {
            "note": "Usage analysis requires usage tracking data - to be implemented"
        })

        return {
            "status": "pending",
            "message": "Usage analysis requires usage tracking integration",
            "action_required": "Implement usage data collection"
        }

    async def analyze_subscription_health(self, context: AgentContext,
                                         subscription_id: str) -> Dict[str, Any]:
        """
        分析单个订阅的健康状况

        Args:
            subscription_id: 订阅ID

        Returns:
            订阅健康分析
        """
        subscription = next(
            (s for s in context.subscriptions if s["id"] == subscription_id),
            None
        )

        if not subscription:
            return {
                "status": "error",
                "message": f"Subscription {subscription_id} not found"
            }

        health_score = 100
        issues = []

        # 检查续费状态
        next_billing = self._calculate_next_billing(subscription)
        if next_billing:
            days_until = (next_billing - datetime.now()).days
            if days_until <= 3:
                health_score -= 20
                issues.append(f"Renewal in {days_until} days")

        # 检查价格合理性（与同类服务比较）
        category_avg = self._calculate_category_average_price(
            context.subscriptions,
            subscription["category"]
        )
        if subscription["price"] > category_avg * 1.5:
            health_score -= 15
            issues.append(f"Price {subscription['price']} is 50% above category average")

        return {
            "status": "success",
            "subscription_id": subscription_id,
            "service_name": subscription["service_name"],
            "health_score": health_score,
            "issues": issues,
            "recommendation": self._generate_recommendation(health_score, issues)
        }

    # Private helper methods

    def _check_renewal_alert(self, subscription: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检查续费提醒"""
        if subscription.get("status") != "active":
            return None

        next_billing = self._calculate_next_billing(subscription)
        if not next_billing:
            return None

        days_until = (next_billing - datetime.now()).days

        if 0 <= days_until <= self.monitoring_rules["renewal_alert_days"]:
            return {
                "type": "renewal_alert",
                "severity": "high" if days_until <= 3 else "medium",
                "subscription_id": subscription["id"],
                "service_name": subscription["service_name"],
                "message": f"Renewal in {days_until} days",
                "next_billing_date": next_billing.isoformat(),
                "amount": subscription["price"]
            }

        return None

    def _check_price_anomaly(self, subscription: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检查价格异常（需要历史数据）"""
        # 占位符 - 需要历史价格数据
        return None

    def _analyze_usage(self, subscription: Dict[str, Any],
                      context: AgentContext) -> Optional[Dict[str, Any]]:
        """分析使用情况"""
        # 占位符 - 需要使用数据
        return None

    def _calculate_next_billing(self, subscription: Dict[str, Any]) -> Optional[datetime]:
        """计算下次计费日期"""
        start_date_str = subscription.get("start_date")
        if not start_date_str:
            return None

        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

        billing_cycle = subscription.get("billing_cycle", "monthly")
        today = datetime.now()

        if billing_cycle == "monthly":
            # 简化计算：从开始日期每月递增
            months_passed = (today.year - start_date.year) * 12 + (today.month - start_date.month)
            next_billing = start_date
            for _ in range(months_passed + 1):
                next_billing = self._add_months(next_billing, 1)
                if next_billing > today:
                    return next_billing

        elif billing_cycle == "yearly":
            years_passed = today.year - start_date.year
            next_billing = start_date.replace(year=start_date.year + years_passed + 1)
            return next_billing

        elif billing_cycle == "weekly":
            days_passed = (today - start_date).days
            weeks_passed = days_passed // 7
            next_billing = start_date + timedelta(weeks=weeks_passed + 1)
            return next_billing

        elif billing_cycle == "daily":
            next_billing = today + timedelta(days=1)
            return next_billing

        return None

    def _add_months(self, date: datetime, months: int) -> datetime:
        """日期增加月份"""
        month = date.month - 1 + months
        year = date.year + month // 12
        month = month % 12 + 1
        day = min(date.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                              31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return date.replace(year=year, month=month, day=day)

    def _calculate_category_average_price(self, subscriptions: List[Dict[str, Any]],
                                         category: str) -> float:
        """计算分类平均价格"""
        category_subs = [s for s in subscriptions if s.get("category") == category]
        if not category_subs:
            return 0.0

        # 统一转换为月度价格
        monthly_prices = []
        for sub in category_subs:
            price = sub["price"]
            cycle = sub.get("billing_cycle", "monthly")

            if cycle == "yearly":
                price = price / 12
            elif cycle == "weekly":
                price = price * 4
            elif cycle == "daily":
                price = price * 30

            monthly_prices.append(price)

        return sum(monthly_prices) / len(monthly_prices)

    def _generate_recommendation(self, health_score: int, issues: List[str]) -> str:
        """生成推荐建议"""
        if health_score >= 80:
            return "Subscription is healthy"
        elif health_score >= 60:
            return "Consider reviewing this subscription"
        else:
            return "Action recommended: " + "; ".join(issues)
