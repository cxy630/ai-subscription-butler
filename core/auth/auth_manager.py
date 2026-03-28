"""
用户认证管理器
提供密码哈希、注册、登录功能
"""

import bcrypt
from typing import Optional, Dict, Any
from core.database.data_interface import data_manager


def hash_password(password: str) -> str:
    """对密码进行 bcrypt 哈希"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码是否匹配哈希值"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def register_user(email: str, password: str, name: str = None) -> Dict[str, Any]:
    """
    注册新用户
    返回 {"success": True, "user": {...}} 或 {"success": False, "error": "..."}
    """
    email = email.strip().lower()

    if not email or '@' not in email:
        return {"success": False, "error": "邮箱格式不正确"}

    if len(password) < 6:
        return {"success": False, "error": "密码长度至少 6 位"}

    # 检查邮箱是否已存在
    existing = data_manager.get_user_by_email(email)
    if existing:
        return {"success": False, "error": "该邮箱已被注册"}

    password_hash = hash_password(password)
    display_name = name.strip() if name and name.strip() else email.split('@')[0]

    user = data_manager.create_user(email, password_hash, display_name)
    if not user:
        return {"success": False, "error": "注册失败，请重试"}

    return {"success": True, "user": user}


def login_user(email: str, password: str) -> Dict[str, Any]:
    """
    用户登录
    返回 {"success": True, "user": {...}} 或 {"success": False, "error": "..."}
    """
    email = email.strip().lower()

    if not email or not password:
        return {"success": False, "error": "请填写邮箱和密码"}

    user = data_manager.get_user_by_email(email)
    if not user:
        return {"success": False, "error": "邮箱或密码错误"}

    password_hash = user.get("password_hash", "")

    # 兼容迁移数据中的占位哈希（包含 placeholder 字样则直接拒绝）
    if "placeholder" in password_hash or "sample_hash" in password_hash:
        # 迁移来的旧账号：要求用户重置密码（此处简单返回提示）
        return {"success": False, "error": "该账号是迁移账号，请先通过注册重新创建账号"}

    if not verify_password(password, password_hash):
        return {"success": False, "error": "邮箱或密码错误"}

    if not user.get("is_active", True):
        return {"success": False, "error": "账号已被禁用"}

    return {"success": True, "user": user}
