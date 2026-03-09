"""
ButlerAgent - 订阅管家中央协调Agent
负责协调各个子Agent，做出决策，与用户交互
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentType, AgentMessage, AgentContext, MessageType
from .monitoring_agent import MonitoringAgent
from .optimization_agent import OptimizationAgent
from .negotiation_agent import NegotiationAgent
from .activity_logger import activity_logger, ActivityType
from core.ai.gemini_client import get_gemini_client
from core.services.price_monitor import price_monitor


class ButlerAgent(BaseAgent):
    """管家Agent - 中央协调者和决策者"""

    def __init__(self, agent_id: str = "butler_agent"):
        super().__init__(agent_id, AgentType.BUTLER)

        # 初始化子Agent
        self.monitoring_agent = MonitoringAgent()
        self.optimization_agent = OptimizationAgent()
        self.negotiation_agent = NegotiationAgent()

        # AI能力
        self.gemini_client = get_gemini_client()

        # Agent注册表
        self.agents = {
            "butler": self,
            "monitoring": self.monitoring_agent,
            "optimization": self.optimization_agent,
            "negotiation": self.negotiation_agent
        }

    async def process_message(self, message: AgentMessage, context: AgentContext) -> Optional[AgentMessage]:
        """处理接收到的消息"""
        if message.message_type == MessageType.QUERY:
            query = message.content.get("query")
            return await self._handle_user_query(query, context, message.from_agent)

        elif message.message_type == MessageType.TASK:
            task = message.content.get("task")
            return await self._handle_task_request(task, context, message.from_agent)

        elif message.message_type == MessageType.RESULT:
            # 处理子Agent返回的结果
            return await self._process_agent_result(message, context)

        return None

    async def execute_task(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """执行管家任务"""
        # 设置当前用户ID用于活动日志记录
        self._current_user_id = context.user_id
        self.monitoring_agent._current_user_id = context.user_id
        self.optimization_agent._current_user_id = context.user_id
        self.negotiation_agent._current_user_id = context.user_id

        task_type = task.get("type")

        if task_type == "daily_checkup":
            return await self.perform_daily_checkup(context)

        elif task_type == "analyze_subscriptions":
            return await self.analyze_subscriptions(context)

        elif task_type == "generate_insights":
            return await self.generate_insights(context)

        elif task_type == "analyze_costs":
            return await self.optimization_agent.analyze_costs(context)

        elif task_type == "find_savings":
            return await self.optimization_agent.find_savings_opportunities(context)

        elif task_type == "optimize_portfolio":
            return await self.optimization_agent.optimize_subscription_portfolio(context)

        elif task_type == "generate_negotiation_strategy":
            return await self.negotiation_agent.generate_negotiation_strategy(
                task.get("subscription_id"), context
            )

        elif task_type == "draft_negotiation_message":
            return await self.negotiation_agent.draft_contact_message(
                task.get("strategy"), context
            )

        elif task_type == "generate_weekly_report":
            return await self.generate_weekly_report(context)

        elif task_type == "generate_monthly_insights":
            return await self.generate_monthly_insights(context)

        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}

    async def perform_daily_checkup(self, context: AgentContext) -> Dict[str, Any]:
        """
        执行每日检查任务

        Returns:
            每日检查报告
        """
        self.log_action("daily_checkup_start", {"user_id": context.user_id})

        # 委托监控Agent扫描订阅
        scan_message = self.send_message(
            to_agent="monitoring",
            message_type=MessageType.COMMAND,
            content={"command": "scan_all"}
        )

        self.monitoring_agent.receive_message(scan_message)
        scan_results = await self.monitoring_agent.process_queue(context)

        if scan_results:
            scan_data = scan_results[0].content
        else:
            scan_data = {"status": "error", "message": "No scan results"}

        # 检查即将续费的订阅
        renewal_message = self.send_message(
            to_agent="monitoring",
            message_type=MessageType.COMMAND,
            content={"command": "check_renewals"}
        )

        self.monitoring_agent.receive_message(renewal_message)
        renewal_results = await self.monitoring_agent.process_queue(context)

        if renewal_results:
            renewal_data = renewal_results[0].content
        else:
            renewal_data = {"status": "error", "message": "No renewal data"}

        # 生成每日摘要
        daily_summary = {
            "status": "success",
            "checkup_date": datetime.now().isoformat(),
            "scan_results": scan_data,
            "upcoming_renewals": renewal_data,
            "action_items": self._generate_action_items(scan_data, renewal_data),
            "total_monthly_cost": self._calculate_total_cost(context.subscriptions)
        }

        self.log_action("daily_checkup_complete", {
            "issues_count": len(scan_data.get("issues", [])),
            "renewals_count": len(renewal_data.get("upcoming_renewals", []))
        })

        return daily_summary

    async def analyze_subscriptions(self, context: AgentContext) -> Dict[str, Any]:
        """
        深度分析订阅组合

        Returns:
            分析报告
        """
        subscriptions = context.subscriptions

        # 分类统计
        category_stats = self._calculate_category_stats(subscriptions)

        # 成本分析
        cost_analysis = self._analyze_costs(subscriptions)

        # 使用AI生成洞察
        ai_insights = await self._generate_ai_insights(subscriptions, context)

        return {
            "status": "success",
            "analysis_date": datetime.now().isoformat(),
            "total_subscriptions": len(subscriptions),
            "active_subscriptions": len([s for s in subscriptions if s.get("status") == "active"]),
            "category_breakdown": category_stats,
            "cost_analysis": cost_analysis,
            "ai_insights": ai_insights
        }

    async def generate_insights(self, context: AgentContext) -> Dict[str, Any]:
        """
        生成个性化洞察和建议

        Returns:
            洞察和建议
        """
        insights = []

        # 成本优化建议
        cost_insights = self._generate_cost_insights(context)
        insights.extend(cost_insights)

        # 订阅优化建议
        optimization_insights = self._generate_optimization_insights(context)
        insights.extend(optimization_insights)

        # 使用AI生成额外洞察
        ai_insights = await self._generate_ai_insights(context.subscriptions, context)
        insights.extend(ai_insights.get("suggestions", []))

        return {
            "status": "success",
            "generated_at": datetime.now().isoformat(),
            "insights": insights,
            "priority_actions": self._prioritize_insights(insights)
        }

    # Private helper methods

    async def _handle_user_query(self, query: str, context: AgentContext,
                                 from_agent: str) -> AgentMessage:
        """处理用户查询"""
        # 使用AI理解用户意图
        prompt = f"""作为订阅管家，用户问: "{query}"

