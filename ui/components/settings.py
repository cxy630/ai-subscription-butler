"""
设置页面组件 - 用户偏好和通知设置
"""

import streamlit as st
from core.database.data_interface import data_manager
from datetime import time


def get_default_preferences():
    """获取默认通知偏好"""
    return {
        "enabled": True,
        "reminder_days": [7, 3, 1],
        "notification_time": "09:00",
        "channels": {
            "email": True,
            "in_app": True,
            "push": False
        },
        "notify_on_renewal": True,
        "notify_on_price_change": True,
        "weekly_summary": True,
        "summary_day": "monday"
    }


def render_notification_settings(user_id: str):
    """渲染通知设置界面"""
    st.header("⚙️ 通知设置")

    # 获取用户当前设置
    user = data_manager.get_user_by_id(user_id)
    if not user:
        st.error("❌ 未找到用户信息")
        return

    # 获取或初始化通知偏好
    preferences = user.get("notification_preferences", get_default_preferences())

    # 通知总开关
    st.subheader("🔔 通知总开关")
    enabled = st.toggle(
        "启用通知",
        value=preferences.get("enabled", True),
        help="关闭后将不会收到任何通知"
    )

    if enabled:
        # 提醒时间设置
        st.subheader("⏰ 提醒时间")
        col1, col2 = st.columns(2)

        with col1:
            # 解析当前时间
            current_time = preferences.get("notification_time", "09:00")
            hour, minute = map(int, current_time.split(":"))

            notification_time = st.time_input(
                "每日通知时间",
                value=time(hour, minute),
                help="设置每天发送通知的时间"
            )

        with col2:
            # 提醒天数
            reminder_days = preferences.get("reminder_days", [7, 3, 1])

            st.write("提前几天提醒")
            col_7d, col_3d, col_1d = st.columns(3)

            with col_7d:
                remind_7d = st.checkbox("7天前", value=7 in reminder_days)
            with col_3d:
                remind_3d = st.checkbox("3天前", value=3 in reminder_days)
            with col_1d:
                remind_1d = st.checkbox("1天前", value=1 in reminder_days)

        # 通知渠道
        st.subheader("📢 通知渠道")
        channels = preferences.get("channels", {})

        col1, col2, col3 = st.columns(3)

        with col1:
            email_enabled = st.checkbox(
                "📧 邮件通知",
                value=channels.get("email", True),
                help="通过邮件发送通知"
            )

        with col2:
            in_app_enabled = st.checkbox(
                "🔔 应用内通知",
                value=channels.get("in_app", True),
                help="在应用内显示通知"
            )

        with col3:
            push_enabled = st.checkbox(
                "📱 推送通知",
                value=channels.get("push", False),
                help="发送系统推送通知（需要授权）"
            )

        # 通知类型
        st.subheader("📋 通知类型")

        col1, col2 = st.columns(2)

        with col1:
            notify_renewal = st.checkbox(
                "续费提醒",
                value=preferences.get("notify_on_renewal", True),
                help="订阅即将续费时提醒"
            )

            notify_price = st.checkbox(
                "价格变动提醒",
                value=preferences.get("notify_on_price_change", True),
                help="订阅价格发生变化时提醒"
            )

        with col2:
            weekly_summary = st.checkbox(
                "每周摘要",
                value=preferences.get("weekly_summary", True),
                help="每周发送订阅支出摘要"
            )

            if weekly_summary:
                summary_day = st.selectbox(
                    "摘要发送日",
                    options=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
                    format_func=lambda x: {
                        "monday": "周一", "tuesday": "周二", "wednesday": "周三",
                        "thursday": "周四", "friday": "周五", "saturday": "周六", "sunday": "周日"
                    }[x],
                    index=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(
                        preferences.get("summary_day", "monday")
                    )
                )
            else:
                summary_day = preferences.get("summary_day", "monday")

        # 保存按钮
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("💾 保存设置", use_container_width=True, type="primary"):
                # 构建新的reminder_days列表
                new_reminder_days = []
                if remind_7d:
                    new_reminder_days.append(7)
                if remind_3d:
                    new_reminder_days.append(3)
                if remind_1d:
                    new_reminder_days.append(1)

                # 构建新的偏好设置
                new_preferences = {
                    "enabled": enabled,
                    "reminder_days": sorted(new_reminder_days, reverse=True),
                    "notification_time": notification_time.strftime("%H:%M"),
                    "channels": {
                        "email": email_enabled,
                        "in_app": in_app_enabled,
                        "push": push_enabled
                    },
                    "notify_on_renewal": notify_renewal,
                    "notify_on_price_change": notify_price,
                    "weekly_summary": weekly_summary,
                    "summary_day": summary_day
                }

                # 更新用户设置
                success = data_manager.update_user(user_id, {
                    "notification_preferences": new_preferences
                })

                if success:
                    st.success("✅ 设置已保存")
                    st.rerun()
                else:
                    st.error("❌ 保存失败，请重试")

        with col2:
            if st.button("🔄 恢复默认", use_container_width=True):
                default_prefs = get_default_preferences()
                success = data_manager.update_user(user_id, {
                    "notification_preferences": default_prefs
                })

                if success:
                    st.success("✅ 已恢复默认设置")
                    st.rerun()
                else:
                    st.error("❌ 操作失败，请重试")

    else:
        # 通知已关闭
        st.info("ℹ️ 通知功能已关闭")

        if st.button("💾 保存设置", type="primary"):
            # 只更新enabled状态
            current_prefs = preferences.copy()
            current_prefs["enabled"] = False

            success = data_manager.update_user(user_id, {
                "notification_preferences": current_prefs
            })

            if success:
                st.success("✅ 设置已保存")
                st.rerun()
            else:
                st.error("❌ 保存失败，请重试")


