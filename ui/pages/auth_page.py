"""
用户登录 / 注册页面
使用 Streamlit session_state 管理登录状态，支持多用户数据隔离
"""

import streamlit as st
from core.auth.auth_manager import login_user, register_user


def render_auth_page():
    """渲染登录/注册页面，返回 True 表示已登录"""
    st.title("💳 AI 订阅管家")
    st.caption("智能管理你的所有订阅服务")

    tab_login, tab_register = st.tabs(["🔑 登录", "📝 注册"])

    # ── 登录 ──────────────────────────────
    with tab_login:
        with st.form("login_form"):
            st.subheader("欢迎回来")
            email = st.text_input("邮箱", placeholder="you@example.com")
            password = st.text_input("密码", type="password", placeholder="请输入密码")
            submitted = st.form_submit_button("登录", use_container_width=True, type="primary")

        if submitted:
            if not email or not password:
                st.error("请填写邮箱和密码")
            else:
                result = login_user(email, password)
                if result["success"]:
                    user = result["user"]
                    st.session_state.current_user_id = user["id"]
                    st.session_state.current_user = user
                    st.session_state.authenticated = True
                    st.success(f"欢迎回来，{user.get('name', user['email'])}！")
                    st.rerun()
                else:
                    st.error(result["error"])

    # ── 注册 ──────────────────────────────
    with tab_register:
        with st.form("register_form"):
            st.subheader("创建新账号")
            reg_name = st.text_input("昵称（可选）", placeholder="你的名字")
            reg_email = st.text_input("邮箱", placeholder="you@example.com", key="reg_email")
            reg_password = st.text_input("密码（至少6位）", type="password", key="reg_password")
            reg_password2 = st.text_input("确认密码", type="password", key="reg_password2")
            reg_submitted = st.form_submit_button("注册", use_container_width=True, type="primary")

        if reg_submitted:
            if not reg_email or not reg_password:
                st.error("请填写邮箱和密码")
            elif reg_password != reg_password2:
                st.error("两次密码不一致")
            else:
                result = register_user(reg_email, reg_password, reg_name or None)
                if result["success"]:
                    user = result["user"]
                    st.session_state.current_user_id = user["id"]
                    st.session_state.current_user = user
                    st.session_state.authenticated = True
                    st.success(f"注册成功！欢迎，{user.get('name', user['email'])}！")
                    st.rerun()
                else:
                    st.error(result["error"])
