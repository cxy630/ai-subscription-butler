"""
JSON storage system unit tests
"""

import pytest
import unittest
import tempfile
import shutil
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database.json_storage import UserStorage, SubscriptionStorage, ConversationStorage, DataManager


class TestUserStorage(unittest.TestCase):
    """User storage tests"""

    def setUp(self):
        """Test setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.user_storage = UserStorage(self.temp_dir)

    def tearDown(self):
        """Test cleanup"""
        shutil.rmtree(self.temp_dir)

    def test_create_user(self):
        """Test user creation"""
        user = self.user_storage.create_user(
            email="test@example.com",
            password_hash="test_hash",
            name="Test User"
        )

        # Verify user data
        self.assertIsNotNone(user["id"])
        self.assertEqual(user["email"], "test@example.com")
        self.assertEqual(user["name"], "Test User")
        self.assertIn("created_at", user)

    def test_get_user_not_found(self):
        """Test getting non-existent user"""
        result = self.user_storage.get_user_by_id("nonexistent-id")
        self.assertIsNone(result)

    def test_get_user_by_email(self):
        """Test getting user by email"""
        user = self.user_storage.create_user(
            email="email@test.com",
            password_hash="test_hash",
            name="Email Test User"
        )

        found_user = self.user_storage.get_user_by_email("email@test.com")

        self.assertIsNotNone(found_user)
        self.assertEqual(found_user["id"], user["id"])
        self.assertEqual(found_user["name"], "Email Test User")

    def test_update_user(self):
        """Test user update"""
        # Create user
        user = self.user_storage.create_user(
            email="original@test.com",
            password_hash="test_hash",
            name="Original Name"
        )
        user_id = user["id"]

        # Update user
        updated_data = {"name": "Updated Name"}
        success = self.user_storage.update_user(user_id, updated_data)

        self.assertTrue(success)

        # Verify update
        updated_user = self.user_storage.get_user_by_id(user_id)
        self.assertEqual(updated_user["name"], "Updated Name")
        self.assertEqual(updated_user["email"], "original@test.com")  # Unchanged
        self.assertIn("updated_at", updated_user)


class TestSubscriptionStorage(unittest.TestCase):
    """Subscription storage tests"""

    def setUp(self):
        """Test setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.subscription_storage = SubscriptionStorage(self.temp_dir)
        self.test_user_id = "test-user-123"

    def tearDown(self):
        """Test cleanup"""
        shutil.rmtree(self.temp_dir)

    def test_create_subscription(self):
        """Test subscription creation"""
        subscription_data = {
            "service_name": "Netflix",
            "price": 15.99,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "entertainment",
            "status": "active"
        }

        subscription = self.subscription_storage.create_subscription(
            self.test_user_id, subscription_data
        )

        # Verify subscription data
        self.assertIsNotNone(subscription["id"])
        self.assertEqual(subscription["service_name"], "Netflix")
        self.assertEqual(subscription["user_id"], self.test_user_id)
        self.assertEqual(subscription["price"], 15.99)

    def test_get_user_subscriptions(self):
        """Test getting user subscriptions"""
        # Create multiple subscriptions
        subscriptions_data = [
            {"service_name": "Netflix", "price": 15.99, "category": "entertainment"},
            {"service_name": "Spotify", "price": 9.99, "category": "entertainment"},
            {"service_name": "GitHub", "price": 4.0, "category": "productivity"}
        ]

        created_ids = []
        for data in subscriptions_data:
            sub = self.subscription_storage.create_subscription(self.test_user_id, data)
            created_ids.append(sub["id"])

        # Get user subscriptions
        user_subs = self.subscription_storage.get_user_subscriptions(self.test_user_id)

        self.assertEqual(len(user_subs), 3)
        service_names = [sub["service_name"] for sub in user_subs]
        self.assertIn("Netflix", service_names)
        self.assertIn("Spotify", service_names)
        self.assertIn("GitHub", service_names)

    def test_get_active_subscriptions(self):
        """Test getting active subscriptions"""
        # Create active and inactive subscriptions
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

        # Get active subscriptions
        active_subs = self.subscription_storage.get_active_subscriptions(self.test_user_id)

        self.assertEqual(len(active_subs), 1)
        self.assertEqual(active_subs[0]["service_name"], "Active Service")

    def test_update_subscription(self):
        """Test subscription update"""
        # Create subscription
        sub = self.subscription_storage.create_subscription(
            self.test_user_id,
            {"service_name": "Original Name", "price": 10.0}
        )
        sub_id = sub["id"]

        # Update subscription
        update_data = {"service_name": "Updated Name", "price": 12.99}
        success = self.subscription_storage.update_subscription(sub_id, update_data)

        self.assertTrue(success)

        # Verify update
        updated_sub = self.subscription_storage.get_subscription_by_id(sub_id)
        self.assertEqual(updated_sub["service_name"], "Updated Name")
        self.assertEqual(updated_sub["price"], 12.99)

    def test_delete_subscription(self):
        """Test subscription deletion"""
        sub = self.subscription_storage.create_subscription(
            self.test_user_id,
            {"service_name": "To Delete", "price": 5.0}
        )
        sub_id = sub["id"]

        # Confirm subscription exists
        self.assertIsNotNone(self.subscription_storage.get_subscription_by_id(sub_id))

        # Delete subscription
        success = self.subscription_storage.delete_subscription(sub_id)
        self.assertTrue(success)

        # Confirm subscription is deleted
        self.assertIsNone(self.subscription_storage.get_subscription_by_id(sub_id))


