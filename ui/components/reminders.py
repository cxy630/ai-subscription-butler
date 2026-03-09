"""
提醒组件 - 显示订阅续费提醒和通知
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.database.data_interface import data_manager
from core.services.reminder_system import reminder_system


def render_reminder_banner():
    """渲染顶部提醒横幅"""
    if not st.session_state.get("current_user_id"):
        return

    # 获取订阅数据
    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
    if not subscriptions:
        return

    # 生成今天和明天的提醒
    reminders = reminder_system.generate_reminders(subscriptions, [0, 1])

    if not reminders:
        return

    # 按优先级分组
    urgent_reminders = [r for r in reminders if r["priority"] == "urgent"]
    high_reminders = [r for r in reminders if r["priority"] == "high"]
    medium_reminders = [r for r in reminders if r["priority"] == "medium"]

    # 显示紧急提醒
    if urgent_reminders:
        for reminder in urgent_reminders:
            st.error(f"⚠️ **紧急**: {reminder['message']}")

    # 显示高优先级提醒
    if high_reminders:
        for reminder in high_reminders:
            st.warning(f"🔔 **今日续费**: {reminder['message']}")

    # 显示中等优先级提醒
    if medium_reminders:
        for reminder in medium_reminders:
            st.info(f"📅 **即将续费**: {reminder['message']}")


def render_upcoming_renewals():
    """渲染即将续费的订阅列表"""
    if not st.session_state.get("current_user_id"):
        st.warning("请先选择用户")
        return

    st.subheader("📅 即将续费的订阅")

    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
    if not subscriptions:
        st.info("暂无活跃订阅")
        return

    # 选择查看的天数范围
    col1, col2 = st.columns([3, 1])
    with col1:
        # 使用7的倍数: 7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84
        days_ahead = st.slider(
            "查看未来多少天的续费",
            min_value=7,
            max_value=84,  # 修改为7的倍数
            value=28,      # 修改为7的倍数
            step=7
        )
    with col2:
        st.metric("查看范围", f"{days_ahead}天")

    # 获取即将续费的订阅
    upcoming = reminder_system.get_upcoming_renewals(subscriptions, days_ahead)

    if not upcoming:
        st.success(f"✅ 未来{days_ahead}天内没有需要续费的订阅")
        return

    # 计算总金额
    total_amount = sum(sub.get("price", 0) for sub in upcoming)

    # 显示汇总信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("即将续费", f"{len(upcoming)}个订阅")
    with col2:
        st.metric("预计支出", f"¥{total_amount:.2f}")
    with col3:
        # 最近的续费日期
        nearest = min(upcoming, key=lambda x: x["days_until_renewal"])
        st.metric("最近续费", f"{nearest['days_until_renewal']}天后")

    st.divider()

    # 显示详细列表
    for sub in upcoming:
        render_renewal_card(sub)


def render_renewal_card(subscription: dict):
    """渲染单个续费提醒卡片"""
    days_until = subscription.get("days_until_renewal", 0)
    next_billing = subscription.get("next_billing_date", "")

    # 根据剩余天数确定样式
    if days_until == 0:
        icon = "🔴"
        status_text = "今天续费"
        color = "red"
    elif days_until == 1:
        icon = "🟡"
        status_text = "明天续费"
        color = "orange"
    elif days_until <= 3:
        icon = "🟠"
        status_text = f"{days_until}天后"
        color = "orange"
    elif days_until <= 7:
        icon = "🟢"
        status_text = f"{days_until}天后"
        color = "blue"
    else:
        icon = "⚪"
        status_text = f"{days_until}天后"
        color = "gray"

    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

        with col1:
            st.markdown(f"### {icon} {subscription['service_name']}")
            if subscription.get("notes"):
                st.caption(subscription["notes"])

        with col2:
            price = subscription.get("price", 0)
            currency = subscription.get("currency", "CNY")
            st.markdown(f"**💰 {currency}{price:.2f}**")
            cycle_display = {
                "monthly": "月付",
                "yearly": "年付",
                "weekly": "周付",
                "daily": "日付"
            }.get(subscription.get("billing_cycle", "monthly"), "月付")
            st.caption(f"计费周期: {cycle_display}")

        with col3:
            st.markdown(f"**⏰ {status_text}**")
            try:
                billing_date = datetime.fromisoformat(next_billing.replace("Z", "+00:00"))
                st.caption(f"续费日期: {billing_date.strftime('%Y-%m-%d')}")
            except:
                st.caption("续费日期: 未知")

        with col4:
            # 操作按钮
            if st.button("📝 编辑", key=f"edit_reminder_{subscription['id']}", use_container_width=True):
                st.session_state[f"edit_subscription_{subscription['id']}"] = True
                st.rerun()

            if st.button("🔕 忽略提醒", key=f"snooze_{subscription['id']}", use_container_width=True, type="secondary"):
                st.info(f"已暂时忽略 {subscription['service_name']} 的提醒")

        st.divider()


def render_reminder_statistics():
    """渲染提醒统计信息"""
    if not st.session_state.get("current_user_id"):
        return

    st.subheader("📊 提醒统计")

    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
    if not subscriptions:
        st.info("暂无订阅数据")
        return

    # 获取统计数据
    stats = reminder_system.get_reminder_statistics(subscriptions)

    # 显示统计卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "今日到期",
            stats.get("due_today", 0),
            delta=f"¥{stats.get('total_amount_due', 0):.2f}"
        )

    with col2:
        st.metric(
            "3天内",
            stats.get("upcoming_3days", 0),
            delta="需关注" if stats.get("upcoming_3days", 0) > 0 else None
        )

    with col3:
        st.metric(
            "7天内",
            stats.get("upcoming_7days", 0),
            delta="即将到期" if stats.get("upcoming_7days", 0) > 0 else None
        )

    with col4:
        overdue = stats.get("overdue", 0)
        st.metric(
            "已逾期",
            overdue,
            delta="⚠️ 需处理" if overdue > 0 else None,
            delta_color="inverse"
        )

    # 显示优先级分布
    st.divider()
    st.markdown("**按优先级分布**")

    priority_data = stats.get("by_priority", {})
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        urgent = priority_data.get("urgent", 0)
        if urgent > 0:
            st.error(f"🚨 紧急: {urgent}")
        else:
            st.caption("🚨 紧急: 0")

    with col2:
        high = priority_data.get("high", 0)
        if high > 0:
            st.warning(f"🔴 高: {high}")
        else:
            st.caption("🔴 高: 0")

    with col3:
        medium = priority_data.get("medium", 0)
        if medium > 0:
            st.info(f"🟡 中: {medium}")
        else:
            st.caption("🟡 中: 0")

    with col4:
        low = priority_data.get("low", 0)
        if low > 0:
            st.success(f"🟢 低: {low}")
        else:
            st.caption("🟢 低: 0")


def render_reminder_settings():
    """渲染提醒设置"""
    st.subheader("⚙️ 提醒设置")

    with st.expander("📧 通知偏好设置", expanded=False):
        st.checkbox("启用桌面通知", value=True)
        st.checkbox("启用邮件提醒", value=False, disabled=True, help="功能开发中")

        st.divider()
        st.markdown("**提醒时机**")

        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("提前7天提醒", value=True)
            st.checkbox("提前3天提醒", value=True)
        with col2:
            st.checkbox("提前1天提醒", value=True)
            st.checkbox("当天提醒", value=True)

        st.divider()
        st.markdown("**免打扰时段**")
        do_not_disturb = st.checkbox("启用免打扰模式", value=False)

        if do_not_disturb:
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.time_input("开始时间", value=None)
            with col2:
                end_time = st.time_input("结束时间", value=None)

    with st.expander("🎯 高级设置", expanded=False):
        st.number_input("最小提醒金额（低于此金额不提醒）", min_value=0.0, value=0.0, step=1.0)
        st.multiselect(
            "忽略的订阅分类",
            ["entertainment", "productivity", "business", "education"],
            format_func=lambda x: {
                "entertainment": "娱乐",
                "productivity": "生产力",
                "business": "商务",
                "education": "教育"
            }.get(x, x)
        )

    if st.button("💾 保存设置", type="primary"):
        st.success("✅ 设置已保存")


def render_reminders_page():
    """渲染完整的提醒页面"""
    st.title("🔔 订阅提醒")

    if not st.session_state.get("current_user_id"):
        st.warning("请先选择用户")
        return

    # 顶部横幅提醒
    render_reminder_banner()

    st.divider()

    # 统计信息
    render_reminder_statistics()

    st.divider()

    # 即将续费列表
    render_upcoming_renewals()

    st.divider()

    # 提醒设置
    render_reminder_settings()


if __name__ == "__main__":
    # 测试组件
    render_reminders_page()