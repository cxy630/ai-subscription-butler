"""
JSON → SQLite 数据迁移脚本
将现有 JSON 文件中的数据导入 SQLite 数据库
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')


def load_json(path: Path) -> list:
    """加载 JSON 文件，失败返回空列表"""
    if not path.exists():
        print(f"  [跳过] 文件不存在: {path}")
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"  [错误] 读取 {path} 失败: {e}")
        return []


def migrate():
    from core.database.sqlite_models import SQLiteDataManager, _SUBSCRIPTION_FIELDS

    data_dir = project_root / 'data'
    db_path = data_dir / 'subscriptions.db'

    print(f"\n=== JSON → SQLite 数据迁移 ===")
    print(f"数据目录: {data_dir}")
    print(f"目标数据库: {db_path}\n")

    manager = SQLiteDataManager()

    # ──────────────────────────────
    # 1. 迁移用户
    # ──────────────────────────────
    users_json = load_json(data_dir / 'users.json')
    user_id_map: dict[str, str] = {}  # old_id → new_id（通常相同）

    print(f"[用户] 共找到 {len(users_json)} 条记录")
    migrated_users = 0
    for u in users_json:
        old_id = u.get('id')
        email = u.get('email', '')
        name = u.get('name', '')

        if not email:
            print(f"  [跳过] 用户缺少 email: {u}")
            continue

        # 检查是否已存在
        existing = manager.get_user_by_email(email)
        if existing:
            print(f"  [已存在] {email} (id={existing.id})")
            user_id_map[old_id] = existing.id
            continue

        # 使用原始密码哈希（迁移时保留，默认给一个占位哈希）
        password_hash = u.get('password_hash', '$2b$12$placeholder_migrate')

        # 直接在数据库中插入，保留原始 id
        with manager.get_session() as db:
            from core.database.sqlite_models import User
            user_obj = User(
                id=old_id or __import__('uuid').uuid4().__str__(),
                email=email,
                password_hash=password_hash,
                name=name,
                is_active=u.get('is_active', True),
                is_verified=u.get('is_verified', False),
                subscription_tier=u.get('subscription_tier', 'free'),
            )
            # 恢复时间戳
            if u.get('created_at'):
                try:
                    user_obj.created_at = datetime.fromisoformat(u['created_at'])
                except ValueError:
                    pass
            if u.get('updated_at'):
                try:
                    user_obj.updated_at = datetime.fromisoformat(u['updated_at'])
                except ValueError:
                    pass

            db.add(user_obj)
            db.commit()

        user_id_map[old_id] = old_id
        migrated_users += 1
        print(f"  [迁移] {email} (id={old_id})")

    print(f"  → 新迁移: {migrated_users} 条\n")

    # ──────────────────────────────
    # 2. 迁移订阅
    # ──────────────────────────────
    subs_json = load_json(data_dir / 'subscriptions.json')
    print(f"[订阅] 共找到 {len(subs_json)} 条记录")
    migrated_subs = 0
    skipped_subs = 0

    with manager.get_session() as db:
        from core.database.sqlite_models import Subscription

        existing_ids = {row.id for row in db.query(Subscription.id).all()}

        for s in subs_json:
            sub_id = s.get('id')
            user_id = s.get('user_id')

            if sub_id in existing_ids:
                print(f"  [已存在] {s.get('service_name')} (id={sub_id})")
                skipped_subs += 1
                continue

            if not user_id:
                print(f"  [跳过] 订阅缺少 user_id: {s}")
                skipped_subs += 1
                continue

            # 只保留模型允许的字段，但单独处理 id / user_id / created_at / updated_at
            filtered = {k: v for k, v in s.items() if k in _SUBSCRIPTION_FIELDS}

            sub_obj = Subscription(
                id=sub_id or __import__('uuid').uuid4().__str__(),
                user_id=user_id,
                **filtered
            )

            if s.get('created_at'):
                try:
                    sub_obj.created_at = datetime.fromisoformat(s['created_at'])
                except ValueError:
                    pass
            if s.get('updated_at'):
                try:
                    sub_obj.updated_at = datetime.fromisoformat(s['updated_at'])
                except ValueError:
                    pass

            db.add(sub_obj)
            migrated_subs += 1
            print(f"  [迁移] {s.get('service_name')} (user={user_id[:8]}...)")

        db.commit()

    print(f"  → 新迁移: {migrated_subs} 条，跳过: {skipped_subs} 条\n")

    # ──────────────────────────────
    # 3. 迁移对话历史
    # ──────────────────────────────
    convs_json = load_json(data_dir / 'conversations.json')
    print(f"[对话] 共找到 {len(convs_json)} 条记录")
    migrated_convs = 0

    with manager.get_session() as db:
        from core.database.sqlite_models import Conversation

        existing_conv_ids = {row.id for row in db.query(Conversation.id).all()}

        for c in convs_json:
            conv_id = c.get('id')
            if conv_id in existing_conv_ids:
                continue

            conv_obj = Conversation(
                id=conv_id or __import__('uuid').uuid4().__str__(),
                user_id=c.get('user_id', ''),
                session_id=c.get('session_id', ''),
                message=c.get('message', ''),
                response=c.get('response', ''),
                intent=c.get('intent'),
                confidence=c.get('confidence'),
            )

            if c.get('created_at'):
                try:
                    conv_obj.created_at = datetime.fromisoformat(c['created_at'])
                except ValueError:
                    pass

            db.add(conv_obj)
            migrated_convs += 1

        db.commit()

    print(f"  → 新迁移: {migrated_convs} 条\n")

    # ──────────────────────────────
    # 4. 验证
    # ──────────────────────────────
    print("=== 迁移验证 ===")
    with manager.get_session() as db:
        from core.database.sqlite_models import User, Subscription, Conversation
        n_users = db.query(User).count()
        n_subs = db.query(Subscription).count()
        n_convs = db.query(Conversation).count()

    print(f"  用户数:    {n_users}")
    print(f"  订阅数:    {n_subs}")
    print(f"  对话记录:  {n_convs}")
    print("\n✅ 迁移完成！")
    return True


if __name__ == "__main__":
    migrate()
