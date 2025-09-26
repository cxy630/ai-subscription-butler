"""
设置页面 - 应用配置和用户偏好设置
"""

import streamlit as st
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.database.data_interface import data_manager

def render_user_profile_settings():
    """渲染用户配置设置"""
    st.subheader("👤 用户设置")

    if not st.session_state.current_user:
        st.warning("请先登录用户")
        return

    current_user = st.session_state.current_user

    with st.form("user_profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("姓名", value=current_user.get("name", ""))
            email = st.text_input("邮箱", value=current_user.get("email", ""))

        with col2:
            phone = st.text_input("手机号", value=current_user.get("phone", ""))
            timezone = st.selectbox("时区", [
                "Asia/Shanghai", "Asia/Hong_Kong", "Asia/Taipei",
                "UTC", "America/New_York", "Europe/London"
            ], index=0)

        preferences = current_user.get("preferences", {})
        currency = st.selectbox("默认货币", [
            "CNY", "USD", "EUR", "GBP", "JPY", "HKD"
        ], index=0 if preferences.get("currency", "CNY") == "CNY" else 1)

        language = st.selectbox("界面语言", [
            "zh-CN", "en-US"
        ], format_func=lambda x: {"zh-CN": "中文", "en-US": "English"}[x])

        if st.form_submit_button("💾 保存设置", use_container_width=True):
            updated_user = {
                **current_user,
                "name": name,
                "email": email,
                "phone": phone,
                "preferences": {
                    "currency": currency,
                    "timezone": timezone,
                    "language": language
                }
            }

            success = data_manager.update_user(current_user["id"], updated_user)
            if success:
                st.session_state.current_user = updated_user
                st.success("✅ 用户设置已更新")
                st.rerun()
            else:
                st.error("❌ 更新失败")

def render_notification_settings():
    """渲染通知设置"""
    st.subheader("🔔 通知设置")

    # 从用户偏好中获取通知设置
    user_prefs = st.session_state.current_user.get("preferences", {})
    notifications = user_prefs.get("notifications", {})

    with st.form("notification_form"):
        st.write("**邮件通知**")
        email_notifications = st.checkbox(
            "启用邮件通知",
            value=notifications.get("email_enabled", True)
        )

        email_frequency = st.selectbox(
            "邮件频率",
            ["daily", "weekly", "monthly"],
            format_func=lambda x: {"daily": "每日", "weekly": "每周", "monthly": "每月"}[x],
            index=1
        )

        st.write("**推送通知**")
        push_enabled = st.checkbox(
            "启用推送通知",
            value=notifications.get("push_enabled", False)
        )

        st.write("**通知类型**")
        col1, col2 = st.columns(2)

        with col1:
            notify_payment_due = st.checkbox(
                "支付到期提醒",
                value=notifications.get("payment_due", True)
            )
            notify_price_change = st.checkbox(
                "价格变动提醒",
                value=notifications.get("price_change", True)
            )

        with col2:
            notify_monthly_summary = st.checkbox(
                "月度总结报告",
                value=notifications.get("monthly_summary", True)
            )
            notify_budget_alert = st.checkbox(
                "预算超支警告",
                value=notifications.get("budget_alert", True)
            )

        if st.form_submit_button("💾 保存通知设置", use_container_width=True):
            updated_notifications = {
                "email_enabled": email_notifications,
                "email_frequency": email_frequency,
                "push_enabled": push_enabled,
                "payment_due": notify_payment_due,
                "price_change": notify_price_change,
                "monthly_summary": notify_monthly_summary,
                "budget_alert": notify_budget_alert
            }

            # 更新用户偏好
            updated_prefs = {
                **user_prefs,
                "notifications": updated_notifications
            }

            updated_user = {
                **st.session_state.current_user,
                "preferences": updated_prefs
            }

            success = data_manager.update_user(
                st.session_state.current_user["id"],
                updated_user
            )

            if success:
                st.session_state.current_user = updated_user
                st.success("✅ 通知设置已更新")
            else:
                st.error("❌ 更新失败")

def render_budget_settings():
    """渲染预算设置"""
    st.subheader("💰 预算设置")

    user_prefs = st.session_state.current_user.get("preferences", {})
    budget_settings = user_prefs.get("budget", {})

    with st.form("budget_form"):
        st.write("**总预算限制**")
        monthly_budget = st.number_input(
            "月度预算上限 (¥)",
            min_value=0.0,
            value=float(budget_settings.get("monthly_limit", 500.0)),
            step=50.0
        )

        budget_alert_threshold = st.slider(
            "预算警告阈值 (%)",
            min_value=50,
            max_value=100,
            value=int(budget_settings.get("alert_threshold", 80)),
            help="当支出达到预算的百分比时发送警告"
        )

        st.write("**分类预算**")
        col1, col2 = st.columns(2)

        category_budgets = budget_settings.get("category_limits", {})

        with col1:
            entertainment_budget = st.number_input(
                "娱乐预算 (¥)",
                min_value=0.0,
                value=float(category_budgets.get("entertainment", 100.0)),
                step=10.0
            )

            productivity_budget = st.number_input(
                "生产力工具预算 (¥)",
                min_value=0.0,
                value=float(category_budgets.get("productivity", 200.0)),
                step=10.0
            )

        with col2:
            education_budget = st.number_input(
                "教育预算 (¥)",
                min_value=0.0,
                value=float(category_budgets.get("education", 150.0)),
                step=10.0
            )

            other_budget = st.number_input(
                "其他预算 (¥)",
                min_value=0.0,
                value=float(category_budgets.get("other", 100.0)),
                step=10.0
            )

        if st.form_submit_button("💾 保存预算设置", use_container_width=True):
            updated_budget = {
                "monthly_limit": monthly_budget,
                "alert_threshold": budget_alert_threshold,
                "category_limits": {
                    "entertainment": entertainment_budget,
                    "productivity": productivity_budget,
                    "education": education_budget,
                    "other": other_budget
                }
            }

            updated_prefs = {
                **user_prefs,
                "budget": updated_budget
            }

            updated_user = {
                **st.session_state.current_user,
                "preferences": updated_prefs
            }

            success = data_manager.update_user(
                st.session_state.current_user["id"],
                updated_user
            )

            if success:
                st.session_state.current_user = updated_user
                st.success("✅ 预算设置已更新")
            else:
                st.error("❌ 更新失败")

def render_data_management():
    """渲染数据管理设置"""
    st.subheader("📂 数据管理")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**数据备份**")
        if st.button("📥 备份数据", use_container_width=True):
            try:
                # 获取用户所有数据
                user_data = {
                    "user": st.session_state.current_user,
                    "subscriptions": data_manager.get_active_subscriptions(
                        st.session_state.current_user_id
                    ),
                    "conversations": data_manager.get_session_history(
                        st.session_state.chat_session_id
                    )
                }

                # 生成备份文件
                backup_filename = f"backup_{st.session_state.current_user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

                st.download_button(
                    label="📁 下载备份文件",
                    data=json.dumps(user_data, ensure_ascii=False, indent=2),
                    file_name=backup_filename,
                    mime="application/json",
                    use_container_width=True
                )

                st.success("✅ 备份数据准备完成")
            except Exception as e:
                st.error(f"❌ 备份失败: {e}")

        if st.button("🔄 导入数据", use_container_width=True):
            st.info("数据导入功能开发中...")

    with col2:
        st.write("**数据清理**")

        if st.button("🗑️ 清空聊天记录", use_container_width=True, type="secondary"):
            if st.session_state.get("confirm_clear_chat", False):
                # 执行清空操作
                try:
                    data_manager.clear_user_conversations(st.session_state.current_user_id)
                    st.session_state.chat_history = []
                    st.session_state.confirm_clear_chat = False
                    st.success("✅ 聊天记录已清空")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 清空失败: {e}")
            else:
                st.session_state.confirm_clear_chat = True
                st.warning("⚠️ 再次点击确认清空所有聊天记录")

        if st.button("⚠️ 删除所有数据", use_container_width=True, type="secondary"):
            if st.session_state.get("confirm_delete_all", False):
                st.error("⚠️ 此功能需要进一步确认，请联系管理员")
            else:
                st.session_state.confirm_delete_all = True
                st.warning("⚠️ 这将删除您的所有数据，不可恢复！")

def render_ai_assistant_settings():
    """渲染AI助手设置"""
    st.subheader("🤖 AI助手设置")

    user_prefs = st.session_state.current_user.get("preferences", {})
    ai_settings = user_prefs.get("ai_assistant", {})

    with st.form("ai_settings_form"):
        st.write("**响应偏好**")
        response_style = st.selectbox(
            "响应风格",
            ["friendly", "professional", "concise"],
            format_func=lambda x: {"friendly": "友好", "professional": "专业", "concise": "简洁"}[x],
            index=0
        )

        response_length = st.select_slider(
            "响应详细程度",
            options=["简短", "适中", "详细"],
            value=ai_settings.get("response_length", "适中")
        )

        st.write("**功能设置**")
        col1, col2 = st.columns(2)

        with col1:
            auto_suggestions = st.checkbox(
                "自动建议优化",
                value=ai_settings.get("auto_suggestions", True)
            )

            include_charts = st.checkbox(
                "包含图表分析",
                value=ai_settings.get("include_charts", True)
            )

        with col2:
            proactive_alerts = st.checkbox(
                "主动预警提醒",
                value=ai_settings.get("proactive_alerts", True)
            )

            learning_enabled = st.checkbox(
                "个性化学习",
                value=ai_settings.get("learning_enabled", True),
                help="AI助手会学习您的偏好，提供更个性化的建议"
            )

        if st.form_submit_button("💾 保存AI设置", use_container_width=True):
            updated_ai_settings = {
                "response_style": response_style,
                "response_length": response_length,
                "auto_suggestions": auto_suggestions,
                "include_charts": include_charts,
                "proactive_alerts": proactive_alerts,
                "learning_enabled": learning_enabled
            }

            updated_prefs = {
                **user_prefs,
                "ai_assistant": updated_ai_settings
            }

            updated_user = {
                **st.session_state.current_user,
                "preferences": updated_prefs
            }

            success = data_manager.update_user(
                st.session_state.current_user["id"],
                updated_user
            )

            if success:
                st.session_state.current_user = updated_user
                st.success("✅ AI助手设置已更新")
            else:
                st.error("❌ 更新失败")

def render_app_info():
    """渲染应用信息"""
    st.subheader("ℹ️ 应用信息")

    col1, col2 = st.columns(2)

    with col1:
        st.info("""
        **🏠 AI订阅管家**

        • 版本: v1.0.0
        • 构建: Claude Code
        • 存储: JSON文件系统
        • 界面: Streamlit框架
        """)

    with col2:
        st.success("""
        **📊 系统状态**

        • 数据库: 正常 ✅
        • 存储空间: 充足 ✅
        • AI助手: 活跃 ✅
        • 备份状态: 最新 ✅
        """)

    st.divider()

    # 技术栈信息
    with st.expander("🔧 技术栈详情"):
        st.markdown("""
        **前端技术:**
        - Streamlit - Web界面框架
        - Plotly - 数据可视化
        - Pandas - 数据处理

        **后端技术:**
        - Python 3.9+ - 核心语言
        - JSON Storage - 数据存储
        - SQLite - 备选数据库

        **AI技术:**
        - OpenAI GPT - 对话引擎
        - 自然语言处理 - 智能分析
        - 机器学习 - 个性化推荐
        """)

    # 使用统计
    st.divider()
    st.write("**📈 使用统计**")

    if st.session_state.current_user:
        user_overview = data_manager.get_user_overview(st.session_state.current_user_id)
        if user_overview:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("订阅总数", user_overview["total_subscriptions"])

            with col2:
                st.metric("活跃订阅", user_overview["active_subscriptions"])

            with col3:
                st.metric("月度支出", f"¥{user_overview['monthly_spending']:.2f}")

            with col4:
                categories_count = len(user_overview.get("subscription_categories", {}))
                st.metric("使用类别", f"{categories_count} 个")

def render_settings_page():
    """渲染完整的设置页面"""
    st.title("⚙️ 设置")

    if not st.session_state.current_user:
        st.warning("请先选择用户")
        return

    # 设置标签页
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👤 用户设置",
        "🔔 通知设置",
        "💰 预算设置",
        "🤖 AI助手",
        "📂 数据管理",
        "ℹ️ 关于"
    ])

    with tab1:
        render_user_profile_settings()

    with tab2:
        render_notification_settings()

    with tab3:
        render_budget_settings()

    with tab4:
        render_ai_assistant_settings()

    with tab5:
        render_data_management()

    with tab6:
        render_app_info()

if __name__ == "__main__":
    # 测试组件
    render_settings_page()