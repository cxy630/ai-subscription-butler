"""
NegotiationAgent - 谈判助手 Agent
负责生成订阅续费谈判策略和起草联系消息
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentType, AgentMessage, AgentContext, MessageType
from core.ai.gemini_client import get_gemini_client

class NegotiationAgent(BaseAgent):
    """谈判助手 - 帮助用户通过谈判节省开支"""

    def __init__(self, agent_id: str = "negotiation_agent"):
        super().__init__(agent_id, AgentType.NEGOTIATION)
        self.gemini_client = get_gemini_client()

    async def process_message(self, message: AgentMessage, context: AgentContext) -> Optional[AgentMessage]:
        """处理接收到的消息"""
        if message.message_type == MessageType.TASK:
            task = message.content.get("task")
            result = await self.execute_task(task, context)
            return self.send_message(
                to_agent=message.from_agent,
                message_type=MessageType.RESULT,
                content=result
            )
        return None

    async def execute_task(self, task: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """执行谈判相关任务"""
        self._current_user_id = context.user_id
        task_type = task.get("type")

        if task_type == "generate_strategy":
            subscription_id = task.get("subscription_id")
            return await self.generate_negotiation_strategy(subscription_id, context)
        
        elif task_type == "draft_message":
            strategy = task.get("strategy")
            return await self.draft_contact_message(strategy, context)
            
        else:
            return {"status": "error", "message": f"未知的任务类型: {task_type}"}

    async def generate_negotiation_strategy(self, subscription_id: str, context: AgentContext) -> Dict[str, Any]:
        """
        为特定订阅生成谈判策略
        """
        # 获取订阅详情
        subscription = next((s for s in context.subscriptions if s["id"] == subscription_id), None)
        if not subscription:
            return {"status": "error", "message": "未找到指定的订阅项目"}

        service_name = subscription.get("service_name")
        price = subscription.get("price")
        currency = subscription.get("currency", "CNY")
        
        self.log_action("generate_strategy_start", {"service": service_name, "subscription_id": subscription_id})

        prompt = f"""你是一名专业的消费谈判专家。请为用户的以下订阅生成谈判策略：

服务名称：{service_name}
当前价格：{price} {currency}
用户背景：这是他们管理下的一个活跃订阅。用户希望降低支出或获得更多优惠。

请提供一个结构化的谈判策略，包含以下内容（仅返回文字内容，不要带 Markdown 或 JSON 标签）：
1. 筹码分析（为什么服务商应该给你优惠）
2. 谈判要点（具体说什么）
3. 目标折扣（建议争取的价格范围）
4. 备选方案（如果谈判失败怎么办）
"""

        try:
            ai_result = self.gemini_client.get_ai_response_sync(prompt)
            response_text = ai_result.get("response", "无法生成策略")

            self.log_action("generate_strategy_complete", {"service": service_name})
            
            return {
                "status": "success",
                "service_name": service_name,
                "subscription_id": subscription_id,
                "strategy_text": response_text,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"生成谈判策略失败: {e}")
            return {"status": "error", "message": str(e)}

    async def draft_contact_message(self, strategy: str, context: AgentContext) -> Dict[str, Any]:
        """
        基于策略起草联系消息
        """
        self.log_action("draft_message_start", {"strategy_preview": strategy[:50]})

        prompt = f"""请基于以下谈判策略，起草一封诚恳且具有说服力的电子邮件或客服聊天消息。

谈判策略概要：
{strategy}

请提供两个版本的初稿：
1. 礼貌且含蓄版（适合社交媒体私信或邮件）
2. 直接且果断版（适合实时在线客服聊天）

仅返回消息正文，不要带 Markdown 或 JSON 标签。"""

        try:
            ai_result = self.gemini_client.get_ai_response_sync(prompt)
            response_text = ai_result.get("response", "无法起草消息")

            self.log_action("draft_message_complete", {"success": True})

            return {
                "status": "success",
                "draft_text": response_text,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"起草谈判消息失败: {e}")
            return {"status": "error", "message": str(e)}