用户当前有 {len(context.subscriptions)} 个订阅。
自动化级别: {context.automation_level}

请分析用户意图并提供简洁的回答。"""

        try:
            ai_result = self.gemini_client.get_ai_response_sync(prompt)
            response_text = ai_result.get("response", "无法生成回复")

            return self.send_message(
                to_agent=from_agent,
                message_type=MessageType.RESULT,
                content={
                    "status": "success",
                    "query": query,
                    "response": response_text
                }
            )
        except Exception as e:
            return self.send_message(
                to_agent=from_agent,
                message_type=MessageType.RESULT,
                content={
                    "status": "error",
                    "query": query,
                    "error": str(e)
                }
            )

    async def _handle_task_request(self, task: Dict[str, Any], context: AgentContext,
                                  from_agent: str) -> AgentMessage:
        """处理任务请求"""
        result = await self.execute_task(task, context)

        return self.send_message(
            to_agent=from_agent,
            message_type=MessageType.RESULT,
            content=result
        )

    async def _process_agent_result(self, message: AgentMessage,
                                   context: AgentContext) -> Optional[AgentMessage]:
        """处理子Agent的结果"""
        # 记录结果
        self.log_action("agent_result_received", {
            "from_agent": message.from_agent,
            "result_status": message.content.get("status")
        })

        # Butler Agent可以在这里决定是否需要进一步行动
        # 当前版本简单记录，未来可以添加更复杂的决策逻辑

        return None

    def _generate_action_items(self, scan_data: Dict[str, Any],
                              renewal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成行动项"""
        action_items = []

        # 从扫描结果生成行动项
        for issue in scan_data.get("issues", []):
            if issue.get("severity") == "high":
                action_items.append({
                    "priority": "high",
                    "type": issue.get("type"),
                    "description": issue.get("message"),
                    "subscription_id": issue.get("subscription_id")
                })

        # 从续费数据生成行动项
        for renewal in renewal_data.get("upcoming_renewals", []):
            if renewal.get("days_until_renewal", 999) <= 3:
                action_items.append({
                    "priority": "high",
                    "type": "renewal_urgent",
                    "description": f"Renewal due in {renewal['days_until_renewal']} days",
                    "subscription_id": renewal.get("subscription_id")
                })

        return action_items

    def _calculate_total_cost(self, subscriptions: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算总成本"""
        monthly_costs = {}

        for sub in subscriptions:
            if sub.get("status") != "active":
                continue

            currency = sub.get("currency", "CNY")
            price = sub.get("price", 0)
            cycle = sub.get("billing_cycle", "monthly")

            # 转换为月度成本
            if cycle == "yearly":
                price = price / 12
            elif cycle == "weekly":
                price = price * 4
            elif cycle == "daily":
                price = price * 30

            if currency not in monthly_costs:
                monthly_costs[currency] = 0
            monthly_costs[currency] += price

        return monthly_costs

    async def generate_weekly_report(self, context: AgentContext) -> Dict[str, Any]:
        """生成订阅周报"""
        self.log_action("generate_weekly_report_start", {"user_id": context.user_id})
        
        subscriptions = context.subscriptions
        active_subs = [s for s in subscriptions if s.get("status") == "active"]
        
        # 1. 基础数据统计
        total_monthly = self._calculate_total_cost(active_subs)
        cny_total = total_monthly.get("CNY", 0)
        
        # 2. 真实价格变化监控
        increases = price_monitor.record_prices(context.user_id, active_subs)
        price_changes = []
        for inc in increases:
            price_changes.append(f"{inc['service_name']} (涨价 {inc['increase_amount']:.2f})")

        # 3. AI 生成摘要
        prompt = f"""作为 AI 订阅管家，请根据以下数据生成一份中文周报摘要：
活跃订阅数：{len(active_subs)} 个
月度开支预估：¥{cny_total:.2f}
价格变动：{', '.join(price_changes) if price_changes else '无明显突发涨价'}

请用一小段话（50字左右）总结本周订阅状态并给出一个建议。"""
        
        try:
            ai_result = self.gemini_client.get_ai_response_sync(prompt)
            summary = ai_result.get("response", "本周订阅状态平稳。")
        except:
            summary = "本周订阅状态平稳，支出符合预期。"

        report = {
            "status": "success",
            "report_date": datetime.now().isoformat(),
            "summary": summary,
            "stats": {
                "active_count": len(active_subs),
                "estimated_monthly_cost": cny_total
            }
        }
        
        self.log_action("generate_weekly_report_complete", {"active_count": len(active_subs)})
        return report

    async def generate_monthly_insights(self, context: AgentContext) -> Dict[str, Any]:
        """生成月度优化总结"""
        self.log_action("generate_monthly_insights_start", {"user_id": context.user_id})
        
        # Request optimization agent to find savings
        savings_result = await self.optimization_agent.find_savings_opportunities(context)
        savings_opportunities = savings_result.get("opportunities", [])
        
        # Calculate summary metrics
        total_monthly_cny = sum(
            sub.get("price", 0) for sub in context.subscriptions 
            if sub.get("status") == "active" and sub.get("billing_cycle") == "monthly"
        )
        
        # Draft a monthly review
        prompt = f"""作为 AI 订阅管家，请根据以下数据生成一份中文月度优化建议报告：
月度开支：¥{total_monthly_cny:.2f}
发现的省钱机会数：{len(savings_opportunities)} 个

请用一段话说明本月的消费健康度，并给出一个具体的建议。"""
        
        try:
            ai_result = self.gemini_client.get_ai_response_sync(prompt)
            summary = ai_result.get("response", "本月订阅消费平稳，请继续保持。")
        except:
            summary = "本月订阅状态平稳，建议多关注长期未使用的订阅服务以节约开支。"
            
        report = {
            "status": "success",
            "report_date": datetime.now().isoformat(),
            "summary": summary,
            "savings_opportunities_count": len(savings_opportunities)
        }
        
        self.log_action("generate_monthly_insights_complete", {"insights_count": len(savings_opportunities)})
        return report

    def _calculate_category_stats(self, subscriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算分类统计"""
        stats = {}

        for sub in subscriptions:
            if sub.get("status") != "active":
                continue

            category = sub.get("category", "other")
            if category not in stats:
                stats[category] = {"count": 0, "total_cost": 0}

            stats[category]["count"] += 1
            stats[category]["total_cost"] += sub.get("price", 0)

        return stats

    def _analyze_costs(self, subscriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """成本分析"""
        active_subs = [s for s in subscriptions if s.get("status") == "active"]

        if not active_subs:
            return {"total_monthly": 0, "average_per_subscription": 0}

        monthly_costs = self._calculate_total_cost(active_subs)
        total_monthly_cny = monthly_costs.get("CNY", 0)

        return {
            "total_monthly": monthly_costs,
            "average_per_subscription": total_monthly_cny / len(active_subs) if active_subs else 0,
            "highest_cost": max(active_subs, key=lambda s: s.get("price", 0))["service_name"] if active_subs else None
        }

    async def _generate_ai_insights(self, subscriptions: List[Dict[str, Any]],
                                   context: AgentContext) -> Dict[str, Any]:
        """使用AI生成洞察"""
        # 构建订阅摘要
        summary = f"用户有 {len(subscriptions)} 个订阅:\n"
        for sub in subscriptions[:10]:  # 限制数量避免token过多
            summary += f"- {sub['service_name']}: {sub['currency']} {sub['price']}/{sub['billing_cycle']}\n"

        prompt = f"""作为订阅管家，分析以下订阅情况:

{summary}

用户偏好: {context.user_preferences}
预算限制: {context.budget_limit if context.budget_limit else '无'}

请提供3-5个简洁的优化建议，每个建议单独一行，格式如下：
- 建议1
- 建议2
- 建议3

注意：只返回建议文本，不要包含JSON格式、代码块或其他格式标记。"""

        try:
            ai_result = self.gemini_client.get_ai_response_sync(prompt)
            response_text = ai_result.get("response", "")

            # 调试日志
            self.logger.info(f"AI response_text type: {type(response_text)}")
            self.logger.info(f"AI response_text length: {len(response_text) if response_text else 0}")
            self.logger.info(f"AI response_text first 200 chars: {response_text[:200] if response_text else 'empty'}")

            # 尝试解析JSON格式的响应
            import json
            import re

            # 第一步：尝试直接JSON解析（处理标准JSON响应）
            try:
                parsed = json.loads(response_text.strip())
                if isinstance(parsed, dict) and "suggestions" in parsed:
                    self.logger.info("Successfully parsed JSON directly")
                    return parsed
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.info(f"Direct JSON parse failed: {e}")

            # 第二步：尝试从文本中提取JSON对象
            import re
            json_pattern = r'\{[^{}]*"suggestions"[^{}]*\[[^\]]*\][^{}]*\}'
            json_match = re.search(json_pattern, response_text, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    if isinstance(parsed, dict) and "suggestions" in parsed:
                        return parsed
                except (json.JSONDecodeError, ValueError):
                    pass

            # 第三步：按行提取建议（处理列表格式或混合格式）
            if response_text:
                lines = [line.strip() for line in response_text.split('\n') if line.strip()]
                # 过滤掉代码块标记、JSON标记和"suggestions"关键字行
                suggestions = []
                for line in lines:
                    # 跳过这些行
                    if (line.startswith('```') or
                        line.startswith('{') or
                        line.startswith('}') or
                        line.startswith('"suggestions"') or
                        line == '[' or
                        line == ']' or
                        line.endswith('[') or
                        line.endswith('],')):
                        continue
                    # 清理行首的列表标记和引号
                    cleaned = line.lstrip('- ').lstrip('* ').lstrip('1234567890. ').strip('"').strip(',').strip()
                    if cleaned:
                        suggestions.append(cleaned)

                if suggestions:
                    return {"suggestions": suggestions}

            # 如果以上都失败，返回原文本
            return {"suggestions": [response_text] if response_text else ["AI分析暂时不可用"]}

        except Exception as e:
            self.logger.error(f"AI insights generation failed: {e}")
            return {"suggestions": ["AI分析暂时不可用"]}

    def _generate_cost_insights(self, context: AgentContext) -> List[Dict[str, Any]]:
        """生成成本洞察"""
        insights = []

        total_costs = self._calculate_total_cost(context.subscriptions)
        total_monthly = total_costs.get("CNY", 0) + total_costs.get("USD", 0) * 7  # 简化汇率

        # 预算检查
        if context.budget_limit and total_monthly > context.budget_limit:
            insights.append({
                "type": "cost_warning",
                "severity": "high",
                "message": f"月度支出 {total_monthly:.2f} 超过预算 {context.budget_limit}"
            })

        # 高成本订阅
        expensive_subs = sorted(
            [s for s in context.subscriptions if s.get("status") == "active"],
            key=lambda s: s.get("price", 0),
            reverse=True
        )[:3]

        if expensive_subs:
            insights.append({
                "type": "high_cost_subscriptions",
                "severity": "medium",
                "message": f"最高成本订阅: {', '.join([s['service_name'] for s in expensive_subs])}"
            })

        return insights

    def _generate_optimization_insights(self, context: AgentContext) -> List[Dict[str, Any]]:
        """生成优化洞察"""
        insights = []

        # 重复分类检查
        category_counts = {}
        for sub in context.subscriptions:
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
            if count > 3:
                category_name = category_display.get(category, category)
                insights.append({
                    "type": "category_redundancy",
                    "severity": "medium",
                    "message": f"{category_name}分类有 {count} 个订阅，考虑整合"
                })

        return insights

    def _prioritize_insights(self, insights: List[Any]) -> List[Any]:
        """优先级排序洞察"""
        # 简单按severity排序
        priority_order = {"high": 0, "medium": 1, "low": 2}

        def get_priority(insight):
            if isinstance(insight, dict):
                return priority_order.get(insight.get("severity", "low"), 3)
            return 3

        return sorted(insights, key=get_priority)
