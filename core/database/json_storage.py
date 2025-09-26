"""
JSON文件存储 - 数据库的临时替代方案
用于开发和演示阶段，无需数据库环境
"""

import json
import os
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod


class JSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理日期和UUID"""

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


class BaseJSONStorage(ABC):
    """JSON存储基类"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._lock = threading.RLock()

    @abstractmethod
    def _get_filename(self) -> str:
        """获取存储文件名"""
        pass

    def _get_file_path(self) -> Path:
        """获取完整文件路径"""
        return self.data_dir / self._get_filename()

    def _load_data(self) -> List[Dict[str, Any]]:
        """从文件加载数据"""
        file_path = self._get_file_path()
        if not file_path.exists():
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        """保存数据到文件"""
        file_path = self._get_file_path()

        with self._lock:
            # 备份现有文件
            backup_path = file_path.with_suffix('.bak')
            if file_path.exists():
                file_path.rename(backup_path)

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, cls=JSONEncoder, indent=2, ensure_ascii=False)

                # 删除备份文件
                if backup_path.exists():
                    backup_path.unlink()

            except Exception as e:
                # 恢复备份
                if backup_path.exists():
                    backup_path.rename(file_path)
                raise e


class UserStorage(BaseJSONStorage):
    """用户数据存储"""

    def _get_filename(self) -> str:
        return "users.json"

    def create_user(self, email: str, password_hash: str, name: str = None) -> Dict[str, Any]:
        """创建用户"""
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_active": True,
            "is_verified": False,
            "subscription_tier": "free"
        }

        users = self._load_data()
        users.append(user)
        self._save_data(users)

        return user

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        users = self._load_data()
        for user in users:
            if user["email"] == email:
                return user
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        users = self._load_data()
        for user in users:
            if user["id"] == user_id:
                return user
        return None

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """更新用户信息"""
        users = self._load_data()
        for i, user in enumerate(users):
            if user["id"] == user_id:
                users[i].update(updates)
                users[i]["updated_at"] = datetime.now().isoformat()
                self._save_data(users)
                return True
        return False


