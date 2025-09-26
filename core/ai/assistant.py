"""
AI助手服务 - 提供智能对话和分析功能
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging

from .openai_client import OpenAIClient, get_openai_client, is_openai_available
from .config import get_ai_config, AIConfig

logger = logging.getLogger(__name__)

class AIAssistant:
    """AI助手服务类"""

    def __init__(self, config: Optional[AIConfig] = None):
        """
        初始化AI助手

        Args:
            config: AI配置，如果为None则使用默认配置
        """
        self.config = config or get_ai_config()
        self.openai_client = get_openai_client() if self.config.is_valid() else None
        self.request_count = 0
        self.last_reset_date = datetime.now().date()

        logger.info(f"AI助手初始化完成，OpenAI可用: {self.is_available()}")

    def is_available(self) -> bool:
        """检查AI助手是否可用"""
        return self.openai_client is not None and self._check_rate_limit()

    def _check_rate_limit(self) -> bool:
        """检查速率限制"""
        current_date = datetime.now().date()

        # 如果是新的一天，重置计数器
        if current_date != self.last_reset_date:
            self.request_count = 0
            self.last_reset_date = current_date

        return self.request_count < self.config.max_daily_requests

    def _increment_request_count(self):
        """增加请求计数"""
        self.request_count += 1

    async def chat(
        self,
        user_message: str,
        user_context: Dict[str, Any],
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        与AI助手对话

        Args:
            user_message: 用户消息
            user_context: 用户上下文数据
            conversation_history: 对话历史

        Returns:
            AI响应结果
        """
        if not self.is_available():
            return self._get_unavailable_response(user_message, user_context)

        try:
            self._increment_request_count()

            # 处理对话历史
            if conversation_history and self.config.enable_conversation_memory:
                # 限制历史长度
                conversation_history = conversation_history[-self.config.max_conversation_history:]

            # 调用OpenAI客户端
            response = await self.openai_client.get_ai_response(
                user_message=user_message,
                user_context=user_context,
                conversation_history=conversation_history
            )

            # 记录成功响应
            logger.info(f"AI响应成功，使用tokens: {response.get('tokens_used', 0)}")

            return response

        except Exception as e:
            logger.error(f"AI对话失败: {str(e)}")
            return self._get_error_response(user_message, user_context, str(e))

    def chat_sync(
        self,
        user_message: str,
        user_context: Dict[str, Any],
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """同步版本的对话接口"""
        if not self.is_available():
            return self._get_unavailable_response(user_message, user_context)

        try:
            self._increment_request_count()

            # 处理对话历史
            if conversation_history and self.config.enable_conversation_memory:
                conversation_history = conversation_history[-self.config.max_conversation_history:]

            # 调用OpenAI客户端（同步版本）
            response = self.openai_client.get_ai_response_sync(
                user_message=user_message,
                user_context=user_context,
                conversation_history=conversation_history
            )

            logger.info(f"AI响应成功，使用tokens: {response.get('tokens_used', 0)}")
            return response

        except Exception as e:
            logger.error(f"AI对话失败: {str(e)}")
            return self._get_error_response(user_message, user_context, str(e))

    async def generate_insights(self, user_context: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        生成智能洞察

        Args:
            user_context: 用户上下文数据

        Returns:
            洞察列表
        """
        if not self.is_available() or not self.config.enable_insights_generation:
            return self._get_default_insights(user_context)

        try:
            self._increment_request_count()

            # 调用OpenAI生成洞察
            insights = await self.openai_client.generate_insights(user_context)

            logger.info(f"智能洞察生成成功，共{len(insights)}条")
            return insights

        except Exception as e:
            logger.error(f"智能洞察生成失败: {str(e)}")
            return self._get_default_insights(user_context)

    def _get_unavailable_response(self, user_message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """获取AI不可用时的响应"""
        if not self.config.enable_fallback_responses:
            return {
                "response": "AI服务暂时不可用，请稍后重试。",
                "intent": "service_unavailable",
                "confidence": 0.0,
                "model": "unavailable",
                "timestamp": datetime.now().isoformat()
            }

        # 使用降级响应
        try:
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))

            from ui.components.chat import get_ai_response_mock
            fallback_response = get_ai_response_mock(user_message, user_context)

            return {
                "response": fallback_response,
                "intent": "fallback_response",
                "confidence": 0.6,
                "model": "fallback",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "response": "抱歉，服务暂时不可用。您可以查看数据概览页面了解订阅情况。",
                "intent": "error_fallback",
                "confidence": 0.3,
                "error": str(e),
                "model": "error",
                "timestamp": datetime.now().isoformat()
            }

    def _get_error_response(self, user_message: str, user_context: Dict[str, Any], error: str) -> Dict[str, Any]:
        """获取错误响应"""
        return {
            "response": "抱歉，处理您的请求时出现了问题。请稍后重试。",
            "intent": "error",
            "confidence": 0.0,
            "error": error,
            "model": "error",
            "timestamp": datetime.now().isoformat()
        }

    def _get_default_insights(self, user_context: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成默认洞察"""
        insights = []

        monthly_spending = user_context.get("monthly_spending", 0)
        subscriptions = user_context.get("subscriptions", [])
        categories = user_context.get("subscription_categories", {})

        # 支出分析
        if monthly_spending > 200:
            insights.append({
                "type": "warning",
                "icon": "⚠️",
                "title": "支出较高提醒",
                "content": f"您的月度订阅支出为¥{monthly_spending:.2f}，建议定期评估各服务的使用频率。"
            })

        # 订阅数量分析
        if len(subscriptions) > 5:
            insights.append({
                "type": "info",
                "icon": "📱",
                "title": "订阅数量提醒",
                "content": f"您有{len(subscriptions)}个活跃订阅，可以考虑整合相似功能的服务。"
            })

        # 娱乐支出分析
        entertainment_cost = categories.get("entertainment", {}).get("spending", 0)
        if entertainment_cost > 50:
            insights.append({
                "type": "info",
                "icon": "🎬",
                "title": "娱乐支出分析",
                "content": f"娱乐类支出¥{entertainment_cost:.2f}/月，可以考虑选择性保留最常用的服务。"
            })

        # 如果没有特殊情况，给出积极反馈
        if not insights:
            insights.append({
                "type": "success",
                "icon": "✅",
                "title": "订阅结构良好",
                "content": "您的订阅管理情况很不错，继续保持定期评估的习惯！"
            })

        return insights

    def get_status(self) -> Dict[str, Any]:
        """获取AI助手状态信息"""
        return {
            "available": self.is_available(),
            "openai_configured": self.openai_client is not None,
            "model": self.config.openai_model,
            "daily_requests_used": self.request_count,
            "daily_limit": self.config.max_daily_requests,
            "features": {
                "insights_generation": self.config.enable_insights_generation,
                "conversation_memory": self.config.enable_conversation_memory,
                "fallback_responses": self.config.enable_fallback_responses
            },
            "config": self.config.to_dict()
        }

    def reset_daily_limit(self):
        """重置每日限制（测试用）"""
        self.request_count = 0
        self.last_reset_date = datetime.now().date()

# 全局助手实例
_ai_assistant = None

def get_ai_assistant() -> AIAssistant:
    """获取AI助手实例"""
    global _ai_assistant

    if _ai_assistant is None:
        _ai_assistant = AIAssistant()

    return _ai_assistant

def is_ai_assistant_available() -> bool:
    """检查AI助手是否可用"""
    assistant = get_ai_assistant()
    return assistant.is_available()

async def chat_with_ai(
    user_message: str,
    user_context: Dict[str, Any],
    conversation_history: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """便捷的AI对话接口"""
    assistant = get_ai_assistant()
    return await assistant.chat(user_message, user_context, conversation_history)

def chat_with_ai_sync(
    user_message: str,
    user_context: Dict[str, Any],
    conversation_history: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """便捷的AI对话接口（同步版本）"""
    assistant = get_ai_assistant()
    return assistant.chat_sync(user_message, user_context, conversation_history)

async def generate_ai_insights(user_context: Dict[str, Any]) -> List[Dict[str, str]]:
    """便捷的智能洞察生成接口"""
    assistant = get_ai_assistant()
    return await assistant.generate_insights(user_context)