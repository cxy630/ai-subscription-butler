"""
SQLite数据模型 - 轻量级数据库方案
基于原PostgreSQL设计，适配SQLite环境
"""

from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import uuid
import json

Base = declarative_base()


class User(Base):
    """用户模型"""
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    subscription_tier = Column(String(20), default='free')  # free, premium, enterprise

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'subscription_tier': self.subscription_tier
        }


class Subscription(Base):
    """订阅模型"""
    __tablename__ = 'subscriptions'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    service_name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default='CNY')
    billing_cycle = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    category = Column(String(50), index=True)
    next_billing_date = Column(String(10))  # 存储为字符串格式 YYYY-MM-DD
    status = Column(String(20), default='active', index=True)  # active, cancelled, paused
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_name': self.service_name,
            'price': float(self.price) if self.price else 0,
            'currency': self.currency,
            'billing_cycle': self.billing_cycle,
            'category': self.category,
            'next_billing_date': self.next_billing_date,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Conversation(Base):
    """对话历史模型"""
    __tablename__ = 'conversations'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    session_id = Column(String(36), nullable=False, index=True)
    message = Column(Text, nullable=False)
    response = Column(Text)
    intent = Column(String(100), index=True)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'message': self.message,
            'response': self.response,
            'intent': self.intent,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class OCRRecord(Base):
    """OCR处理记录模型"""
    __tablename__ = 'ocr_records'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    extracted_data = Column(Text)  # JSON字符串
    confidence_score = Column(Float)
    status = Column(String(20), default='processing', index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_extracted_data(self) -> Dict[str, Any]:
        """获取提取的数据"""
        if self.extracted_data:
            try:
                return json.loads(self.extracted_data)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_extracted_data(self, data: Dict[str, Any]):
        """设置提取的数据"""
        self.extracted_data = json.dumps(data, ensure_ascii=False)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_path': self.file_path,
            'extracted_data': self.get_extracted_data(),
            'confidence_score': self.confidence_score,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SQLiteDataManager:
    """SQLite数据管理器"""

    def __init__(self, database_url: str = "sqlite:///data/subscriptions.db"):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # 创建表
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    # 用户相关操作
    def create_user(self, email: str, password_hash: str, name: str = None) -> Optional[User]:
        """创建用户"""
        with self.get_session() as db:
            # 检查邮箱是否已存在
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                return None

            user = User(
                email=email,
                password_hash=password_hash,
                name=name
            )

            db.add(user)
            db.commit()
            db.refresh(user)
            return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        with self.get_session() as db:
            return db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        with self.get_session() as db:
            return db.query(User).filter(User.id == user_id).first()

    # 订阅相关操作
    def create_subscription(self, user_id: str, subscription_data: Dict[str, Any]) -> Optional[Subscription]:
        """创建订阅"""
        with self.get_session() as db:
            subscription = Subscription(
                user_id=user_id,
                **subscription_data
            )

            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            return subscription

    def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """获取用户所有订阅"""
        with self.get_session() as db:
            return db.query(Subscription).filter(Subscription.user_id == user_id).all()

    def get_active_subscriptions(self, user_id: str) -> List[Subscription]:
        """获取用户活跃订阅"""
        with self.get_session() as db:
            return db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.status == 'active'
            ).all()

    def update_subscription(self, subscription_id: str, updates: Dict[str, Any]) -> bool:
        """更新订阅"""
        with self.get_session() as db:
            subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
            if not subscription:
                return False

            for key, value in updates.items():
                if hasattr(subscription, key):
                    setattr(subscription, key, value)

            subscription.updated_at = datetime.utcnow()
            db.commit()
            return True

    def delete_subscription(self, subscription_id: str) -> bool:
        """删除订阅"""
        with self.get_session() as db:
            subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
            if not subscription:
                return False

            db.delete(subscription)
            db.commit()
            return True

    # 对话相关操作
    def save_conversation(self, user_id: str, session_id: str, message: str,
                         response: str, intent: str = None, confidence: float = None) -> Conversation:
        """保存对话记录"""
        with self.get_session() as db:
            conversation = Conversation(
                user_id=user_id,
                session_id=session_id,
                message=message,
                response=response,
                intent=intent,
                confidence=confidence
            )

            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation

    def get_session_history(self, session_id: str, limit: int = 10) -> List[Conversation]:
        """获取会话历史"""
        with self.get_session() as db:
            return db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).order_by(Conversation.created_at.desc()).limit(limit).all()

    # 用户概览
    def get_user_overview(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户概览"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        subscriptions = self.get_user_subscriptions(user_id)
        active_subscriptions = self.get_active_subscriptions(user_id)

        # 计算月度支出
        monthly_spending = 0
        category_breakdown = {}

        for sub in active_subscriptions:
            price = sub.price or 0
            cycle = sub.billing_cycle or "monthly"

            # 标准化为月度成本
            if cycle == "monthly":
                monthly_price = price
            elif cycle == "yearly":
                monthly_price = price / 12
            elif cycle == "weekly":
                monthly_price = price * 4.33
            elif cycle == "daily":
                monthly_price = price * 30
            else:
                monthly_price = price

            monthly_spending += monthly_price

            # 分类统计
            category = sub.category or "other"
            if category not in category_breakdown:
                category_breakdown[category] = {"count": 0, "spending": 0}

            category_breakdown[category]["count"] += 1
            category_breakdown[category]["spending"] += monthly_price

        return {
            "user": user.to_dict(),
            "total_subscriptions": len(subscriptions),
            "active_subscriptions": len(active_subscriptions),
            "monthly_spending": round(monthly_spending, 2),
            "subscription_categories": category_breakdown,
            "subscriptions": [sub.to_dict() for sub in active_subscriptions]
        }

    def search_subscriptions(self, user_id: str, query: str) -> List[Subscription]:
        """搜索订阅"""
        with self.get_session() as db:
            query_lower = f"%{query.lower()}%"
            return db.query(Subscription).filter(
                Subscription.user_id == user_id,
                db.func.lower(Subscription.service_name).like(query_lower)
            ).all()


# 全局SQLite数据管理器实例
sqlite_manager = SQLiteDataManager()


def init_sqlite_sample_data():
    """初始化SQLite示例数据"""
    # 创建示例用户
    user = sqlite_manager.create_user(
        email="demo@example.com",
        password_hash="$2b$12$sample_hash",
        name="演示用户"
    )

    if not user:
        # 用户已存在，获取现有用户
        user = sqlite_manager.get_user_by_email("demo@example.com")

    user_id = user.id

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
            "price": 140.0,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "productivity",
            "status": "active",
            "next_billing_date": "2025-02-20"
        },
        {
            "service_name": "Adobe Creative Cloud",
            "price": 348.0,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "productivity",
            "status": "active",
            "next_billing_date": "2025-02-12"
        }
    ]

    for sub_data in sample_subscriptions:
        # 检查是否已存在相同订阅
        existing = sqlite_manager.get_user_subscriptions(user_id)
        exists = any(sub.service_name == sub_data["service_name"] for sub in existing)

        if not exists:
            sqlite_manager.create_subscription(user_id, sub_data)

    print(f"SQLite示例数据已创建！用户ID: {user_id}")
    return user_id


if __name__ == "__main__":
    # 测试SQLite数据存储
    print("初始化SQLite数据存储...")
    user_id = init_sqlite_sample_data()

    # 测试查询
    overview = sqlite_manager.get_user_overview(user_id)
    print(f"用户概览: {overview}")