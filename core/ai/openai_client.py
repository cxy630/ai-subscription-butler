"""
OpenAI API客户端 - 处理与OpenAI服务的交互
"""

from openai import OpenAI, AsyncOpenAI
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
from pathlib import Path
import logging
import re
import html
import time
from collections import defaultdict

class RateLimiter:
    """API请求速率限制器"""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        """
        初始化速率限制器

        Args:
            max_requests: 时间窗口内的最大请求数
            window_seconds: 时间窗口大小（秒）
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)  # user_id -> [timestamp, timestamp, ...]

    def is_allowed(self, user_id: str = "default") -> bool:
        """
        检查是否允许请求

        Args:
            user_id: 用户标识

        Returns:
            bool: 是否允许请求
        """
        current_time = time.time()
        user_requests = self.requests[user_id]

        # 清理过期的请求记录
        cutoff_time = current_time - self.window_seconds
        self.requests[user_id] = [
            timestamp for timestamp in user_requests
            if timestamp > cutoff_time
        ]

        # 检查是否超过限制
        if len(self.requests[user_id]) >= self.max_requests:
            return False

        # 记录当前请求
        self.requests[user_id].append(current_time)
        return True

    def get_reset_time(self, user_id: str = "default") -> float:
        """获取速率限制重置时间"""
        if not self.requests[user_id]:
            return 0.0

        oldest_request = min(self.requests[user_id])
        return max(0.0, oldest_request + self.window_seconds - time.time())

class OpenAIClient:
    """OpenAI API客户端类"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化OpenAI客户端

        Args:
            api_key: OpenAI API密钥，如果为None则从环境变量读取
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到OpenAI API密钥，请设置环境变量OPENAI_API_KEY或传入api_key参数")

        # 初始化新版OpenAI客户端
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

        # 设置日志
        self.logger = logging.getLogger(__name__)

        # 输入验证配置
        self.max_message_length = 2000
        self.max_context_length = 5000

        # 速率限制器 (每分钟最多30个请求)
        self.rate_limiter = RateLimiter(max_requests=30, window_seconds=60)

        # 系统提示词
        self.system_prompt = """你是AI订阅管家的智能助手，专门帮助用户管理订阅服务。

你的能力包括：
1. 分析用户的订阅支出情况
2. 提供个性化的节省建议
3. 回答关于订阅管理的问题
4. 识别重复或不必要的订阅
5. 预测支出趋势

回复要求：
- 使用中文回复
- 语言亲切、专业
- 提供具体的数据分析
- 给出可执行的建议
- 根据用户数据个性化响应

当用户询问时，基于提供的用户数据进行分析和建议。"""

    async def get_ai_response(
        self,
        user_message: str,
        user_context: Dict[str, Any],
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        获取AI助手响应

        Args:
            user_message: 用户输入的消息
            user_context: 用户上下文信息（订阅数据等）
            conversation_history: 对话历史

        Returns:
            包含AI响应和相关信息的字典
        """
        try:
            # 输入验证和清理
            if not self._validate_user_input(user_message):
                return {
                    "response": "抱歉，您的输入包含不当内容或过长，请重新输入。",
                    "intent": "validation_error",
                    "confidence": 0.0,
                    "error": "Input validation failed",
                    "model": "validation",
                    "timestamp": datetime.now().isoformat()
                }

            # 清理用户输入
            user_message = self._sanitize_input(user_message)

            # 检查速率限制
            if not self.rate_limiter.is_allowed():
                reset_time = self.rate_limiter.get_reset_time()
                return {
                    "response": f"请求过于频繁，请等待 {reset_time:.0f} 秒后重试。",
                    "intent": "rate_limit",
                    "confidence": 0.0,
                    "error": "Rate limit exceeded",
                    "model": "rate_limiter",
                    "reset_time": reset_time,
                    "timestamp": datetime.now().isoformat()
                }

            # 构建消息上下文
            context_info = self._build_context_string(user_context)

            # 构建对话消息
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"用户当前数据：\n{context_info}"}
            ]

            # 添加对话历史（最近5轮对话）
            if conversation_history:
                recent_history = conversation_history[-10:]  # 取最近10条消息
                for msg in recent_history:
                    if msg.get("role") in ["user", "assistant"]:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })

            # 添加当前用户消息
            messages.append({"role": "user", "content": user_message})

            # 调用新版OpenAI API
            self.logger.info(f"Sending request to OpenAI with {len(messages)} messages")

            response = await self.async_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )

            # 解析响应
            ai_message = response.choices[0].message.content.strip()

            # 分析响应意图和置信度
            intent = self._analyze_intent(user_message)
            confidence = self._calculate_confidence(response, user_message)

            self.logger.info(f"OpenAI response received, tokens used: {response.usage.total_tokens}")

            return {
                "response": ai_message,
                "intent": intent,
                "confidence": confidence,
                "tokens_used": response.usage.total_tokens,
                "model": "gpt-3.5-turbo",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            # 返回错误信息和降级响应
            fallback_response = self._get_fallback_response(user_message, user_context)
            return {
                "response": fallback_response,
                "intent": "error_fallback",
                "confidence": 0.5,
                "error": str(e),
                "model": "fallback",
                "timestamp": datetime.now().isoformat()
            }

    def get_ai_response_sync(
        self,
        user_message: str,
        user_context: Dict[str, Any],
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        同步版本的AI响应获取
        """
        try:
            # 输入验证和清理
            if not self._validate_user_input(user_message):
                return {
                    "response": "抱歉，您的输入包含不当内容或过长，请重新输入。",
                    "intent": "validation_error",
                    "confidence": 0.0,
                    "error": "Input validation failed",
                    "model": "validation",
                    "timestamp": datetime.now().isoformat()
                }

            # 清理用户输入
            user_message = self._sanitize_input(user_message)

            # 检查速率限制
            if not self.rate_limiter.is_allowed():
                reset_time = self.rate_limiter.get_reset_time()
                return {
                    "response": f"请求过于频繁，请等待 {reset_time:.0f} 秒后重试。",
                    "intent": "rate_limit",
                    "confidence": 0.0,
                    "error": "Rate limit exceeded",
                    "model": "rate_limiter",
                    "reset_time": reset_time,
                    "timestamp": datetime.now().isoformat()
                }

            # 构建消息上下文
            context_info = self._build_context_string(user_context)

            # 构建对话消息
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"用户当前数据：\n{context_info}"}
            ]

            # 添加对话历史
            if conversation_history:
                recent_history = conversation_history[-10:]
                for msg in recent_history:
                    if msg.get("role") in ["user", "assistant"]:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })

            # 添加当前用户消息
            messages.append({"role": "user", "content": user_message})

            # 调用新版OpenAI API (同步版本)
            self.logger.info(f"Sending sync request to OpenAI with {len(messages)} messages")

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )

            # 解析响应
            ai_message = response.choices[0].message.content.strip()

            # 分析响应意图和置信度
            intent = self._analyze_intent(user_message)
            confidence = self._calculate_confidence(response, user_message)

            self.logger.info(f"OpenAI sync response received, tokens used: {response.usage.total_tokens}")

            return {
                "response": ai_message,
                "intent": intent,
                "confidence": confidence,
                "tokens_used": response.usage.total_tokens,
                "model": "gpt-3.5-turbo",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            # 返回降级响应
            fallback_response = self._get_fallback_response(user_message, user_context)
            return {
                "response": fallback_response,
                "intent": "error_fallback",
                "confidence": 0.5,
                "error": str(e),
                "model": "fallback",
                "timestamp": datetime.now().isoformat()
            }

    def _build_context_string(self, user_context: Dict[str, Any]) -> str:
        """构建用户上下文字符串"""
        context_parts = []

        # 基本统计信息
        if "monthly_spending" in user_context:
            context_parts.append(f"月度支出: ¥{user_context['monthly_spending']:.2f}")

        if "subscriptions" in user_context:
            context_parts.append(f"订阅总数: {len(user_context['subscriptions'])}")

        # 订阅详细信息
        if "subscriptions" in user_context and user_context["subscriptions"]:
            context_parts.append("\n订阅列表:")
            for sub in user_context["subscriptions"]:
                service = sub.get("service_name", "未知服务")
                price = sub.get("price", 0)
                category = sub.get("category", "其他")
                status = sub.get("status", "active")
                context_parts.append(f"- {service}: ¥{price}/月 ({category}, {status})")

        # 分类统计
        if "subscription_categories" in user_context:
            context_parts.append("\n分类统计:")
            for category, stats in user_context["subscription_categories"].items():
                context_parts.append(f"- {category}: {stats['count']}个服务, ¥{stats['spending']:.2f}/月")

        return "\n".join(context_parts) if context_parts else "暂无订阅数据"

    def _analyze_intent(self, user_message: str) -> str:
        """分析用户意图"""
        message_lower = user_message.lower()

        # 定义意图关键词
        intent_keywords = {
            "spending_query": ["花费", "支出", "钱", "费用", "成本", "多少"],
            "subscription_count": ["多少", "几个", "数量", "订阅"],
            "cancel_request": ["取消", "停止", "删除", "退订"],
            "optimization_advice": ["节省", "省钱", "优化", "建议", "推荐"],
            "add_subscription": ["添加", "新增", "订阅"],
            "category_analysis": ["分类", "类别", "分析"],
            "trend_analysis": ["趋势", "变化", "预测"],
            "general_help": ["帮助", "怎么", "如何", "什么"]
        }

        # 匹配意图
        for intent, keywords in intent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return "general_query"

    def _calculate_confidence(self, response: Any, user_message: str) -> float:
        """计算响应置信度"""
        base_confidence = 0.8

        # 根据消息长度调整置信度
        message_length = len(user_message)
        if message_length < 10:
            base_confidence -= 0.1
        elif message_length > 50:
            base_confidence += 0.1

        # 根据API响应质量调整
        if hasattr(response, 'choices') and response.choices:
            response_text = response.choices[0].message.content
            if len(response_text) > 100:
                base_confidence += 0.1
            if "¥" in response_text:  # 包含具体数据
                base_confidence += 0.05

        return min(0.95, max(0.5, base_confidence))

    def _get_fallback_response(self, user_message: str, user_context: Dict[str, Any]) -> str:
        """生成降级响应"""
        # 导入现有的模拟响应函数
        try:
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))

            from ui.components.chat import get_ai_response_mock
            return get_ai_response_mock(user_message, user_context)
        except ImportError:
            return "抱歉，AI服务暂时不可用。您可以稍后重试，或者查看数据概览页面了解订阅情况。"

    async def generate_insights(self, user_context: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        生成智能洞察

        Args:
            user_context: 用户上下文数据

        Returns:
            洞察列表
        """
        try:
            context_info = self._build_context_string(user_context)

            prompt = f"""基于以下用户数据，生成3-5个有价值的订阅管理洞察：

{context_info}

请以JSON格式返回洞察，每个洞察包含：
- type: "info", "warning", "success" 中的一个
- icon: 相关的emoji图标
- title: 洞察标题
- content: 详细内容

示例格式：
[
  {{
    "type": "warning",
    "icon": "⚠️",
    "title": "支出较高提醒",
    "content": "您的月度订阅支出较高，建议定期评估各服务的使用频率。"
  }}
]"""

            self.logger.info("Generating insights with OpenAI")

            response = await self.async_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个订阅管理专家，擅长数据分析和个性化建议。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )

            # 尝试解析JSON响应
            insights_text = response.choices[0].message.content.strip()
            if insights_text.startswith("```json"):
                insights_text = insights_text[7:-3].strip()
            elif insights_text.startswith("```"):
                insights_text = insights_text[3:-3].strip()

            insights = json.loads(insights_text)
            return insights if isinstance(insights, list) else [insights]

        except Exception as e:
            # 返回默认洞察
            return self._get_default_insights(user_context)

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

    def _validate_user_input(self, user_message: str) -> bool:
        """
        验证用户输入安全性和有效性

        Args:
            user_message: 用户输入的消息

        Returns:
            bool: 验证是否通过
        """
        # 检查消息长度
        if not user_message or len(user_message.strip()) == 0:
            return False

        if len(user_message) > self.max_message_length:
            self.logger.warning(f"User input too long: {len(user_message)} characters")
            return False

        # 检查恶意模式
        malicious_patterns = [
            r'<script[^>]*>.*?</script>',  # JavaScript
            r'javascript:',
            r'eval\s*\(',
            r'exec\s*\(',
            r'system\s*\(',
            r'__import__\s*\(',
            r'\.\./',  # 路径遍历
            r'SELECT\s+.*FROM',  # SQL注入基础模式
            r'DROP\s+TABLE',
            r'DELETE\s+FROM',
            r'INSERT\s+INTO'
        ]

        for pattern in malicious_patterns:
            if re.search(pattern, user_message, re.IGNORECASE):
                self.logger.warning(f"Malicious pattern detected: {pattern}")
                return False

        # 检查过多的重复字符（可能是攻击）
        if re.search(r'(.)\1{100,}', user_message):
            self.logger.warning("Excessive character repetition detected")
            return False

        return True

    def _sanitize_input(self, user_message: str) -> str:
        """
        清理和标准化用户输入

        Args:
            user_message: 用户输入的消息

        Returns:
            str: 清理后的消息
        """
        # HTML转义
        sanitized = html.escape(user_message)

        # 移除多余的空白字符
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()

        # 限制长度
        if len(sanitized) > self.max_message_length:
            sanitized = sanitized[:self.max_message_length] + "..."

        # 记录清理操作
        if sanitized != user_message:
            self.logger.info("User input sanitized")

        return sanitized

# 创建全局客户端实例
_openai_client = None

def get_openai_client() -> Optional[OpenAIClient]:
    """获取OpenAI客户端实例"""
    global _openai_client

    if _openai_client is None:
        try:
            _openai_client = OpenAIClient()
        except ValueError:
            # API密钥未配置，返回None
            return None

    return _openai_client

def is_openai_available() -> bool:
    """检查OpenAI API是否可用"""
    return get_openai_client() is not None