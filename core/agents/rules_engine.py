"""
Rules Engine - 自主规则引擎
基于用户偏好和规则自动执行订阅管理操作
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging


class RuleConditionType(Enum):
    """规则条件类型"""
    PRICE_CHANGE = "price_change"
    RENEWAL_DUE = "renewal_due"
    UNUSED_PERIOD = "unused_period"
    BUDGET_EXCEEDED = "budget_exceeded"
    BETTER_ALTERNATIVE = "better_alternative"
    SUBSCRIPTION_COUNT = "subscription_count"
    REDUNDANT_FEATURE = "redundant_feature"  # 分类功能冗余
    ANNUAL_POTENTIAL = "annual_potential"    # 转年付潜力


class RuleActionType(Enum):
    """规则动作类型"""
    NOTIFY_USER = "notify_user"
    PAUSE_SUBSCRIPTION = "pause_subscription"
    CANCEL_SUBSCRIPTION = "cancel_subscription"
    DOWNGRADE_PLAN = "downgrade_plan"
    SUGGEST_ALTERNATIVE = "suggest_alternative"
    REQUEST_DISCOUNT = "request_discount"
    AUTO_RENEW_OFF = "auto_renew_off"


class RuleExecutionMode(Enum):
    """规则执行模式"""
    MANUAL = "manual"  # 仅通知，需用户确认
    SEMI_AUTO = "semi_auto"  # 低风险自动执行，高风险需确认
    FULL_AUTO = "full_auto"  # 完全自动执行


@dataclass
class RuleCondition:
    """规则条件"""
    condition_type: RuleConditionType
    parameters: Dict[str, Any]  # 条件参数，如阈值、天数等

    def evaluate(self, subscription: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        评估条件是否满足

        Args:
            subscription: 订阅数据
            context: 上下文数据（如历史价格、使用数据等）

        Returns:
            条件是否满足
        """
        if self.condition_type == RuleConditionType.PRICE_CHANGE:
            threshold = self.parameters.get("threshold", 0.05)
            historical_price = context.get("historical_price")
            if historical_price:
                current_price = subscription.get("price", 0)
                change_rate = abs(current_price - historical_price) / historical_price
                return change_rate > threshold
            return False

        elif self.condition_type == RuleConditionType.RENEWAL_DUE:
            days_threshold = self.parameters.get("days", 7)
            next_billing = context.get("next_billing_date")
            if next_billing:
                if isinstance(next_billing, str):
                    next_billing = datetime.fromisoformat(next_billing)
                days_until = (next_billing - datetime.now()).days
                return 0 <= days_until <= days_threshold
            return False

        elif self.condition_type == RuleConditionType.UNUSED_PERIOD:
            days_threshold = self.parameters.get("days", 30)
            last_used = context.get("last_used_date")
            if last_used:
                if isinstance(last_used, str):
                    last_used = datetime.fromisoformat(last_used)
                days_unused = (datetime.now() - last_used).days
                return days_unused > days_threshold
            return False

        elif self.condition_type == RuleConditionType.BUDGET_EXCEEDED:
            budget_limit = self.parameters.get("budget_limit")
            total_cost = context.get("total_monthly_cost", 0)
            if budget_limit:
                return total_cost > budget_limit
            return False

        elif self.condition_type == RuleConditionType.SUBSCRIPTION_COUNT:
            category = self.parameters.get("category")
            max_count = self.parameters.get("max_count", 3)
            category_count = context.get(f"category_{category}_count", 0)
            return category_count > max_count

        elif self.condition_type == RuleConditionType.REDUNDANT_FEATURE:
            category = subscription.get("category")
            if not category: return False
            active_in_category = context.get(f"category_{category}_active_count", 0)
            return active_in_category > 1

        elif self.condition_type == RuleConditionType.ANNUAL_POTENTIAL:
            cycle = subscription.get("billing_cycle")
            if cycle != "monthly": return False
            months_active = context.get("months_active", 0)
            threshold = self.parameters.get("months_threshold", 3)
            return months_active >= threshold

        return False


