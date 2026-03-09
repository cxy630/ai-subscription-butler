import os
import json
import uuid
from datetime import datetime
import sqlite3
from sqlalchemy.orm import Session

# 设置环境变量确保使用 sqlite 后端进行初始化
os.environ["STORAGE_BACKEND"] = "sqlite"

from core.database.json_storage import JSONDataManager
from core.database.sqlite_models import SQLiteDataManager, Base

def migrate_data():
    """将数据从 JSON 迁移到 SQLite"""
    print("开始数据迁移 (JSON -> SQLite)...")
    
    # 1. 确保 SQLite 数据库初始化
    sqlite_manager = SQLiteDataManager()
    
    # 2. 读取 JSON 文件数据
    json_manager = JSONDataManager()
    
    # 获取底层数据模型
    users_data = json_manager._load_data(json_manager.users.users_file)
    subscriptions_data = json_manager._load_data(json_manager.subscriptions.subscriptions_file)
    conversations_data = json_manager._load_data(json_manager.conversations.conversations_file)
    
    # 获取会话
    with sqlite_manager.get_session() as session:
        # --- 迁移用户 ---
        users_count = 0
        user_id_map = {}  # 保持原有 ID
        
        for email, u in users_data.items():
            user_id = u.get("id")
            
            # 检查是否已存在
            from core.database.sqlite_models import User
            existing = session.query(User).filter(User.id == user_id).first()
            if existing:
                print(f"用户 {email} 已存在，跳过。")
                continue
                
            new_user = User(
                id=user_id,
                email=email,
                password_hash=u.get("password_hash", "default_hash"),
                name=u.get("name"),
                created_at=datetime.fromisoformat(u.get("created_at")) if u.get("created_at") else datetime.utcnow(),
                is_active=u.get("is_active", True),
                subscription_tier=u.get("subscription_tier", "free")
            )
            session.add(new_user)
            users_count += 1
            print(f"准备插入用户: {email} (ID: {user_id})")
        
        # --- 迁移订阅 ---
        subs_count = 0
        for sub_id, s in subscriptions_data.items():
            from core.database.sqlite_models import Subscription
            existing = session.query(Subscription).filter(Subscription.id == sub_id).first()
            if existing:
                continue
                
            new_sub = Subscription(
                id=sub_id,
                user_id=s.get("user_id"),
                service_name=s.get("service_name", "Unknown"),
                price=float(s.get("price", 0)),
                currency=s.get("currency", "CNY"),
                billing_cycle=s.get("billing_cycle", "monthly"),
                category=s.get("category"),
                next_billing_date=s.get("next_billing_date"),
                status=s.get("status", "active"),
                notes=s.get("notes"),
                created_at=datetime.fromisoformat(s.get("created_at")) if s.get("created_at") else datetime.utcnow(),
                updated_at=datetime.fromisoformat(s.get("updated_at")) if s.get("updated_at") else datetime.utcnow()
            )
            session.add(new_sub)
            subs_count += 1
            
        # --- 迁移对话记录 ---
        conv_count = 0
        from core.database.sqlite_models import Conversation
        
        # JSON结构: { session_id: [ { message_data } ] }
        for session_id, history_list in conversations_data.items():
            for msg in history_list:
                msg_id = msg.get("id")
                # 为避免ID冲突，如果之前没有存ID则生成一个
                if not msg_id:
                    msg_id = str(uuid.uuid4())
                    
                existing = session.query(Conversation).filter(Conversation.id == msg_id).first()
                if existing:
                    continue
                    
                new_conv = Conversation(
                    id=msg_id,
                    user_id=msg.get("user_id", "unknown_user"),
                    session_id=session_id,
                    message=msg.get("message", ""),
                    response=msg.get("response", ""),
                    intent=msg.get("intent"),
                    confidence=msg.get("confidence"),
                    created_at=datetime.fromisoformat(msg.get("timestamp")) if msg.get("timestamp") else datetime.utcnow()
                )
                session.add(new_conv)
                conv_count += 1

        print("正在提交事务...")
        session.commit()
    
    print(f"迁移完成！成功插入: {users_count} 用户, {subs_count} 订阅, {conv_count} 对话记录。")
    print("现在可以将全局设置中的存储引擎更改为 'sqlite'。")

if __name__ == "__main__":
    migrate_data()