def render_user_profile(user_id: str):
    """渲染用户资料设置"""
    st.header("👤 个人资料")

    user = data_manager.get_user_by_id(user_id)
    if not user:
        st.error("❌ 未找到用户信息")
        return

    with st.form("profile_form"):
        name = st.text_input("用户名", value=user.get("name", ""))
        email = st.text_input("邮箱", value=user.get("email", ""), disabled=True)

        st.caption("💡 邮箱地址不可修改")

        submitted = st.form_submit_button("💾 保存", use_container_width=True, type="primary")

        if submitted:
            if not name:
                st.error("❌ 用户名不能为空")
            else:
                success = data_manager.update_user(user_id, {"name": name})

                if success:
                    st.success("✅ 资料已更新")
                    st.rerun()
                else:
                    st.error("❌ 更新失败，请重试")


def render_settings_page(user_id: str):
    """渲染设置页面"""
    st.title("⚙️ 设置")

    # 选项卡
    tab1, tab2, tab3 = st.tabs(["👤 个人资料", "🔔 通知设置", "ℹ️ 关于"])

    with tab1:
        render_user_profile(user_id)

    with tab2:
        render_notification_settings(user_id)

    with tab3:
        st.header("ℹ️ 关于")
        st.markdown("""
        ### AI订阅管家 v1.0

        一个智能的订阅服务管理工具，帮助您：
        - 📊 追踪所有订阅服务
        - 💰 管理订阅支出
        - 🔔 及时续费提醒
        - 🤖 AI智能助手
        - 📸 OCR快速录入

        ---

        **技术栈**
        - Python 3.12 + Streamlit
        - Google Gemini 2.5 Flash Lite
        - JSON/SQLite 存储

        **开源协议**: MIT License

        **版本**: 1.0.0 (2025-09-30)
        """)

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.metric("当前存储后端", "JSON")

        with col2:
            user = data_manager.get_user_by_id(user_id)
            tier = user.get("subscription_tier", "free")
            st.metric("订阅等级", tier.upper())


if __name__ == "__main__":
    # 测试设置页面
    st.set_page_config(page_title="设置", page_icon="⚙️", layout="wide")
    render_settings_page("d2389f2e-4276-46d2-8843-c7d63602315a")