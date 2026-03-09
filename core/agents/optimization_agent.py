"""
OptimizationAgent - 订阅优化Agent
负责成本分析、订阅组合优化、替代方案推荐
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from .base_agent import BaseAgent, AgentType, AgentMessage, AgentContext, MessageType
import statistics


class OptimizationAgent(BaseAgent):
    """优化Agent - 分析和优化订阅组合"""

    def __init__(self, agent_id: str = "optimization_agent"):
        super().__init__(agent_id, AgentType.OPTIMIZATION)

    async def process_message(self, message: AgentMessage, context: AgentContext) -> Optional[AgentMessage]:
        """处理接收到的消息"""
        if message.message_type == MessageType.COMMAND:
            command = message.content.get("command")

            if command == "analyze_costs":
                result = await self.analyze_costs(context)
                return self.send_message(
                    to_agent=message.from_agent,
                    message_type=MessageType.RESULT,
                    content=result
                )

            elif command == "find_savings":
                result = await self.find_savings_opportunities(context)
                return self.send_message(
                    to_agent=message.from_agent,
                    message_type=MessageType.RESULT,
                    content=result
                )

            elif command == "optimize_portfolio":
                result = await self.optimize_subscription_portfolio(context)
                return self.send_message(
                    to_agent=message.from_agent,
                    message_type=MessageType.RESULT,
                    content=result
                )

        return None

    async def execute_task(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """执行优化任务"""
        task_type = task.get("type")

        if task_type == "cost_analysis":
            return await self.analyze_costs(context)
        elif task_type == "find_savings":
            return await self.find_savings_opportunities(context)
        elif task_type == "optimize_portfolio":
            return await self.optimize_subscription_portfolio(context)
        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}

    async def analyze_costs(self, context: AgentContext) -> Dict[str, Any]:
        """
        深度成本分析

        Returns:
            成本分析报告
        """
        subscriptions = context.subscriptions
        if not subscriptions:
            return {
                "status": "success",
                "message": "No subscriptions to analyze",
                "total_cost": 0
            }

        # 计算总成本（统一为月度）
        monthly_costs = self._calculate_monthly_costs(subscriptions)
        total_monthly = sum(monthly_costs.values())

        # 按分类分析
        category_analysis = self._analyze_by_category(subscriptions)

        # 按周期分析
        cycle_analysis = self._analyze_by_billing_cycle(subscriptions)

        # 成本趋势（如果有历史数据）
        cost_trend = self._analyze_cost_trend(subscriptions)

        # 识别高成本订阅
        top_expenses = sorted(
            subscriptions,
            key=lambda s: self._to_monthly_cost(s.get("price", 0), s.get("billing_cycle", "monthly")),
            reverse=True
        )[:5]

        self.log_action("cost_analysis", {
            "total_subscriptions": len(subscriptions),
            "total_monthly_cost": total_monthly,
            "categories": len(category_analysis)
        })

        return {
            "status": "success",
            "analysis_date": datetime.now().isoformat(),
            "total_monthly_cost": monthly_costs,
            "total_monthly_cny": total_monthly,
            "subscription_count": len(subscriptions),
            "average_cost_per_subscription": total_monthly / len(subscriptions) if subscriptions else 0,
            "category_analysis": category_analysis,
            "cycle_analysis": cycle_analysis,
            "cost_trend": cost_trend,
            "top_5_expenses": [
                {
                    "service_name": sub.get("service_name"),
                    "monthly_cost": self._to_monthly_cost(sub.get("price", 0), sub.get("billing_cycle", "monthly")),
                    "currency": sub.get("currency"),
                    "percentage_of_total": (self._to_monthly_cost(sub.get("price", 0), sub.get("billing_cycle", "monthly")) / total_monthly * 100) if total_monthly > 0 else 0
                }
                for sub in top_expenses
            ]
        }

    async def find_savings_opportunities(self, context: AgentContext) -> Dict[str, Any]:
        """
        寻找节省机会

        Returns:
            节省机会列表
        """
        subscriptions = context.subscriptions
        opportunities = []

        # 1. 识别重复/重叠服务
        duplicates = self._find_duplicate_services(subscriptions)
        for dup in duplicates:
            opportunities.append({
                "type": "duplicate_service",
                "severity": "high",
                "savings_potential": dup["potential_savings"],
                "description": f"发现{len(dup['services'])}个相似服务: {', '.join(dup['services'])}",
                "recommendation": f"考虑只保留一个，每月可节省约¥{dup['potential_savings']:.2f}",
                "services": dup["services"],
                "subscription_id": dup.get("subscription_id")  # 对于重复项，展示主服务的谈判入口
            })

        # 2. 未使用订阅（需要使用数据，当前使用启发式方法）
        unused = self._identify_potentially_unused(subscriptions)
        for sub in unused:
            monthly_cost = self._to_monthly_cost(sub.get("price", 0), sub.get("billing_cycle", "monthly"))
            opportunities.append({
                "type": "unused_subscription",
                "severity": "medium",
                "savings_potential": monthly_cost,
                "description": f"{sub.get('service_name')} 可能未充分使用",
                "recommendation": f"考虑取消或降级，每月可节省约¥{monthly_cost:.2f}",
                "service": sub.get("service_name"),
                "subscription_id": sub.get("id")
            })

        # 3. 年付机会（月付改年付通常有折扣）
        annual_opportunities = self._find_annual_savings_opportunities(subscriptions)
        for opp in annual_opportunities:
            opportunities.append({
                "type": "annual_billing_discount",
                "severity": "low",
                "savings_potential": opp["estimated_annual_savings"],
                "description": f"{opp['service_name']} 改为年付可能更划算",
                "recommendation": f"改为年付预计每年可节省约¥{opp['estimated_annual_savings']:.2f}（按15%折扣估算）",
                "service": opp["service_name"],
                "subscription_id": opp.get("subscription_id")
            })

        # 4. 预算超支识别
        if context.budget_limit:
            total_monthly = sum(self._calculate_monthly_costs(subscriptions).values())
            if total_monthly > context.budget_limit:
                overspend = total_monthly - context.budget_limit
                opportunities.append({
                    "type": "budget_exceeded",
                    "severity": "high",
                    "savings_potential": overspend,
                    "description": f"月度支出¥{total_monthly:.2f}超过预算¥{context.budget_limit:.2f}",
                    "recommendation": f"需要削减约¥{overspend:.2f}的订阅支出",
                    "amount": overspend
                })

        # 按节省潜力排序
        opportunities.sort(key=lambda x: x.get("savings_potential", 0), reverse=True)

        total_savings_potential = sum(o.get("savings_potential", 0) for o in opportunities)

        self.log_action("find_savings_opportunities", {
            "opportunities_found": len(opportunities),
            "total_savings_potential": total_savings_potential
        })

        return {
            "status": "success",
            "analysis_date": datetime.now().isoformat(),
            "opportunities": opportunities,
            "total_savings_potential": total_savings_potential,
            "opportunities_count": len(opportunities)
        }

    async def optimize_subscription_portfolio(self, context: AgentContext) -> Dict[str, Any]:
        """
        优化订阅组合

        Returns:
            优化建议
        """
        subscriptions = context.subscriptions
        recommendations = []

        # 1. 组合分析
        portfolio_health = self._analyze_portfolio_health(subscriptions, context)

        # 2. 预算优化
        if context.budget_limit:
            budget_optimization = self._optimize_for_budget(subscriptions, context.budget_limit)
            recommendations.extend(budget_optimization)

        # 3. 价值优化（成本效益分析）
        value_optimization = self._optimize_for_value(subscriptions)
        recommendations.extend(value_optimization)

        # 4. 多样性建议
        diversity_suggestions = self._suggest_portfolio_diversity(subscriptions)
        recommendations.extend(diversity_suggestions)

        self.log_action("optimize_portfolio", {
            "recommendations_count": len(recommendations),
            "portfolio_health_score": portfolio_health.get("overall_score", 0)
        })

        return {
            "status": "success",
            "analysis_date": datetime.now().isoformat(),
            "portfolio_health": portfolio_health,
            "recommendations": recommendations,
            "optimization_summary": self._generate_optimization_summary(
                portfolio_health, recommendations
            )
        }

    # Private helper methods

    def _calculate_monthly_costs(self, subscriptions: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算月度成本（按货币分组）"""
        monthly_costs = {}

        for sub in subscriptions:
            if sub.get("status") != "active":
                continue

            currency = sub.get("currency", "CNY")
            price = sub.get("price", 0)
            monthly_cost = self._to_monthly_cost(price, sub.get("billing_cycle", "monthly"))

            if currency not in monthly_costs:
                monthly_costs[currency] = 0
            monthly_costs[currency] += monthly_cost

        return monthly_costs

    def _to_monthly_cost(self, price: float, billing_cycle: str) -> float:
        """转换为月度成本"""
        if billing_cycle == "yearly":
            return price / 12
        elif billing_cycle == "weekly":
            return price * 4
        elif billing_cycle == "daily":
            return price * 30
        else:  # monthly
            return price

    def _analyze_by_category(self, subscriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """按分类分析"""
        category_data = {}

        for sub in subscriptions:
            if sub.get("status") != "active":
                continue

            category = sub.get("category", "other")
            monthly_cost = self._to_monthly_cost(sub.get("price", 0), sub.get("billing_cycle", "monthly"))

            if category not in category_data:
                category_data[category] = {
                    "count": 0,
                    "total_cost": 0,
                    "subscriptions": []
                }

            category_data[category]["count"] += 1
            category_data[category]["total_cost"] += monthly_cost
            category_data[category]["subscriptions"].append(sub.get("service_name"))

        return category_data

    def _analyze_by_billing_cycle(self, subscriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """按付费周期分析"""
        cycle_data = {}

        for sub in subscriptions:
            if sub.get("status") != "active":
                continue

            cycle = sub.get("billing_cycle", "monthly")
            if cycle not in cycle_data:
                cycle_data[cycle] = {"count": 0, "total_cost": 0}

            cycle_data[cycle]["count"] += 1
            cycle_data[cycle]["total_cost"] += sub.get("price", 0)

        return cycle_data

    def _analyze_cost_trend(self, subscriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析成本趋势（占位符，需要历史数据）"""
        return {
            "status": "insufficient_data",
            "message": "需要历史成本数据来分析趋势"
        }

    def _find_duplicate_services(self, subscriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """查找重复服务"""
        duplicates = []

        # 按分类分组
        by_category = {}
        for sub in subscriptions:
            if sub.get("status") != "active":
                continue
            category = sub.get("category", "other")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(sub)

        # 识别同类中的多个订阅
        for category, subs in by_category.items():
            if len(subs) > 1:  # 同类超过1个即可视为有重复倾向
                services = [s.get("service_name") for s in subs]
                total_cost = sum(
                    self._to_monthly_cost(s.get("price", 0), s.get("billing_cycle", "monthly"))
                    for s in subs
                )
                # 假设可以削减最便宜的一个
                min_cost = min(
                    self._to_monthly_cost(s.get("price", 0), s.get("billing_cycle", "monthly"))
                    for s in subs
                )

                duplicates.append({
                    "category": category,
                    "services": services,
                    "total_cost": total_cost,
                    "potential_savings": min_cost,
                    "subscription_id": subs[0].get("id")  # 取第一个作为代表
                })

        return duplicates

    def _identify_potentially_unused(self, subscriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别可能未使用的订阅（启发式）"""
        # 占位符 - 实际需要使用数据
        # 这里使用简单启发式：价格低但分类重复
        return []

    def _find_annual_savings_opportunities(self, subscriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """查找年付节省机会"""
        opportunities = []

        for sub in subscriptions:
            if sub.get("billing_cycle") == "monthly" and sub.get("status") == "active":
                monthly_price = sub.get("price", 0)
                annual_cost = monthly_price * 12
                # 假设年付有15%折扣
                estimated_annual_price = annual_cost * 0.85
                estimated_savings = annual_cost - estimated_annual_price

                if estimated_savings > 0:
                    opportunities.append({
                        "service_name": sub.get("service_name"),
                        "current_annual_cost": annual_cost,
                        "estimated_annual_price": estimated_annual_price,
                        "estimated_annual_savings": estimated_savings,
                        "subscription_id": sub.get("id")
                    })

        return opportunities

    def _analyze_portfolio_health(self, subscriptions: List[Dict[str, Any]],
                                  context: AgentContext) -> Dict[str, Any]:
        """分析投资组合健康度"""
        if not subscriptions:
            return {"overall_score": 0, "status": "empty"}

        scores = {}

        # 1. 预算健康度
        if context.budget_limit:
            total_cost = sum(self._calculate_monthly_costs(subscriptions).values())
            budget_ratio = total_cost / context.budget_limit
            scores["budget_health"] = max(0, 100 - (budget_ratio - 1) * 50) if budget_ratio > 1 else 100
        else:
            scores["budget_health"] = None

        # 2. 多样性得分
        categories = set(s.get("category") for s in subscriptions if s.get("status") == "active")
        scores["diversity_score"] = min(100, len(categories) * 20)

        # 3. 成本效率得分（基于是否有明显的高成本项）
        monthly_costs = [
            self._to_monthly_cost(s.get("price", 0), s.get("billing_cycle", "monthly"))
            for s in subscriptions if s.get("status") == "active"
        ]
        if monthly_costs:
            avg_cost = statistics.mean(monthly_costs)
            high_cost_count = sum(1 for c in monthly_costs if c > avg_cost * 2)
            scores["cost_efficiency"] = max(0, 100 - high_cost_count * 15)
        else:
            scores["cost_efficiency"] = 100

        # 计算总分
        valid_scores = [s for s in scores.values() if s is not None]
        overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0

        return {
            "overall_score": overall_score,
            "scores": scores,
            "status": "healthy" if overall_score >= 70 else "needs_attention"
        }

    def _optimize_for_budget(self, subscriptions: List[Dict[str, Any]],
                            budget_limit: float) -> List[Dict[str, Any]]:
        """预算优化"""
        recommendations = []
        total_cost = sum(self._calculate_monthly_costs(subscriptions).values())

        if total_cost > budget_limit:
            overspend = total_cost - budget_limit
            recommendations.append({
                "type": "budget_cut",
                "priority": "high",
                "description": f"需要削减¥{overspend:.2f}的月度支出",
                "action": "review_low_value_subscriptions"
            })

        return recommendations

    def _optimize_for_value(self, subscriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """价值优化"""
        recommendations = []

        # 识别高成本订阅
        sorted_subs = sorted(
            [s for s in subscriptions if s.get("status") == "active"],
            key=lambda s: self._to_monthly_cost(s.get("price", 0), s.get("billing_cycle", "monthly")),
            reverse=True
        )

        for sub in sorted_subs[:3]:  # 前3个最贵的
            monthly_cost = self._to_monthly_cost(sub.get("price", 0), sub.get("billing_cycle", "monthly"))
            recommendations.append({
                "type": "high_cost_review",
                "priority": "medium",
                "description": f"{sub.get('service_name')} 月度成本¥{monthly_cost:.2f}较高",
                "action": "review_usage_and_alternatives"
            })

        return recommendations

    def _suggest_portfolio_diversity(self, subscriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """建议组合多样性"""
        recommendations = []

        # 检查分类集中度
        category_counts = {}
        for sub in subscriptions:
            if sub.get("status") == "active":
                category = sub.get("category", "other")
                category_counts[category] = category_counts.get(category, 0) + 1

        # 分类显示名称映射
        category_display = {
            "entertainment": "娱乐",
            "productivity": "生产力",
            "storage": "存储",
            "education": "教育",
            "health_fitness": "健康",
            "business": "商务",
            "other": "其他"
        }

        for category, count in category_counts.items():
            if count > 4:
                category_name = category_display.get(category, category)
                recommendations.append({
                    "type": "category_concentration",
                    "priority": "low",
                    "description": f"{category_name}分类有{count}个订阅，可能过于集中",
                    "action": "consider_consolidation"
                })

        return recommendations

    def _generate_optimization_summary(self, health: Dict[str, Any],
                                      recommendations: List[Dict[str, Any]]) -> str:
        """生成优化摘要"""
        score = health.get("overall_score", 0)

        if score >= 80:
            summary = "订阅组合整体健康，继续保持。"
        elif score >= 60:
            summary = "订阅组合基本健康，但有改进空间。"
        else:
            summary = "订阅组合需要优化，建议采取行动。"

        high_priority = len([r for r in recommendations if r.get("priority") == "high"])
        if high_priority > 0:
            summary += f" 发现{high_priority}个高优先级问题需要处理。"

        return summary