class SubscriptionStorage(BaseJSONStorage):
    """订阅数据存储"""

    def _get_filename(self) -> str:
        return "subscriptions.json"

    def create_subscription(self, user_id: str, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建订阅"""
        subscription_id = str(uuid.uuid4())
        subscription = {
            "id": subscription_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **subscription_data
        }

        subscriptions = self._load_data()
        subscriptions.append(subscription)
        self._save_data(subscriptions)

        return subscription

    def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户的所有订阅"""
        subscriptions = self._load_data()
        return [sub for sub in subscriptions if sub["user_id"] == user_id]

    def get_subscription_by_id(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取订阅"""
        subscriptions = self._load_data()
        for sub in subscriptions:
            if sub["id"] == subscription_id:
                return sub
        return None

    def update_subscription(self, subscription_id: str, updates: Dict[str, Any]) -> bool:
        """更新订阅"""
        subscriptions = self._load_data()
        for i, sub in enumerate(subscriptions):
            if sub["id"] == subscription_id:
                subscriptions[i].update(updates)
                subscriptions[i]["updated_at"] = datetime.now().isoformat()
                self._save_data(subscriptions)
                return True
        return False

    def delete_subscription(self, subscription_id: str) -> bool:
        """删除订阅"""
        subscriptions = self._load_data()
        for i, sub in enumerate(subscriptions):
            if sub["id"] == subscription_id:
                subscriptions.pop(i)
                self._save_data(subscriptions)
                return True
        return False

    def get_active_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户活跃订阅"""
        subscriptions = self.get_user_subscriptions(user_id)
        return [sub for sub in subscriptions if sub.get("status", "active") == "active"]


class ConversationStorage(BaseJSONStorage):
    """对话历史存储"""

    def _get_filename(self) -> str:
        return "conversations.json"

    def save_conversation(self, user_id: str, session_id: str, message: str,
                         response: str, intent: str = None, confidence: float = None) -> Dict[str, Any]:
        """保存对话记录"""
        conversation_id = str(uuid.uuid4())
        conversation = {
            "id": conversation_id,
            "user_id": user_id,
            "session_id": session_id,
            "message": message,
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "created_at": datetime.now().isoformat()
        }

        conversations = self._load_data()
        conversations.append(conversation)
        self._save_data(conversations)

        return conversation

    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取会话历史"""
        conversations = self._load_data()
        session_conversations = [
            conv for conv in conversations
            if conv["session_id"] == session_id
        ]
        # 按时间倒序排列，取最近的记录
        session_conversations.sort(key=lambda x: x["created_at"], reverse=True)
        return session_conversations[:limit]


class OCRStorage(BaseJSONStorage):
    """OCR处理记录存储"""

    def _get_filename(self) -> str:
        return "ocr_records.json"

    def create_ocr_record(self, user_id: str, file_path: str,
                         extracted_data: Dict[str, Any] = None,
                         confidence_score: float = None) -> Dict[str, Any]:
        """创建OCR记录"""
        record_id = str(uuid.uuid4())
        record = {
            "id": record_id,
            "user_id": user_id,
            "file_path": file_path,
            "extracted_data": extracted_data,
            "confidence_score": confidence_score,
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        records = self._load_data()
        records.append(record)
        self._save_data(records)

        return record

    def update_ocr_record(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """更新OCR记录"""
        records = self._load_data()
        for i, record in enumerate(records):
            if record["id"] == record_id:
                records[i].update(updates)
                records[i]["updated_at"] = datetime.now().isoformat()
                self._save_data(records)
                return True
        return False


class DataManager:
    """数据管理器 - 统一数据访问接口"""

    def __init__(self, data_dir: str = "data"):
        self.users = UserStorage(data_dir)
        self.subscriptions = SubscriptionStorage(data_dir)
        self.conversations = ConversationStorage(data_dir)
        self.ocr_records = OCRStorage(data_dir)

    def get_user_overview(self, user_id: str) -> Dict[str, Any]:
        """获取用户概览信息"""
        user = self.users.get_user_by_id(user_id)
        if not user:
            return None

        subscriptions = self.subscriptions.get_user_subscriptions(user_id)
        active_subscriptions = self.subscriptions.get_active_subscriptions(user_id)

        # 计算月度支出
        monthly_spending = 0
        for sub in active_subscriptions:
            price = sub.get("price", 0)
            cycle = sub.get("billing_cycle", "monthly")

            if cycle == "monthly":
                monthly_spending += price
            elif cycle == "yearly":
                monthly_spending += price / 12
            elif cycle == "weekly":
                monthly_spending += price * 4.33
            elif cycle == "daily":
                monthly_spending += price * 30

        return {
            "user": user,
            "total_subscriptions": len(subscriptions),
            "active_subscriptions": len(active_subscriptions),
            "monthly_spending": round(monthly_spending, 2),
            "subscription_categories": self._get_category_breakdown(active_subscriptions)
        }

    def _get_category_breakdown(self, subscriptions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """获取分类统计"""
        categories = {}
        for sub in subscriptions:
            category = sub.get("category", "other")
            if category not in categories:
                categories[category] = {"count": 0, "spending": 0}

            categories[category]["count"] += 1

            price = sub.get("price", 0)
            cycle = sub.get("billing_cycle", "monthly")

            if cycle == "monthly":
                monthly_price = price
            elif cycle == "yearly":
                monthly_price = price / 12
            else:
                monthly_price = price

            categories[category]["spending"] += monthly_price

        return categories

    def search_subscriptions(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """搜索订阅"""
        subscriptions = self.subscriptions.get_user_subscriptions(user_id)
        query_lower = query.lower()

        results = []
        for sub in subscriptions:
            if (query_lower in sub.get("service_name", "").lower() or
                query_lower in sub.get("category", "").lower() or
                query_lower in sub.get("notes", "").lower()):
                results.append(sub)

        return results


# 全局数据管理器实例
data_manager = DataManager()


def init_sample_data():
    """初始化示例数据"""
    # 创建示例用户
    sample_user = data_manager.users.create_user(
        email="demo@example.com",
        password_hash="$2b$12$sample_hash",
        name="演示用户"
    )

    user_id = sample_user["id"]

    # 创建示例订阅
    sample_subscriptions = [
        {
            "service_name": "Netflix",
            "price": 15.99,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "entertainment",
            "status": "active",
            "next_billing_date": "2025-02-15"
        },
        {
            "service_name": "Spotify",
            "price": 9.99,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "entertainment",
            "status": "active",
            "next_billing_date": "2025-02-10"
        },
        {
            "service_name": "ChatGPT Plus",
            "price": 20.0,
            "currency": "USD",
            "billing_cycle": "monthly",
            "category": "productivity",
            "status": "active",
            "next_billing_date": "2025-02-20"
        }
    ]

    for sub_data in sample_subscriptions:
        data_manager.subscriptions.create_subscription(user_id, sub_data)

    print(f"示例数据已创建！用户ID: {user_id}")
    return user_id


if __name__ == "__main__":
    # 测试数据存储
    print("初始化JSON数据存储...")
    user_id = init_sample_data()

    # 测试查询
    overview = data_manager.get_user_overview(user_id)
    print(f"用户概览: {overview}")