@dataclass
class RuleAction:
    """规则动作"""
    action_type: RuleActionType
    parameters: Dict[str, Any]
    risk_level: str = "low"  # low, medium, high

    def execute(self, subscription: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行动作

        Args:
            subscription: 订阅数据
            context: 执行上下文

        Returns:
            执行结果
        """
        # 实际执行逻辑会在具体的执行器中实现
        # 这里返回动作描述
        return {
            "action": self.action_type.value,
            "subscription_id": subscription.get("id"),
            "service_name": subscription.get("service_name"),
            "parameters": self.parameters,
            "risk_level": self.risk_level,
            "executed_at": datetime.now().isoformat()
        }


@dataclass
class AutomationRule:
    """自动化规则"""
    rule_id: str
    name: str
    description: str
    enabled: bool
    conditions: List[RuleCondition]
    actions: List[RuleAction]
    execution_mode: RuleExecutionMode
    priority: int = 0  # 优先级，数字越小优先级越高

    def evaluate(self, subscription: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        评估规则是否应触发

        Args:
            subscription: 订阅数据
            context: 上下文数据

        Returns:
            是否应触发规则
        """
        if not self.enabled:
            return False

        # 所有条件都必须满足（AND逻辑）
        return all(condition.evaluate(subscription, context) for condition in self.conditions)


class RulesEngine:
    """规则引擎 - 管理和执行自动化规则"""

    def __init__(self):
        self.logger = logging.getLogger("rules_engine")
        self.rules: Dict[str, AutomationRule] = {}
        self._load_default_rules()

    def _load_default_rules(self):
        """加载默认规则"""

        # 规则1: 续费提醒
        self.add_rule(AutomationRule(
            rule_id="renewal_reminder",
            name="续费提醒",
            description="订阅即将续费时通知用户",
            enabled=True,
            conditions=[
                RuleCondition(
                    RuleConditionType.RENEWAL_DUE,
                    {"days": 7}
                )
            ],
            actions=[
                RuleAction(
                    RuleActionType.NOTIFY_USER,
                    {"message": "订阅即将在{days}天后续费"},
                    risk_level="low"
                )
            ],
            execution_mode=RuleExecutionMode.FULL_AUTO,
            priority=1
        ))

        # 规则2: 未使用订阅暂停
        self.add_rule(AutomationRule(
            rule_id="pause_unused",
            name="暂停未使用订阅",
            description="30天未使用的订阅建议暂停",
            enabled=True,
            conditions=[
                RuleCondition(
                    RuleConditionType.UNUSED_PERIOD,
                    {"days": 30}
                )
            ],
            actions=[
                RuleAction(
                    RuleActionType.PAUSE_SUBSCRIPTION,
                    {"reason": "长期未使用"},
                    risk_level="medium"
                )
            ],
            execution_mode=RuleExecutionMode.SEMI_AUTO,
            priority=2
        ))

        # 规则3: 价格上涨通知
        self.add_rule(AutomationRule(
            rule_id="price_increase_alert",
            name="价格上涨警报",
            description="订阅价格上涨超过5%时通知",
            enabled=True,
            conditions=[
                RuleCondition(
                    RuleConditionType.PRICE_CHANGE,
                    {"threshold": 0.05}
                )
            ],
            actions=[
                RuleAction(
                    RuleActionType.NOTIFY_USER,
                    {"message": "订阅价格上涨超过5%"},
                    risk_level="low"
                ),
                RuleAction(
                    RuleActionType.SUGGEST_ALTERNATIVE,
                    {},
                    risk_level="low"
                )
            ],
            execution_mode=RuleExecutionMode.FULL_AUTO,
            priority=1
        ))

        # 规则4: 预算超支警告
        self.add_rule(AutomationRule(
            rule_id="budget_warning",
            name="预算超支警告",
            description="月度订阅支出超过预算时警告",
            enabled=True,
            conditions=[
                RuleCondition(
                    RuleConditionType.BUDGET_EXCEEDED,
                    {}
                )
            ],
            actions=[
                RuleAction(
                    RuleActionType.NOTIFY_USER,
                    {"message": "订阅支出超过预算限制"},
                    risk_level="high"
                )
            ],
            execution_mode=RuleExecutionMode.FULL_AUTO,
            priority=0
        ))

        # 规则5: 分类冗余提醒
        self.add_rule(AutomationRule(
            rule_id="redundant_category_alert",
            name="同类订阅过多提醒",
            description="当同一分类下有多个活跃订阅时提醒",
            enabled=True,
            conditions=[
                RuleCondition(RuleConditionType.REDUNDANT_FEATURE, {})
            ],
            actions=[
                RuleAction(
                    RuleActionType.NOTIFY_USER,
                    {"message": "检测到该分类下有多个订阅，建议整合"},
                    risk_level="low"
                )
            ],
            execution_mode=RuleExecutionMode.FULL_AUTO,
            priority=2
        ))

        # 规则6: 转年付建议
        self.add_rule(AutomationRule(
            rule_id="annual_savings_suggestion",
            name="转年付省钱建议",
            description="月付订阅使用超过3个月时，建议转为年付",
            enabled=True,
            conditions=[
                RuleCondition(RuleConditionType.ANNUAL_POTENTIAL, {"months_threshold": 3})
            ],
            actions=[
                RuleAction(
                    RuleActionType.NOTIFY_USER,
                    {"message": "该订阅已稳定使用，转为年付平均可省10%-20%"},
                    risk_level="low"
                )
            ],
            execution_mode=RuleExecutionMode.FULL_AUTO,
            priority=3
        ))

    def add_rule(self, rule: AutomationRule):
        """添加规则"""
        self.rules[rule.rule_id] = rule
        self.logger.info(f"Added rule: {rule.name} ({rule.rule_id})")

    def remove_rule(self, rule_id: str) -> bool:
        """删除规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            self.logger.info(f"Removed rule: {rule_id}")
            return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        """启用规则"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            self.logger.info(f"Enabled rule: {rule_id}")
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """禁用规则"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            self.logger.info(f"Disabled rule: {rule_id}")
            return True
        return False

    def evaluate_subscription(self, subscription: Dict[str, Any],
                             context: Dict[str, Any]) -> List[AutomationRule]:
        """
        评估订阅，返回应触发的规则

        Args:
            subscription: 订阅数据
            context: 上下文数据

        Returns:
            应触发的规则列表
        """
        triggered_rules = []

        for rule in sorted(self.rules.values(), key=lambda r: r.priority):
            if rule.evaluate(subscription, context):
                triggered_rules.append(rule)
                self.logger.info(
                    f"Rule triggered: {rule.name} for subscription {subscription.get('service_name')}"
                )

        return triggered_rules

    def execute_rules(self, triggered_rules: List[AutomationRule],
                     subscription: Dict[str, Any],
                     context: Dict[str, Any],
                     user_automation_level: str = "manual") -> List[Dict[str, Any]]:
        """
        执行触发的规则

        Args:
            triggered_rules: 触发的规则列表
            subscription: 订阅数据
            context: 执行上下文
            user_automation_level: 用户自动化级别

        Returns:
            执行结果列表
        """
        results = []

        for rule in triggered_rules:
            # 检查是否应执行
            should_execute = self._should_execute_rule(rule, user_automation_level)

            if not should_execute:
                results.append({
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "status": "pending_approval",
                    "message": "需要用户确认"
                })
                continue

            # 执行规则动作
            for action in rule.actions:
                try:
                    result = action.execute(subscription, context)
                    result["rule_id"] = rule.rule_id
                    result["rule_name"] = rule.name
                    result["status"] = "executed"
                    results.append(result)

                    # 记录到活动日志
                    self._log_rule_execution(rule, action, subscription, "success")

                    self.logger.info(
                        f"Executed action {action.action_type.value} for rule {rule.name}"
                    )
                except Exception as e:
                    self.logger.error(f"Action execution failed: {e}")
                    # 记录失败日志
                    self._log_rule_execution(rule, action, subscription, "failed", str(e))
                    results.append({
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "action": action.action_type.value,
                        "status": "error",
                        "error": str(e)
                    })

        return results

    def _should_execute_rule(self, rule: AutomationRule, user_automation_level: str) -> bool:
        """
        判断是否应执行规则

        Args:
            rule: 规则
            user_automation_level: 用户自动化级别

        Returns:
            是否应执行
        """
        # Manual模式：不自动执行任何规则
        if user_automation_level == "manual":
            return False

        # Semi-Auto模式：只执行低风险动作
        if user_automation_level == "semi_auto":
            if rule.execution_mode == RuleExecutionMode.FULL_AUTO:
                # 检查所有动作是否都是低风险
                return all(action.risk_level == "low" for action in rule.actions)
            return False

        # Full-Auto模式：执行所有规则
        if user_automation_level == "full_auto":
            return rule.execution_mode in [
                RuleExecutionMode.SEMI_AUTO,
                RuleExecutionMode.FULL_AUTO
            ]

        return False

    def get_all_rules(self) -> List[AutomationRule]:
        """获取所有规则"""
        return list(self.rules.values())

    def get_rule(self, rule_id: str) -> Optional[AutomationRule]:
        """获取指定规则"""
        return self.rules.get(rule_id)

    def update_rule(self, rule_id: str, **kwargs) -> bool:
        """
        更新规则参数

        Args:
            rule_id: 规则ID
            **kwargs: 要更新的字段

        Returns:
            是否成功
        """
        if rule_id not in self.rules:
            return False

        rule = self.rules[rule_id]

        # 更新允许的字段
        updatable_fields = ["name", "description", "enabled", "priority", "execution_mode"]
        for field, value in kwargs.items():
            if field in updatable_fields and hasattr(rule, field):
                setattr(rule, field, value)

        self.logger.info(f"Updated rule: {rule_id}")
        return True

    def _log_rule_execution(self, rule: AutomationRule, action: RuleAction, 
                           subscription: Dict[str, Any], status: str, error: str = None):
        """记录规则执行到 activity_logger"""
        try:
            from .activity_logger import activity_logger, ActivityType
            
            details = {
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "action_type": action.action_type.value,
                "service_name": subscription.get("service_name"),
                "risk_level": action.risk_level
            }
            if error: details["error"] = error

            activity_logger.log_activity(
                agent_id="rules_engine",
                agent_type="system",
                activity_type=ActivityType.ACTION_TAKEN if status == "success" else ActivityType.ERROR_OCCURRED,
                description=f"执行规则: {rule.name} -> {action.action_type.value}",
                details=details,
                related_subscription_id=subscription.get("id"),
                status=status
            )
        except Exception as e:
            self.logger.error(f"Failed to log rule execution: {e}")


# 全局规则引擎实例
rules_engine = RulesEngine()
