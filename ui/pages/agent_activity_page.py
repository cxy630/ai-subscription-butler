"""
Agent活动日志页面 - 查看AI Agent的活动记录
"""

import streamlit as st
from datetime import datetime, timedelta
from core.agents.activity_logger import activity_logger, ActivityType


def render_agent_activity_page():
    """渲染Agent活动日志页面"""
    st.title("📊 AI Agent 活动日志")

    st.markdown("""
    查看AI管家和所有子Agent的活动记录，了解系统运行状态。
    """)

    st.divider()

    # === 筛选选项 ===
    st.subheader("🔍 筛选条件")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        time_range = st.selectbox(
            "时间范围",
            options=["最近1小时", "最近24小时", "最近7天", "最近30天", "全部"],
            index=1
        )

    with col2:
        agent_filter = st.selectbox(
            "Agent类型",
            options=["全部", "Butler", "Monitoring", "Optimization", "Negotiation"]
        )

    with col3:
        activity_type_filter = st.selectbox(
            "活动类型",
            options=["全部"] + [t.value for t in ActivityType]
        )

    with col4:
        status_filter = st.selectbox(
            "状态",
            options=["全部", "success", "failed", "pending"]
        )

    # 计算时间范围
    time_ranges = {
        "最近1小时": timedelta(hours=1),
        "最近24小时": timedelta(days=1),
        "最近7天": timedelta(days=7),
        "最近30天": timedelta(days=30),
        "全部": None
    }

    start_time = None
    if time_range != "全部":
        start_time = datetime.now() - time_ranges[time_range]

    # 获取活动记录
    activities = activity_logger.get_activities(
        user_id=st.session_state.current_user_id,
        agent_id=None if agent_filter == "全部" else agent_filter.lower() + "_agent",
        activity_type=None if activity_type_filter == "全部" else ActivityType(activity_type_filter),
        start_time=start_time,
        limit=200
    )

    # 应用状态筛选
    if status_filter != "全部":
        activities = [a for a in activities if a.status == status_filter]

    st.divider()

    # === 统计概览 ===
    st.subheader("📈 活动统计")

    # 获取统计数据
    stats = activity_logger.get_activity_stats(
        user_id=st.session_state.current_user_id,
        time_window=timedelta(days=7)
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("总活动数", stats["total_activities"])

    with col2:
        st.metric("成功率", f"{stats['success_rate']:.1f}%")

    with col3:
        st.metric("失败数", stats["by_status"]["failed"])

    with col4:
        most_active = stats.get("most_active_agent", "N/A")
        st.metric("最活跃Agent", most_active)

    # 按Agent类型分布
    if stats["by_agent_type"]:
        st.markdown("**Agent活动分布**")
        for agent_type, count in sorted(stats["by_agent_type"].items(), key=lambda x: x[1], reverse=True):
            percentage = count / stats["total_activities"] * 100 if stats["total_activities"] > 0 else 0
            st.markdown(f"**{agent_type}**: {count} 次 ({percentage:.1f}%)")
            st.progress(percentage / 100)

    st.divider()

    # === 活动列表 ===
    st.subheader("📋 活动记录")

    if not activities:
        st.info("📭 没有找到符合条件的活动记录")
    else:
        st.markdown(f"显示 {len(activities)} 条活动记录")

        # 活动类型图标映射
        activity_icons = {
            "task_started": "▶️",
            "task_completed": "✅",
            "task_failed": "❌",
            "message_sent": "📤",
            "message_received": "📥",
            "decision_made": "🤔",
            "action_taken": "⚡",
            "error_occurred": "🚨"
        }

        # 状态颜色映射
        status_colors = {
            "success": "🟢",
            "failed": "🔴",
            "pending": "🟡"
        }

        for activity in activities:
            # 格式化时间
            time_str = activity.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            time_ago = _get_time_ago(activity.timestamp)

            # 活动标题
            icon = activity_icons.get(activity.activity_type.value, "📌")
            status_icon = status_colors.get(activity.status, "⚪")

            title = f"{icon} {status_icon} **{activity.agent_type}** - {activity.description}"

            with st.expander(f"{title} ({time_ago})"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**活动ID**: `{activity.activity_id}`")
                    st.markdown(f"**Agent**: {activity.agent_id}")
                    st.markdown(f"**类型**: {activity.activity_type.value}")
                    st.markdown(f"**状态**: {activity.status}")

                with col2:
                    st.markdown(f"**时间**: {time_str}")
                    if activity.related_subscription_id:
                        st.markdown(f"**相关订阅**: {activity.related_subscription_id}")

                # 详细信息
                if activity.details:
                    st.markdown("**详细信息**:")
                    st.json(activity.details)

    st.divider()

    # === 最近错误 ===
    recent_errors = activity_logger.get_recent_errors(limit=5)
    if recent_errors:
        st.subheader("🚨 最近错误")

        for error in recent_errors:
            time_str = error.timestamp.strftime("%Y-%m-%d %H:%M:%S")

            with st.expander(f"❌ {error.agent_type} - {error.description}"):
                st.markdown(f"**时间**: {time_str}")
                st.markdown(f"**Agent**: {error.agent_id}")
                if error.details:
                    st.markdown("**错误详情**:")
                    st.json(error.details)

    st.divider()

    # === 操作按钮 ===
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("📥 导出日志", use_container_width=True):
            try:
                filepath = f"agent_activity_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                activity_logger.export_logs(
                    filepath,
                    user_id=st.session_state.current_user_id
                )
                st.success(f"✅ 日志已导出到: {filepath}")
            except Exception as e:
                st.error(f"❌ 导出失败: {str(e)}")

    with col3:
        if st.button("🗑️ 清理旧日志", use_container_width=True):
            activity_logger.clear_old_logs(days_to_keep=30)
            st.success("✅ 已清理30天前的日志")
            st.rerun()


def _get_time_ago(timestamp: datetime) -> str:
    """计算时间差并返回友好的描述"""
    now = datetime.now()
    diff = now - timestamp

    if diff < timedelta(minutes=1):
        return "刚刚"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes}分钟前"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours}小时前"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"{days}天前"
    else:
        return timestamp.strftime("%Y-%m-%d")


if __name__ == "__main__":
    render_agent_activity_page()
