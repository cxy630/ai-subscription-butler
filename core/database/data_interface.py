"""
数据访问接口抽象层
提供统一的数据访问接口，支持多种存储后端切换
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum


class StorageBackend(Enum):
    """存储后端类型"""
    JSON = "json"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class DataInterface(ABC):
    """数据访问抽象接口"""

    @abstractmethod
    def create_user(self, email: str, password_hash: str, name: str = None) -> Optional[Dict[str, Any]]:
        """创建用户"""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        pass

    @abstractmethod
    def create_subscription(self, user_id: str, subscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建订阅"""
        pass

    @abstractmethod
    def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户所有订阅"""
        pass

    @abstractmethod
    def get_active_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户活跃订阅"""
        pass

    @abstractmethod
    def update_subscription(self, subscription_id: str, updates: Dict[str, Any]) -> bool:
        """更新订阅"""
        pass

    @abstractmethod
    def delete_subscription(self, subscription_id: str) -> bool:
        """删除订阅"""
        pass

    @abstractmethod
    def save_conversation(self, user_id: str, session_id: str, message: str,
                         response: str, intent: str = None, confidence: float = None) -> Dict[str, Any]:
        """保存对话记录"""
        pass

    @abstractmethod
    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取会话历史"""
        pass

    @abstractmethod
    def get_user_overview(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户概览"""
        pass

    @abstractmethod
    def search_subscriptions(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """搜索订阅"""
        pass


class JSONDataInterface(DataInterface):
    """JSON文件存储接口实现"""

    def __init__(self):
        from .json_storage import data_manager
        self.data_manager = data_manager

    def create_user(self, email: str, password_hash: str, name: str = None) -> Optional[Dict[str, Any]]:
        return self.data_manager.users.create_user(email, password_hash, name)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.data_manager.users.get_user_by_email(email)

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.data_manager.users.get_user_by_id(user_id)

    def create_subscription(self, user_id: str, subscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.data_manager.subscriptions.create_subscription(user_id, subscription_data)

    def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        return self.data_manager.subscriptions.get_user_subscriptions(user_id)

    def get_active_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        return self.data_manager.subscriptions.get_active_subscriptions(user_id)

    def update_subscription(self, subscription_id: str, updates: Dict[str, Any]) -> bool:
        return self.data_manager.subscriptions.update_subscription(subscription_id, updates)

    def delete_subscription(self, subscription_id: str) -> bool:
        return self.data_manager.subscriptions.delete_subscription(subscription_id)

    def save_conversation(self, user_id: str, session_id: str, message: str,
                         response: str, intent: str = None, confidence: float = None) -> Dict[str, Any]:
        return self.data_manager.conversations.save_conversation(
            user_id, session_id, message, response, intent, confidence
        )

    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self.data_manager.conversations.get_session_history(session_id, limit)

    def get_user_overview(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.data_manager.get_user_overview(user_id)

    def search_subscriptions(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        return self.data_manager.search_subscriptions(user_id, query)


class SQLiteDataInterface(DataInterface):
    """SQLite数据库接口实现"""

    def __init__(self):
        from .sqlite_models import sqlite_manager
        self.sqlite_manager = sqlite_manager

    def create_user(self, email: str, password_hash: str, name: str = None) -> Optional[Dict[str, Any]]:
        user = self.sqlite_manager.create_user(email, password_hash, name)
        return user.to_dict() if user else None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        user = self.sqlite_manager.get_user_by_email(email)
        return user.to_dict() if user else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        user = self.sqlite_manager.get_user_by_id(user_id)
        return user.to_dict() if user else None

    def create_subscription(self, user_id: str, subscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        subscription = self.sqlite_manager.create_subscription(user_id, subscription_data)
        return subscription.to_dict() if subscription else None

    def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        subscriptions = self.sqlite_manager.get_user_subscriptions(user_id)
        return [sub.to_dict() for sub in subscriptions]

    def get_active_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        subscriptions = self.sqlite_manager.get_active_subscriptions(user_id)
        return [sub.to_dict() for sub in subscriptions]

    def update_subscription(self, subscription_id: str, updates: Dict[str, Any]) -> bool:
        return self.sqlite_manager.update_subscription(subscription_id, updates)

    def delete_subscription(self, subscription_id: str) -> bool:
        return self.sqlite_manager.delete_subscription(subscription_id)

    def save_conversation(self, user_id: str, session_id: str, message: str,
                         response: str, intent: str = None, confidence: float = None) -> Dict[str, Any]:
        conversation = self.sqlite_manager.save_conversation(
            user_id, session_id, message, response, intent, confidence
        )
        return conversation.to_dict()

    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        conversations = self.sqlite_manager.get_session_history(session_id, limit)
        return [conv.to_dict() for conv in conversations]

    def get_user_overview(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.sqlite_manager.get_user_overview(user_id)

    def search_subscriptions(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        subscriptions = self.sqlite_manager.search_subscriptions(user_id, query)
        return [sub.to_dict() for sub in subscriptions]


class DataManager:
    """统一数据管理器"""

    def __init__(self, backend: StorageBackend = StorageBackend.JSON):
        self.backend = backend
        self._interface = self._create_interface()

    def _create_interface(self) -> DataInterface:
        """创建数据接口"""
        if self.backend == StorageBackend.JSON:
            return JSONDataInterface()
        elif self.backend == StorageBackend.SQLITE:
            return SQLiteDataInterface()
        else:
            raise ValueError(f"不支持的存储后端: {self.backend}")

    def switch_backend(self, backend: StorageBackend):
        """切换存储后端"""
        self.backend = backend
        self._interface = self._create_interface()

    # 代理所有数据接口方法
    def create_user(self, email: str, password_hash: str, name: str = None) -> Optional[Dict[str, Any]]:
        return self._interface.create_user(email, password_hash, name)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self._interface.get_user_by_email(email)

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._interface.get_user_by_id(user_id)

    def create_subscription(self, user_id: str, subscription_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self._interface.create_subscription(user_id, subscription_data)

    def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        return self._interface.get_user_subscriptions(user_id)

    def get_active_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        return self._interface.get_active_subscriptions(user_id)

    def update_subscription(self, subscription_id: str, updates: Dict[str, Any]) -> bool:
        return self._interface.update_subscription(subscription_id, updates)

    def delete_subscription(self, subscription_id: str) -> bool:
        return self._interface.delete_subscription(subscription_id)

    def save_conversation(self, user_id: str, session_id: str, message: str,
                         response: str, intent: str = None, confidence: float = None) -> Dict[str, Any]:
        return self._interface.save_conversation(user_id, session_id, message, response, intent, confidence)

    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self._interface.get_session_history(session_id, limit)

    def get_user_overview(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._interface.get_user_overview(user_id)

    def search_subscriptions(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        return self._interface.search_subscriptions(user_id, query)


# 获取当前配置的数据管理器
def get_data_manager(backend: StorageBackend = None) -> DataManager:
    """获取数据管理器实例"""
    if backend is None:
        # 从配置文件读取默认后端
        from app.config import settings
        backend_str = getattr(settings, 'storage_backend', 'json').lower()
        backend = StorageBackend(backend_str) if backend_str in ['json', 'sqlite'] else StorageBackend.JSON

    return DataManager(backend)


# 全局数据管理器实例（默认使用JSON存储）
data_manager = get_data_manager()


def init_sample_data():
    """初始化示例数据"""
    # 根据当前后端初始化示例数据
    if data_manager.backend == StorageBackend.JSON:
        from .json_storage import init_sample_data
        return init_sample_data()
    elif data_manager.backend == StorageBackend.SQLITE:
        from .sqlite_models import init_sqlite_sample_data
        return init_sqlite_sample_data()


if __name__ == "__main__":
    # 测试数据接口
    print("测试统一数据接口...")

    # 测试JSON后端
    print("\n=== JSON存储测试 ===")
    json_manager = DataManager(StorageBackend.JSON)
    user_id = init_sample_data()
    overview = json_manager.get_user_overview(user_id)
    print(f"JSON - 用户概览: 总订阅数={overview['total_subscriptions']}, 月度支出={overview['monthly_spending']}")

    # 测试SQLite后端
    print("\n=== SQLite存储测试 ===")
    sqlite_manager = DataManager(StorageBackend.SQLITE)
    sqlite_manager.switch_backend(StorageBackend.SQLITE)
    user_id_sqlite = init_sample_data()
    overview_sqlite = sqlite_manager.get_user_overview(user_id_sqlite)
    print(f"SQLite - 用户概览: 总订阅数={overview_sqlite['total_subscriptions']}, 月度支出={overview_sqlite['monthly_spending']}")

    print("\n✅ 数据接口测试完成！")