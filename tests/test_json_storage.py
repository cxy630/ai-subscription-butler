"""
JSON存储系统单元测试
"""

import pytest
import unittest
import tempfile
import shutil
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database.json_storage import UserStorage, SubscriptionStorage, ConversationStorage, DataManager


class TestUserStorage(unittest.TestCase):
    """用户存储测试"""

    def setUp(self):
        """测试设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.user_storage = UserStorage(self.temp_dir)

    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.temp_dir)

    def test_create_user(self):
        """测试创建用户"""
        user_data = {
            "name": "测试用户",
            "email": "test@example.com",
            "phone": "1234567890"
        }

        user_id = self.user_storage.create_user(user_data)

        # 验证用户ID生成
        self.assertIsNotNone(user_id)
        self.assertIsInstance(user_id, str)

        # 验证用户数据保存
        saved_user = self.user_storage.get_user(user_id)
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user["name"], "测试用户")
        self.assertEqual(saved_user["email"], "test@example.com")
        self.assertIn("created_at", saved_user)

    def test_get_user_not_found(self):
        """测试获取不存在的用户"""
        result = self.user_storage.get_user("nonexistent-id")
        self.assertIsNone(result)

    def test_get_user_by_email(self):
        """测试通过邮箱获取用户"""
        user_data = {
            "name": "邮箱测试用户",
            "email": "email@test.com",
        }

        user_id = self.user_storage.create_user(user_data)
        found_user = self.user_storage.get_user_by_email("email@test.com")

        self.assertIsNotNone(found_user)
        self.assertEqual(found_user["id"], user_id)
        self.assertEqual(found_user["name"], "邮箱测试用户")

    def test_update_user(self):
        """测试更新用户"""
        # 创建用户
        user_data = {"name": "原始名称", "email": "original@test.com"}
        user_id = self.user_storage.create_user(user_data)

        # 更新用户
        updated_data = {"name": "更新名称", "phone": "9876543210"}
        success = self.user_storage.update_user(user_id, updated_data)

        self.assertTrue(success)

        # 验证更新
        updated_user = self.user_storage.get_user(user_id)
        self.assertEqual(updated_user["name"], "更新名称")
        self.assertEqual(updated_user["email"], "original@test.com")  # 保持不变
        self.assertEqual(updated_user["phone"], "9876543210")
        self.assertIn("updated_at", updated_user)

    def test_delete_user(self):
        """测试删除用户"""
        user_data = {"name": "待删除用户", "email": "delete@test.com"}
        user_id = self.user_storage.create_user(user_data)

        # 确认用户存在
        self.assertIsNotNone(self.user_storage.get_user(user_id))

        # 删除用户
        success = self.user_storage.delete_user(user_id)
        self.assertTrue(success)

        # 确认用户已删除
        self.assertIsNone(self.user_storage.get_user(user_id))

    def test_list_users(self):
        """测试列出所有用户"""
        # 创建多个用户
        users_data = [
            {"name": "用户1", "email": "user1@test.com"},
            {"name": "用户2", "email": "user2@test.com"},
            {"name": "用户3", "email": "user3@test.com"}
        ]

        created_ids = []
        for data in users_data:
            user_id = self.user_storage.create_user(data)
            created_ids.append(user_id)

        # 列出所有用户
        all_users = self.user_storage.list_users()

        self.assertEqual(len(all_users), 3)
        user_ids = [user["id"] for user in all_users]
        for created_id in created_ids:
            self.assertIn(created_id, user_ids)


class TestSubscriptionStorage(unittest.TestCase):
    """订阅存储测试"""

    def setUp(self):
        """测试设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.subscription_storage = SubscriptionStorage(self.temp_dir)
        self.test_user_id = "test-user-123"

    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.temp_dir)

    def test_create_subscription(self):
        """测试创建订阅"""
        subscription_data = {
            "service_name": "Netflix",
            "price": 15.99,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "entertainment",
            "status": "active"
        }

        subscription_id = self.subscription_storage.create_subscription(
            self.test_user_id, subscription_data
        )

        # 验证订阅ID
        self.assertIsNotNone(subscription_id)

        # 验证订阅数据
        saved_subscription = self.subscription_storage.get_subscription(subscription_id)
        self.assertIsNotNone(saved_subscription)
        self.assertEqual(saved_subscription["service_name"], "Netflix")
        self.assertEqual(saved_subscription["user_id"], self.test_user_id)
        self.assertEqual(saved_subscription["price"], 15.99)

    def test_get_user_subscriptions(self):
        """测试获取用户订阅"""
        # 创建多个订阅
        subscriptions_data = [
            {"service_name": "Netflix", "price": 15.99, "category": "entertainment"},
            {"service_name": "Spotify", "price": 9.99, "category": "entertainment"},
            {"service_name": "GitHub", "price": 4.0, "category": "productivity"}
        ]

        created_ids = []
        for data in subscriptions_data:
            sub_id = self.subscription_storage.create_subscription(self.test_user_id, data)
            created_ids.append(sub_id)

        # 获取用户所有订阅
        user_subs = self.subscription_storage.get_user_subscriptions(self.test_user_id)

        self.assertEqual(len(user_subs), 3)
        service_names = [sub["service_name"] for sub in user_subs]
        self.assertIn("Netflix", service_names)
        self.assertIn("Spotify", service_names)
        self.assertIn("GitHub", service_names)

    def test_get_active_subscriptions(self):
        """测试获取活跃订阅"""
        # 创建活跃和非活跃订阅
        active_sub = self.subscription_storage.create_subscription(
            self.test_user_id,
            {"service_name": "Active Service", "price": 10.0, "status": "active"}
        )

        paused_sub = self.subscription_storage.create_subscription(
            self.test_user_id,
            {"service_name": "Paused Service", "price": 5.0, "status": "paused"}
        )

        cancelled_sub = self.subscription_storage.create_subscription(
            self.test_user_id,
            {"service_name": "Cancelled Service", "price": 8.0, "status": "cancelled"}
        )

        # 获取活跃订阅
        active_subs = self.subscription_storage.get_active_subscriptions(self.test_user_id)

        self.assertEqual(len(active_subs), 1)
        self.assertEqual(active_subs[0]["service_name"], "Active Service")

    def test_update_subscription(self):
        """测试更新订阅"""
        # 创建订阅
        sub_id = self.subscription_storage.create_subscription(
            self.test_user_id,
            {"service_name": "Original Name", "price": 10.0}
        )

        # 更新订阅
        update_data = {"service_name": "Updated Name", "price": 12.99}
        success = self.subscription_storage.update_subscription(sub_id, update_data)

        self.assertTrue(success)

        # 验证更新
        updated_sub = self.subscription_storage.get_subscription(sub_id)
        self.assertEqual(updated_sub["service_name"], "Updated Name")
        self.assertEqual(updated_sub["price"], 12.99)

    def test_delete_subscription(self):
        """测试删除订阅"""
        sub_id = self.subscription_storage.create_subscription(
            self.test_user_id,
            {"service_name": "To Delete", "price": 5.0}
        )

        # 确认订阅存在
        self.assertIsNotNone(self.subscription_storage.get_subscription(sub_id))

        # 删除订阅
        success = self.subscription_storage.delete_subscription(sub_id)
        self.assertTrue(success)

        # 确认订阅已删除
        self.assertIsNone(self.subscription_storage.get_subscription(sub_id))


