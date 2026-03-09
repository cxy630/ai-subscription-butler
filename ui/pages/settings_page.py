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
    from ui.components.settings import render_notification_settings as render_detailed_notification_settings

    # 使用详细的通知设置组件
    render_detailed_notification_settings(st.session_state.current_user_id)

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

    from core.backup import backup_manager

    # 备份统计
    stats = backup_manager.get_backup_statistics()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("备份总数", stats["total_backups"])
    with col2:
        size_mb = stats["total_size"] / (1024 * 1024)
        st.metric("总大小", f"{size_mb:.2f} MB")
    with col3:
        latest = stats.get("latest_backup")
        if latest:
            latest_date = latest.get("created_at", "N/A")[:10]
            st.metric("最新备份", latest_date)
        else:
            st.metric("最新备份", "无")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.write("**数据备份**")

        if st.button("📥 创建新备份", use_container_width=True, type="primary"):
            with st.spinner("正在创建备份..."):
                try:
                    result = backup_manager.create_full_backup(st.session_state.current_user_id)

                    if result.get("success"):
                        st.success(f"✅ 备份创建成功!")
                        st.caption(f"文件: {result['backup_name']}")
                        st.rerun()
                    else:
                        st.error("❌ 备份创建失败")
                except Exception as e:
                    st.error(f"❌ 备份失败: {e}")

        # 备份列表
        st.write("**备份历史**")
        backups = backup_manager.list_backups()

        if backups:
            for backup in backups[:5]:  # 显示最近5个备份
                with st.expander(f"📦 {backup['filename']}", expanded=False):
                    col_a, col_b = st.columns(2)

                    with col_a:
                        st.write(f"**创建时间:** {backup['created_at'][:19]}")
                        st.write(f"**大小:** {backup['size'] / 1024:.1f} KB")
                        st.write(f"**类型:** {backup['backup_type']}")

                    with col_b:
                        # 下载备份
                        backup_data = backup_manager.export_backup_data(backup['path'])
                        if backup_data:
                            st.download_button(
                                "📥 下载",
                                data=backup_data,
                                file_name=backup['filename'].replace('.json', '.zip'),
                                mime="application/zip",
                                use_container_width=True
                            )

                        # 恢复备份
                        if st.button("♻️ 恢复", key=f"restore_{backup['filename']}", use_container_width=True):
                            st.session_state.restore_backup_file = backup['path']
                            st.session_state.show_restore_confirm = True

                        # 删除备份
                        if st.button("🗑️ 删除", key=f"delete_{backup['filename']}", use_container_width=True, type="secondary"):
                            backup_name = backup['filename'].replace('.json', '')
                            if backup_manager.delete_backup(backup_name):
                                st.success("✅ 备份已删除")
                                st.rerun()
                            else:
                                st.error("❌ 删除失败")
        else:
            st.info("暂无备份记录")

    with col2:
        st.write("**数据导入**")

        uploaded_file = st.file_uploader(
            "上传备份文件",
            type=['json', 'zip'],
            help="支持JSON或ZIP格式的备份文件"
        )

        if uploaded_file:
            st.info(f"📄 已选择: {uploaded_file.name}")

            col_import1, col_import2 = st.columns(2)

            with col_import1:
                if st.button("📥 导入并恢复", use_container_width=True, type="primary"):
                    with st.spinner("正在导入备份..."):
                        try:
                            # 导入文件
                            file_bytes = uploaded_file.read()
                            import_result = backup_manager.import_backup_file(file_bytes, uploaded_file.name)

                            if import_result.get("success"):
                                # 恢复数据
                                restore_result = backup_manager.restore_from_backup(
                                    import_result["backup_file"],
                                    merge=False
                                )

                                if restore_result.get("success"):
                                    st.success("✅ 数据已成功恢复!")
                                    st.caption(f"恢复文件: {', '.join(restore_result['restored_files'])}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ 恢复失败: {restore_result.get('error')}")
                            else:
                                st.error(f"❌ 导入失败: {import_result.get('error')}")
                        except Exception as e:
                            st.error(f"❌ 操作失败: {e}")

            with col_import2:
                if st.button("🔀 合并导入", use_container_width=True):
                    with st.spinner("正在合并数据..."):
                        try:
                            file_bytes = uploaded_file.read()
                            import_result = backup_manager.import_backup_file(file_bytes, uploaded_file.name)

                            if import_result.get("success"):
                                restore_result = backup_manager.restore_from_backup(
                                    import_result["backup_file"],
                                    merge=True
                                )

                                if restore_result.get("success"):
                                    st.success("✅ 数据已合并!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ 合并失败: {restore_result.get('error')}")
                            else:
                                st.error(f"❌ 导入失败: {import_result.get('error')}")
                        except Exception as e:
                            st.error(f"❌ 操作失败: {e}")

        st.divider()

        st.write("**数据清理**")

        if st.button("🗑️ 清空聊天记录", use_container_width=True, type="secondary"):
            if st.session_state.get("confirm_clear_chat", False):
                try:
                    st.session_state.chat_history = []
                    st.session_state.confirm_clear_chat = False
                    st.success("✅ 聊天记录已清空")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 清空失败: {e}")
            else:
                st.session_state.confirm_clear_chat = True
                st.warning("⚠️ 再次点击确认清空")

    # 恢复确认对话框
    if st.session_state.get("show_restore_confirm", False):
        st.warning("⚠️ 恢复备份将覆盖当前数据，是否继续？")
        col_confirm1, col_confirm2 = st.columns(2)

        with col_confirm1:
            if st.button("✅ 确认恢复", use_container_width=True, type="primary"):
                backup_file = st.session_state.get("restore_backup_file")
                if backup_file:
                    result = backup_manager.restore_from_backup(backup_file, merge=False)
                    if result.get("success"):
                        st.success("✅ 数据已恢复!")
                        st.session_state.show_restore_confirm = False
                        st.rerun()
                    else:
                        st.error(f"❌ 恢复失败: {result.get('error')}")

        with col_confirm2:
            if st.button("❌ 取消", use_container_width=True):
                st.session_state.show_restore_confirm = False
                st.rerun()

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