class TestConversationStorage(unittest.TestCase):
    """Conversation storage tests"""

    def setUp(self):
        """Test setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.conversation_storage = ConversationStorage(self.temp_dir)
        self.test_user_id = "test-user-456"
        self.test_session_id = "test-session-789"

    def tearDown(self):
        """Test cleanup"""
        shutil.rmtree(self.temp_dir)

    def test_save_conversation(self):
        """Test conversation saving"""
        conversation = self.conversation_storage.save_conversation(
            user_id=self.test_user_id,
            session_id=self.test_session_id,
            message="Test user message",
            response="Test AI response",
            intent="test_intent",
            confidence=0.85
        )

        self.assertIsNotNone(conversation["id"])
        self.assertEqual(conversation["user_id"], self.test_user_id)
        self.assertEqual(conversation["message"], "Test user message")

    def test_get_session_history(self):
        """Test session history retrieval"""
        # Save multiple conversations
        conversations = [
            ("Message1", "Response1", "intent1", 0.9),
            ("Message2", "Response2", "intent2", 0.8),
            ("Message3", "Response3", "intent3", 0.95)
        ]

        for msg, resp, intent, conf in conversations:
            self.conversation_storage.save_conversation(
                self.test_user_id, self.test_session_id, msg, resp, intent, conf
            )

        # Get history (should be in reverse chronological order)
        history = self.conversation_storage.get_session_history(self.test_session_id)

        self.assertEqual(len(history), 3)
        # Most recent first due to reverse ordering
        self.assertEqual(history[0]["message"], "Message3")
        self.assertEqual(history[1]["response"], "Response2")
        self.assertEqual(history[2]["confidence"], 0.9)


class TestDataManager(unittest.TestCase):
    """Data manager tests"""

    def setUp(self):
        """Test setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_manager = DataManager(self.temp_dir)

    def tearDown(self):
        """Test cleanup"""
        shutil.rmtree(self.temp_dir)

    def test_create_user_with_subscriptions(self):
        """Test complete user and subscription workflow"""
        # Create user
        user = self.data_manager.users.create_user(
            email="full@test.com",
            password_hash="test_hash",
            name="Complete Test User"
        )
        user_id = user["id"]

        # Create subscription
        subscription_data = {
            "service_name": "Complete Test Service",
            "price": 25.99,
            "category": "productivity"
        }
        sub = self.data_manager.subscriptions.create_subscription(user_id, subscription_data)
        self.assertIsNotNone(sub["id"])

        # Save conversation
        conversation = self.data_manager.conversations.save_conversation(
            user_id, "test-session", "Test message", "Test response", "test", 0.9
        )
        self.assertIsNotNone(conversation["id"])

        # Verify data integrity
        user = self.data_manager.users.get_user_by_id(user_id)
        self.assertIsNotNone(user)

        user_subs = self.data_manager.subscriptions.get_user_subscriptions(user_id)
        self.assertEqual(len(user_subs), 1)
        self.assertEqual(user_subs[0]["service_name"], "Complete Test Service")

    def test_get_user_overview(self):
        """Test user overview"""
        # Create user
        user = self.data_manager.users.create_user(
            email="overview@test.com",
            password_hash="test_hash",
            name="Overview Test"
        )
        user_id = user["id"]

        # Create multiple subscriptions
        subscriptions = [
            {"service_name": "Service1", "price": 10.0, "category": "entertainment", "status": "active"},
            {"service_name": "Service2", "price": 15.0, "category": "entertainment", "status": "active"},
            {"service_name": "Service3", "price": 20.0, "category": "productivity", "status": "active"},
            {"service_name": "Service4", "price": 5.0, "category": "productivity", "status": "paused"}
        ]

        for sub_data in subscriptions:
            self.data_manager.subscriptions.create_subscription(user_id, sub_data)

        # Get overview
        overview = self.data_manager.get_user_overview(user_id)

        # Verify overview data
        self.assertIsNotNone(overview)
        self.assertEqual(overview["total_subscriptions"], 4)
        self.assertEqual(overview["active_subscriptions"], 3)
        self.assertEqual(overview["monthly_spending"], 45.0)  # 10 + 15 + 20

        # Verify category breakdown
        categories = overview["subscription_categories"]
        self.assertEqual(categories["entertainment"]["count"], 2)
        self.assertEqual(categories["entertainment"]["spending"], 25.0)
        self.assertEqual(categories["productivity"]["count"], 1)  # Only active counted
        self.assertEqual(categories["productivity"]["spending"], 20.0)  # Only active


if __name__ == '__main__':
    unittest.main()