class TestConversationStorage(unittest.TestCase):
    """对话存储测试"""

    def setUp(self):
        """测试设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.conversation_storage = ConversationStorage(self.temp_dir)
        self.test_user_id = "test-user-456"
        self.test_session_id = "test-session-789"

    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.temp_dir)

    def test_save_conversation(self):
        """测试保存对话"""
        success = self.conversation_storage.save_conversation(
            user_id=self.test_user_id,
            session_id=self.test_session_id,
            message="测试用户消息",
            response="测试AI响应",
            intent="test_intent",
            confidence=0.85
        )

        self.assertTrue(success)

    def test_get_session_history(self):
        """测试获取会话历史"""
        # 保存多条对话
        conversations = [
            ("消息1", "响应1", "intent1", 0.9),
            ("消息2", "响应2", "intent2", 0.8),
            ("消息3", "响应3", "intent3", 0.95)
        ]

        for msg, resp, intent, conf in conversations:
            self.conversation_storage.save_conversation(
                self.test_user_id, self.test_session_id, msg, resp, intent, conf
            )

        # 获取历史记录
        history = self.conversation_storage.get_session_history(self.test_session_id)

        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["message"], "消息1")
        self.assertEqual(history[1]["response"], "响应2")
        self.assertEqual(history[2]["confidence"], 0.95)

    def test_get_user_conversations(self):
        """测试获取用户对话"""
        session1 = "session1"
        session2 = "session2"

        # 在不同会话中保存对话
        self.conversation_storage.save_conversation(
            self.test_user_id, session1, "会话1消息", "响应", "intent", 0.8
        )
        self.conversation_storage.save_conversation(
            self.test_user_id, session2, "会话2消息", "响应", "intent", 0.9
        )

        # 获取用户所有对话
        user_conversations = self.conversation_storage.get_user_conversations(self.test_user_id)

        self.assertEqual(len(user_conversations), 2)
        session_ids = [conv["session_id"] for conv in user_conversations]
        self.assertIn(session1, session_ids)
        self.assertIn(session2, session_ids)


class TestDataManager(unittest.TestCase):
    """数据管理器测试"""

    def setUp(self):
        """测试设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_manager = DataManager(self.temp_dir)

    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.temp_dir)

    def test_create_user_with_subscriptions(self):
        """测试创建用户和订阅的完整流程"""
        # 创建用户
        user_data = {"name": "完整测试用户", "email": "full@test.com"}
        user_id = self.data_manager.create_user(user_data)
        self.assertIsNotNone(user_id)

        # 创建订阅
        subscription_data = {
            "service_name": "Complete Test Service",
            "price": 25.99,
            "category": "productivity"
        }
        sub_id = self.data_manager.create_subscription(user_id, subscription_data)
        self.assertIsNotNone(sub_id)

        # 保存对话
        success = self.data_manager.save_conversation(
            user_id, "test-session", "测试消息", "测试响应", "test", 0.9
        )
        self.assertTrue(success)

        # 验证数据完整性
        user = self.data_manager.get_user(user_id)
        self.assertIsNotNone(user)

        user_subs = self.data_manager.get_user_subscriptions(user_id)
        self.assertEqual(len(user_subs), 1)
        self.assertEqual(user_subs[0]["service_name"], "Complete Test Service")

    def test_get_user_overview(self):
        """测试获取用户概览"""
        # 创建用户
        user_id = self.data_manager.create_user({"name": "概览测试", "email": "overview@test.com"})

        # 创建多个订阅
        subscriptions = [
            {"service_name": "Service1", "price": 10.0, "category": "entertainment", "status": "active"},
            {"service_name": "Service2", "price": 15.0, "category": "entertainment", "status": "active"},
            {"service_name": "Service3", "price": 20.0, "category": "productivity", "status": "active"},
            {"service_name": "Service4", "price": 5.0, "category": "productivity", "status": "paused"}
        ]

        for sub_data in subscriptions:
            self.data_manager.create_subscription(user_id, sub_data)

        # 获取概览
        overview = self.data_manager.get_user_overview(user_id)

        # 验证概览数据
        self.assertIsNotNone(overview)
        self.assertEqual(overview["total_subscriptions"], 4)
        self.assertEqual(overview["active_subscriptions"], 3)
        self.assertEqual(overview["monthly_spending"], 45.0)  # 10 + 15 + 20

        # 验证分类统计
        categories = overview["subscription_categories"]
        self.assertEqual(categories["entertainment"]["count"], 2)
        self.assertEqual(categories["entertainment"]["spending"], 25.0)
        self.assertEqual(categories["productivity"]["count"], 2)
        self.assertEqual(categories["productivity"]["spending"], 20.0)  # 只计算活跃的


if __name__ == '__main__':
    unittest.main()