"""
仪表板组件 - 显示用户订阅概览和统计信息
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.database.data_interface import data_manager
from app.constants import CATEGORY_COLORS, CATEGORY_ICONS

def render_subscription_metrics():
    """渲染订阅指标卡片"""
    if not st.session_state.current_user_id:
        st.warning("请先选择用户")
        return

    user_overview = data_manager.get_user_overview(st.session_state.current_user_id)
    if not user_overview:
        st.error("无法获取用户数据")
        return

    # 指标卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📊 总订阅数",
            value=user_overview["total_subscriptions"],
            delta=f"{user_overview['active_subscriptions']} 个活跃"
        )

    with col2:
        monthly_spending = user_overview["monthly_spending"]
        st.metric(
            label="💰 月度支出",
            value=f"¥{monthly_spending:.2f}",
            delta=f"年支出: ¥{monthly_spending * 12:.2f}"
        )

    with col3:
        categories_count = len(user_overview.get("subscription_categories", {}))
        st.metric(
            label="📂 服务类别",
            value=f"{categories_count} 个",
            delta="多样化订阅"
        )

    with col4:
        # 计算平均订阅成本
        avg_cost = monthly_spending / max(user_overview['active_subscriptions'], 1)
        st.metric(
            label="📈 平均成本",
            value=f"¥{avg_cost:.2f}",
            delta="每个订阅/月"
        )

def render_category_breakdown():
    """渲染分类统计"""
    if not st.session_state.current_user_id:
        return

    user_overview = data_manager.get_user_overview(st.session_state.current_user_id)
    if not user_overview or not user_overview.get("subscription_categories"):
        st.info("暂无分类数据")
        return

    st.subheader("📊 支出分类统计")

    categories = user_overview["subscription_categories"]

    # 准备图表数据
    category_names = []
    spending_amounts = []
    subscription_counts = []
    colors = []

    for category, stats in categories.items():
        # 中文名称映射
        category_display = {
            "entertainment": "娱乐",
            "productivity": "生产力",
            "health_fitness": "健康健身",
            "education": "教育",
            "business": "商务",
            "gaming": "游戏",
            "news_media": "新闻媒体",
            "shopping": "购物",
            "travel": "旅行",
            "utilities": "工具",
            "other": "其他"
        }.get(category, category)

        category_names.append(f"{CATEGORY_ICONS.get(category, '📦')} {category_display}")
        spending_amounts.append(stats["spending"])
        subscription_counts.append(stats["count"])
        colors.append(CATEGORY_COLORS.get(category, "#C8D6E5"))

    # 创建两列布局
    col1, col2 = st.columns(2)

    with col1:
        # 支出分布饼图
        fig_pie = go.Figure(data=[go.Pie(
            labels=category_names,
            values=spending_amounts,
            hole=0.4,
            marker=dict(colors=colors),
            textinfo='label+percent',
            textposition='auto'
        )])

        fig_pie.update_layout(
            title="月度支出分布",
            showlegend=True,
            height=400
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # 服务数量柱状图
        fig_bar = go.Figure(data=[go.Bar(
            x=category_names,
            y=subscription_counts,
            marker=dict(color=colors),
            text=subscription_counts,
            textposition='auto'
        )])

        fig_bar.update_layout(
            title="各类别服务数量",
            xaxis_title="类别",
            yaxis_title="服务数量",
            height=400
        )

        fig_bar.update_xaxis(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)

def render_subscription_list():
    """渲染订阅列表"""
    if not st.session_state.current_user_id:
        return

    st.subheader("📋 我的订阅列表")

    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)

    if not subscriptions:
        st.info("暂无活跃订阅")
        return

    # 搜索框
    search_query = st.text_input("🔍 搜索订阅", placeholder="输入服务名称或类别...")

    # 过滤订阅
    if search_query:
        filtered_subs = [
            sub for sub in subscriptions
            if search_query.lower() in sub.get("service_name", "").lower()
            or search_query.lower() in sub.get("category", "").lower()
        ]
    else:
        filtered_subs = subscriptions

    # 排序选项
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("排序方式", [
            "service_name", "price", "category", "created_at"
        ], format_func=lambda x: {
            "service_name": "服务名称",
            "price": "价格",
            "category": "类别",
            "created_at": "添加时间"
        }[x])

    with col2:
        sort_order = st.selectbox("排序顺序", ["asc", "desc"], format_func=lambda x: {"asc": "升序", "desc": "降序"}[x])

    # 排序订阅
    reverse = sort_order == "desc"
    filtered_subs.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)

    # 显示订阅卡片
    for sub in filtered_subs:
        render_subscription_card(sub)

def render_subscription_card(subscription):
    """渲染单个订阅卡片"""
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

        with col1:
            # 服务名称和图标
            category = subscription.get("category", "other")
            icon = CATEGORY_ICONS.get(category, "📦")
            color = CATEGORY_COLORS.get(category, "#C8D6E5")

            st.markdown(f"### {icon} {subscription['service_name']}")

            if subscription.get("notes"):
                st.caption(f"💭 {subscription['notes']}")

        with col2:
            # 价格信息
            price = subscription.get("price", 0)
            currency = subscription.get("currency", "CNY")
            cycle = subscription.get("billing_cycle", "monthly")

            cycle_display = {
                "monthly": "月",
                "yearly": "年",
                "weekly": "周",
                "daily": "日"
            }.get(cycle, cycle)

            st.markdown(f"**💰 {currency}{price:.2f}**")
            st.caption(f"每{cycle_display}")

        with col3:
            # 类别和状态
            category_display = {
                "entertainment": "娱乐",
                "productivity": "生产力",
                "health_fitness": "健康健身",
                "education": "教育",
                "business": "商务",
                "gaming": "游戏",
                "other": "其他"
            }.get(category, category)

            st.markdown(f"**📂 {category_display}**")

            status = subscription.get("status", "active")
            status_color = {"active": "🟢", "paused": "🟡", "cancelled": "🔴"}.get(status, "⚪")
            st.caption(f"{status_color} {status}")

        with col4:
            # 操作按钮
            if st.button("✏️ 编辑", key=f"edit_{subscription['id']}"):
                st.session_state[f"edit_subscription_{subscription['id']}"] = True
                st.rerun()

            if st.button("🗑️ 删除", key=f"delete_{subscription['id']}", type="secondary"):
                if st.session_state.get(f"confirm_delete_{subscription['id']}", False):
                    # 执行删除
                    success = data_manager.delete_subscription(subscription['id'])
                    if success:
                        st.success(f"已删除订阅: {subscription['service_name']}")
                        st.rerun()
                    else:
                        st.error("删除失败")
                else:
                    st.session_state[f"confirm_delete_{subscription['id']}"] = True
                    st.warning("再次点击确认删除")

        st.divider()

def render_quick_stats():
    """渲染快速统计信息"""
    if not st.session_state.current_user_id:
        return

    st.subheader("⚡ 快速洞察")

    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
    if not subscriptions:
        return

    col1, col2 = st.columns(2)

    with col1:
        st.info("💡 **节省建议**")

        # 找出最贵的订阅
        most_expensive = max(subscriptions, key=lambda x: x.get("price", 0))
        st.write(f"• 最贵订阅: {most_expensive['service_name']} (¥{most_expensive['price']}/月)")

        # 统计娱乐类支出
        entertainment_subs = [s for s in subscriptions if s.get("category") == "entertainment"]
        if entertainment_subs:
            entertainment_cost = sum(s.get("price", 0) for s in entertainment_subs)
            st.write(f"• 娱乐支出: ¥{entertainment_cost}/月 ({len(entertainment_subs)}个服务)")

    with col2:
        st.success("📈 **使用提示**")

        # 订阅数量建议
        total_subs = len(subscriptions)
        if total_subs > 5:
            st.write(f"• 您有{total_subs}个订阅，考虑整理一下")
        else:
            st.write(f"• 订阅数量适中 ({total_subs}个)")

        # 年度支出预估
        monthly_total = sum(s.get("price", 0) for s in subscriptions)
        yearly_total = monthly_total * 12
        st.write(f"• 预计年支出: ¥{yearly_total:.2f}")

def render_dashboard():
    """渲染完整仪表板"""
    st.title("📊 数据概览")

    if not st.session_state.current_user_id:
        st.warning("请先选择用户")
        return

    # 指标概览
    render_subscription_metrics()

    st.divider()

    # 分类统计
    render_category_breakdown()

    st.divider()

    # 快速统计
    render_quick_stats()

    st.divider()

    # 订阅列表
    render_subscription_list()

if __name__ == "__main__":
    # 测试组件
    render_dashboard()