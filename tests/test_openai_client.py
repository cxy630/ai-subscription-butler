"""
OpenAI客户端单元测试
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.ai.openai_client import OpenAIClient, RateLimiter


class TestRateLimiter(unittest.TestCase):
    """速率限制器测试"""

    def setUp(self):
        """测试设置"""
        self.rate_limiter = RateLimiter(max_requests=3, window_seconds=1)

    def test_rate_limiter_allows_requests_within_limit(self):
        """测试限制范围内的请求被允许"""
        # 前3个请求应该被允许
        for i in range(3):
            self.assertTrue(self.rate_limiter.is_allowed("user1"))

    def test_rate_limiter_blocks_excess_requests(self):
        """测试超出限制的请求被阻止"""
        # 前3个请求被允许
        for i in range(3):
            self.rate_limiter.is_allowed("user1")

        # 第4个请求应该被阻止
        self.assertFalse(self.rate_limiter.is_allowed("user1"))

    def test_rate_limiter_resets_after_window(self):
        """测试时间窗口重置后允许新请求"""
        # 使用很短的时间窗口进行测试
        limiter = RateLimiter(max_requests=1, window_seconds=0.1)

        # 第一个请求被允许
        self.assertTrue(limiter.is_allowed("user1"))

        # 立即的第二个请求被阻止
        self.assertFalse(limiter.is_allowed("user1"))

        # 等待时间窗口过期
        import time
        time.sleep(0.2)

        # 现在应该允许新请求
        self.assertTrue(limiter.is_allowed("user1"))

    def test_rate_limiter_per_user_isolation(self):
        """测试不同用户的限制隔离"""
        # 用户1达到限制
        for i in range(3):
            self.rate_limiter.is_allowed("user1")

        # 用户1被阻止，但用户2仍然被允许
        self.assertFalse(self.rate_limiter.is_allowed("user1"))
        self.assertTrue(self.rate_limiter.is_allowed("user2"))


class TestOpenAIClient(unittest.TestCase):
    """OpenAI客户端测试"""

    def setUp(self):
        """测试设置"""
        self.test_api_key = "test-api-key-for-testing"

        # 模拟环境变量
        self.env_patcher = patch.dict(os.environ, {"OPENAI_API_KEY": self.test_api_key})
        self.env_patcher.start()

    def tearDown(self):
        """测试清理"""
        self.env_patcher.stop()

    @patch('core.ai.openai_client.OpenAI')
    @patch('core.ai.openai_client.AsyncOpenAI')
    def test_client_initialization(self, mock_async_openai, mock_openai):
        """测试客户端初始化"""
        client = OpenAIClient()

        # 验证客户端被正确初始化
        mock_openai.assert_called_once_with(api_key=self.test_api_key)
        mock_async_openai.assert_called_once_with(api_key=self.test_api_key)

        # 验证属性设置
        self.assertEqual(client.api_key, self.test_api_key)
        self.assertIsNotNone(client.rate_limiter)
        self.assertIsNotNone(client.logger)

    def test_client_initialization_without_api_key(self):
        """测试没有API密钥时的初始化失败"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                OpenAIClient()

            self.assertIn("未找到OpenAI API密钥", str(context.exception))

    def test_validate_user_input_valid_message(self):
        """测试有效用户输入验证"""
        with patch('core.ai.openai_client.OpenAI'), \
             patch('core.ai.openai_client.AsyncOpenAI'):
            client = OpenAIClient()

            valid_messages = [
                "hello",
                "what is my subscription spending?",
                "help me analyze entertainment spending",
                "A" * 100  # Length within limit
            ]

            for message in valid_messages:
                self.assertTrue(client._validate_user_input(message), f"Message should be valid: {message}")

    def test_validate_user_input_invalid_message(self):
        """测试无效用户输入验证"""
        with patch('core.ai.openai_client.OpenAI'), \
             patch('core.ai.openai_client.AsyncOpenAI'):
            client = OpenAIClient()

            invalid_messages = [
                "",  # 空消息
                "   ",  # 只有空格
                "A" * 3000,  # 太长
                "<script>alert('xss')</script>",  # XSS攻击
                "SELECT * FROM users",  # SQL注入
                "javascript:alert('test')",  # JavaScript攻击
                "A" * 150,  # 过多重复字符
            ]

            for message in invalid_messages:
                self.assertFalse(client._validate_user_input(message), f"Message should be invalid: {message}")

    def test_sanitize_input(self):
        """测试输入清理"""
        with patch('core.ai.openai_client.OpenAI'), \
             patch('core.ai.openai_client.AsyncOpenAI'):
            client = OpenAIClient()

            test_cases = [
                ("Hello <script>", "Hello &lt;script&gt;"),
                ("  Multiple   spaces  ", "Multiple spaces"),
                ("Normal text", "Normal text"),
                ("A&B", "A&amp;B"),
            ]

            for input_text, expected in test_cases:
                result = client._sanitize_input(input_text)
                self.assertEqual(result, expected)

    @patch('core.ai.openai_client.OpenAI')
    @patch('core.ai.openai_client.AsyncOpenAI')
    def test_get_ai_response_sync_with_validation_failure(self, mock_async_openai, mock_openai):
        """测试输入验证失败时的同步响应"""
        client = OpenAIClient()

        # 测试无效输入
        response = client.get_ai_response_sync(
            user_message="<script>alert('xss')</script>",
            user_context={}
        )

        self.assertEqual(response["intent"], "validation_error")
        self.assertEqual(response["confidence"], 0.0)
        self.assertIn("不当内容", response["response"])

    @patch('core.ai.openai_client.OpenAI')
    @patch('core.ai.openai_client.AsyncOpenAI')
    def test_rate_limiting_in_sync_method(self, mock_async_openai, mock_openai):
        """测试同步方法中的速率限制"""
        client = OpenAIClient()

        # 模拟速率限制器返回False
        with patch.object(client.rate_limiter, 'is_allowed', return_value=False), \
             patch.object(client.rate_limiter, 'get_reset_time', return_value=30.0):

            response = client.get_ai_response_sync(
                user_message="测试消息",
                user_context={}
            )

            self.assertEqual(response["intent"], "rate_limit")
            self.assertIn("请求过于频繁", response["response"])
            self.assertEqual(response["reset_time"], 30.0)

    @patch('core.ai.openai_client.OpenAI')
    @patch('core.ai.openai_client.AsyncOpenAI')
    def test_successful_api_call_sync(self, mock_async_openai, mock_openai):
        """测试成功的API调用（同步）"""
        # 模拟OpenAI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "这是AI的回复"
        mock_response.usage.total_tokens = 100

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance

        client = OpenAIClient()

        response = client.get_ai_response_sync(
            user_message="你好",
            user_context={"monthly_spending": 100, "subscriptions": []}
        )

        # 验证响应
        self.assertEqual(response["response"], "这是AI的回复")
        self.assertEqual(response["tokens_used"], 100)
        self.assertEqual(response["model"], "gpt-3.5-turbo")
        self.assertGreater(response["confidence"], 0)

        # 验证API被正确调用
        mock_client_instance.chat.completions.create.assert_called_once()
        call_args = mock_client_instance.chat.completions.create.call_args
        self.assertEqual(call_args[1]["model"], "gpt-3.5-turbo")
        self.assertIsInstance(call_args[1]["messages"], list)

    @patch('core.ai.openai_client.OpenAI')
    @patch('core.ai.openai_client.AsyncOpenAI')
    def test_api_call_failure_fallback(self, mock_async_openai, mock_openai):
        """测试API调用失败时的降级处理"""
        # 模拟API调用失败
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client_instance

        client = OpenAIClient()

        response = client.get_ai_response_sync(
            user_message="你好",
            user_context={"monthly_spending": 100, "subscriptions": []}
        )

        # 验证降级响应
        self.assertIsNotNone(response["response"])
        self.assertIn("error", response)
        self.assertEqual(response["model"], "fallback")

    def test_build_context_string(self):
        """测试上下文字符串构建"""
        with patch('core.ai.openai_client.OpenAI'), \
             patch('core.ai.openai_client.AsyncOpenAI'):
            client = OpenAIClient()

            user_context = {
                "monthly_spending": 150.50,
                "subscriptions": [
                    {"service_name": "Netflix", "price": 15.99, "category": "entertainment", "status": "active"},
                    {"service_name": "Spotify", "price": 9.99, "category": "entertainment", "status": "active"}
                ],
                "subscription_categories": {
                    "entertainment": {"count": 2, "spending": 25.98}
                }
            }

            context_str = client._build_context_string(user_context)

            # 验证关键信息包含在上下文中
            self.assertIn("月度支出: ¥150.50", context_str)
            self.assertIn("订阅总数: 2", context_str)
            self.assertIn("Netflix: ¥15.99/月", context_str)
            self.assertIn("entertainment: 2个服务", context_str)

    def test_analyze_intent(self):
        """Test intent analysis function works"""
        with patch('core.ai.openai_client.OpenAI'), \
             patch('core.ai.openai_client.AsyncOpenAI'):
            client = OpenAIClient()

            test_messages = [
                "how much did I spend",
                "how many subscriptions",
                "cancel Netflix",
                "optimize my budget",
                "add new subscription",
                "just chatting",
                "unknown message"
            ]

            for message in test_messages:
                intent = client._analyze_intent(message)
                # Just verify that an intent is returned and it's a string
                self.assertIsInstance(intent, str)
                self.assertGreater(len(intent), 0)


if __name__ == '__main__':
    unittest.main()