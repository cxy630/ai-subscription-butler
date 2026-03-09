"""
自动化设置页面 - 配置AI管家自动化规则和偏好
"""

import streamlit as st
from datetime import datetime
from core.database.data_interface import data_manager
from core.agents.rules_engine import rules_engine
from core.services.daily_checkup_scheduler import daily_checkup_scheduler


def render_automation_settings_page():
    """渲染自动化设置页面"""
    st.title("🤖 AI管家自动化设置")

    st.markdown("""
    配置AI订阅管家的自动化级别和规则，让管家代替您管理订阅。
    """)

    # 获取用户数据
    user = data_manager.get_user_by_id(st.session_state.current_user_id)
    if not user:
        st.error("❌ 无法加载用户数据")
        return

    automation_prefs = user.get("automation_preferences", {
        "automation_level": "manual",
        "budget_limit": None,
        "enabled_rules": [],
        "auto_pause_unused": False,
        "unused_days_threshold": 30,
        "require_approval_for": [],
        "enable_auto_checkup": True,
        "checkup_time": "09:00"
    })

    st.divider()

    # === 自动化级别设置 ===
    st.subheader("🎚️ 自动化级别")

    automation_level = st.radio(
        "选择自动化级别",
        options=["manual", "semi_auto", "full_auto"],
        index=["manual", "semi_auto", "full_auto"].index(
            automation_prefs.get("automation_level", "manual")
        ),
        format_func=lambda x: {
            "manual": "🔴 手动模式 - 仅通知，所有操作需要您确认",
            "semi_auto": "🟡 半自动模式 - 低风险操作自动执行，高风险操作需确认",
            "full_auto": "🟢 全自动模式 - AI管家完全自主管理订阅"
        }[x],
        help="自动化级别决定了AI管家可以自动执行哪些操作"
    )

    # 自动化级别说明
    level_descriptions = {
        "manual": """
        **手动模式**：最安全的模式
        - ✅ AI管家仅提供通知和建议
        - ✅ 所有操作都需要您的明确确认
        - ✅ 适合刚开始使用的用户
        """,
        "semi_auto": """
        **半自动模式**：平衡安全与便利
        - ✅ 低风险操作自动执行（如发送提醒）
        - ⚠️ 中高风险操作需要确认（如暂停订阅）
        - ✅ 适合希望节省时间的用户
        """,
        "full_auto": """
        **全自动模式**：最大化便利
        - ✅ AI管家完全自主管理订阅
        - ⚠️ 高风险操作也会自动执行（如取消订阅）
        - ⚠️ 建议设置预算限制和审批规则
        - ✅ 适合完全信任AI管家的用户
        """
    }

    st.info(level_descriptions[automation_level])

    st.divider()

    # === 预算设置 ===
    st.subheader("💰 预算限制")

    col1, col2 = st.columns([3, 1])

    with col1:
        budget_enabled = st.checkbox(
            "启用月度预算限制",
            value=automation_prefs.get("budget_limit") is not None,
            help="当订阅总支出超过预算时，AI管家会发出警告"
        )

    with col2:
        if budget_enabled:
            budget_limit = st.number_input(
                "月度预算 (CNY)",
                min_value=0.0,
                value=float(automation_prefs.get("budget_limit") or 500.0),
                step=50.0
            )
        else:
            budget_limit = None

    st.divider()

    # === 自动化规则设置 ===
    st.subheader("⚙️ 自动化规则")

    st.markdown("选择您希望启用的自动化规则：")

    # 获取所有规则
    all_rules = rules_engine.get_all_rules()
    enabled_rules = automation_prefs.get("enabled_rules", [])

    # 规则选择
    rule_selections = {}
    for rule in sorted(all_rules, key=lambda r: r.priority):
        rule_selections[rule.rule_id] = st.checkbox(
            f"**{rule.name}**",
            value=rule.rule_id in enabled_rules,
            help=rule.description,
            key=f"rule_{rule.rule_id}"
        )

        # 显示规则详情
        if rule_selections[rule.rule_id]:
            with st.expander(f"📋 {rule.name} - 规则详情"):
                st.markdown(f"**描述**: {rule.description}")
                st.markdown(f"**优先级**: {rule.priority}")
                st.markdown(f"**执行模式**: {rule.execution_mode.value}")

                # 显示条件
                st.markdown("**触发条件**:")
                for condition in rule.conditions:
                    st.markdown(f"- {condition.condition_type.value}: {condition.parameters}")

                # 显示动作
                st.markdown("**执行动作**:")
                for action in rule.actions:
                    risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
                    st.markdown(
                        f"- {risk_emoji.get(action.risk_level, '⚪')} "
                        f"{action.action_type.value} (风险: {action.risk_level})"
                    )

    st.divider()

    # === 每日检查设置 ===
    st.subheader("📅 每日自动检查")

    col1, col2 = st.columns([3, 1])

    with col1:
        enable_auto_checkup = st.checkbox(
            "启用每日自动检查",
            value=automation_prefs.get("enable_auto_checkup", True),
            help="AI管家将在每天固定时间自动检查您的订阅状态"
        )

    with col2:
        if enable_auto_checkup:
            checkup_time = st.time_input(
                "检查时间",
                value=datetime.strptime(
                    automation_prefs.get("checkup_time", "09:00"), "%H:%M"
                ).time(),
                help="每天执行检查的时间"
            )
            checkup_time_str = checkup_time.strftime("%H:%M")
        else:
            checkup_time_str = "09:00"

    # 显示调度器状态
    scheduler_status = daily_checkup_scheduler.get_status()

    if enable_auto_checkup:
        col1, col2, col3 = st.columns(3)

        with col1:
            status_emoji = "🟢" if scheduler_status["is_running"] else "🔴"
            st.metric("调度器状态", f"{status_emoji} {'运行中' if scheduler_status['is_running'] else '已停止'}")

        with col2:
            if scheduler_status["last_run_time"]:
                last_run = datetime.fromisoformat(scheduler_status["last_run_time"])
                st.metric("上次检查", last_run.strftime("%H:%M"))
            else:
                st.metric("上次检查", "从未运行")

        with col3:
            if scheduler_status["next_run_time"]:
                next_run = datetime.fromisoformat(scheduler_status["next_run_time"])
                st.metric("下周一预定周报", next_run.strftime("%m-%d %H:%M"))
            else:
                st.metric("下次检查", checkup_time_str)

        # 手动触发按钮
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("▶️ 立即执行每日检查", use_container_width=True):
                import asyncio
                with st.spinner("正在执行每日检查..."):
                    result = asyncio.run(
                        daily_checkup_scheduler.run_daily_checkup_for_user(
                            st.session_state.current_user_id
                        )
                    )

                    if result.get("status") == "success":
                        st.success("✅ 每日检查执行完成！")
                        st.session_state.daily_checkup_result = result
                        st.info("💡 检查结果已更新到AI洞察页面")
                    else:
                        st.error(f"❌ 执行失败: {result.get('error', '未知错误')}")
        
        with col_btn2:
            if st.button("📊 立即生成周报", use_container_width=True):
                import asyncio
                with st.spinner("正在生成本周报告..."):
                    result = asyncio.run(
                        daily_checkup_scheduler.run_weekly_report_for_user(
                            st.session_state.current_user_id
                        )
                    )

                    if result.get("status") == "success":
                        st.success("✅ 周报已生成！")
                        st.session_state.last_weekly_report = result
                        st.markdown(f"**本周摘要**: {result.get('summary')}")
                    else:
                        st.error(f"❌ 生成失败: {result.get('error', '未知错误')}")

    st.divider()

    # === 高级设置 ===
    with st.expander("🔧 高级设置"):
        st.markdown("**未使用订阅自动暂停**")

        auto_pause = st.checkbox(
            "启用未使用订阅自动暂停",
            value=automation_prefs.get("auto_pause_unused", False),
            help="长期未使用的订阅将被自动暂停"
        )

        if auto_pause:
            unused_threshold = st.slider(
                "未使用天数阈值",
                min_value=7,
                max_value=90,
                value=automation_prefs.get("unused_days_threshold", 30),
                step=7,
                help="超过此天数未使用的订阅将被标记为可暂停"
            )
        else:
            unused_threshold = 30

        st.markdown("**需要审批的操作类型**")

        require_approval_options = {
            "cancel": "取消订阅",
            "pause": "暂停订阅",
            "downgrade": "降级套餐",
            "change_plan": "更改套餐",
            "negotiate": "价格谈判"
        }

        require_approval_for = automation_prefs.get("require_approval_for", [])

        approval_selections = {}
        for key, label in require_approval_options.items():
            approval_selections[key] = st.checkbox(
                label,
                value=key in require_approval_for,
                key=f"approval_{key}",
                help=f"执行{label}操作前需要您的确认"
            )

    st.divider()

    # === 保存设置 ===
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("💾 保存设置", type="primary", use_container_width=True):
            # 构建新的自动化偏好
            new_automation_prefs = {
                "automation_level": automation_level,
                "budget_limit": budget_limit,
                "enabled_rules": [
                    rule_id for rule_id, enabled in rule_selections.items() if enabled
                ],
                "auto_pause_unused": auto_pause,
                "unused_days_threshold": unused_threshold,
                "require_approval_for": [
                    key for key, enabled in approval_selections.items() if enabled
                ],
                "enable_auto_checkup": enable_auto_checkup,
                "checkup_time": checkup_time_str
            }

            # 保存 - update_user接受updates字典
            success = data_manager.update_user(
                st.session_state.current_user_id,
                {"automation_preferences": new_automation_prefs}
            )

            if success:
                st.success("✅ 自动化设置已保存")
                st.balloons()

                # 同步规则引擎
                for rule_id, enabled in rule_selections.items():
                    if enabled:
                        rules_engine.enable_rule(rule_id)
                    else:
                        rules_engine.disable_rule(rule_id)

                # 更新调度器
                if enable_auto_checkup:
                    if not scheduler_status["is_running"]:
                        # 在后台线程启动调度器
                        import threading
                        scheduler_thread = threading.Thread(
                            target=daily_checkup_scheduler.start_scheduler,
                            args=(checkup_time_str,),
                            daemon=True
                        )
                        scheduler_thread.start()
                        st.info(f"🟢 每日检查调度器已启动，将在每天 {checkup_time_str} 执行")
                    else:
                        # 更新调度时间
                        daily_checkup_scheduler.schedule_daily_checkup(checkup_time_str)
                        st.info(f"🔄 每日检查时间已更新为 {checkup_time_str}")
                else:
                    if scheduler_status["is_running"]:
                        daily_checkup_scheduler.stop_scheduler()
                        st.info("🔴 每日检查调度器已停止")

            else:
                st.error("❌ 保存设置失败，请重试")

    with col2:
        if st.button("🔄 恢复默认", use_container_width=True):
            st.warning("此操作将恢复所有自动化设置为默认值")
            if st.button("确认恢复", type="secondary"):
                # 恢复默认设置逻辑
                st.info("默认设置已恢复")

    with col3:
        if st.button("🔙 返回", use_container_width=True):
            st.session_state.current_page = "设置"
            st.rerun()

    st.divider()

    # === 规则执行历史 ===
    st.subheader("📜 规则执行历史")
    
    from core.agents.activity_logger import activity_logger
    activities = activity_logger.get_activities(
        agent_id="rules_engine",
        limit=10
    )
    
    if activities:
        for act in activities:
            with st.container():
                status_emoji = "✅" if act.status == "success" else "❌" if act.status == "failed" else "⏳"
                col_h1, col_h2 = st.columns([0.1, 0.9])
                with col_h1:
                    st.write(status_emoji)
                with col_h2:
                    st.markdown(f"**{act.description}**")
                    st.caption(f"时间: {act.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | 服务: {act.details.get('service_name', '未知')}")
                    if act.status == "failed" and "error" in act.details:
                        st.error(f"错误原因: {act.details['error']}")
                st.divider()
    else:
        st.info("暂无规则执行记录")

    st.divider()

    # === 当前状态概览 ===
    st.subheader("📊 当前自动化状态")

    col1, col2, col3 = st.columns(3)

    with col1:
        level_display = {
            "manual": "🔴 手动",
            "semi_auto": "🟡 半自动",
            "full_auto": "🟢 全自动"
        }
        st.metric("自动化级别", level_display.get(automation_level, "未知"))

    with col2:
        enabled_count = sum(1 for v in rule_selections.values() if v)
        st.metric("启用规则数", f"{enabled_count}/{len(all_rules)}")

    with col3:
        if budget_limit:
            st.metric("月度预算", f"¥{budget_limit:.0f}")
        else:
            st.metric("月度预算", "未设置")


if __name__ == "__main__":
    render_automation_settings_page()
