"""
分析报告页面 - 深度数据分析和洞察
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.database.data_interface import data_manager
from core.services.daily_checkup_scheduler import daily_checkup_scheduler
from app.constants import CATEGORY_COLORS, CATEGORY_ICONS

def render_weekly_ai_report():
    """渲染AI周报摘要"""
    st.subheader("🤖 AI 管家周度洞察")
    
    # 获取缓存的周报
    report = st.session_state.get("last_weekly_report")
    
    if report and report.get("status") == "success":
        with st.container():
            st.info(f"📅 **报告日期**: {datetime.fromisoformat(report['report_date']).strftime('%Y-%m-%d')}")
            st.markdown(f"### 💡 管家本周总结")
            st.write(report.get("summary", "本周订阅状态平稳。"))
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("活跃订阅", f"{report['stats']['active_count']} 个")
            with col2:
                st.metric("月度开支(CNY)", f"¥{report['stats']['estimated_monthly_cost']:.2f}")
    else:
        st.info("💡 尚未生成本周报告。点击下方按钮，让AI管家为您进行深度分析。")
        if st.button("🚀 立即生成AI周报", use_container_width=True):
            with st.spinner("AI管家正在梳理账单并撰写报告..."):
                import asyncio
                result = asyncio.run(
                    daily_checkup_scheduler.run_weekly_report_for_user(
                        st.session_state.current_user_id
                    )
                )
                if result.get("status") == "success":
                    st.session_state.last_weekly_report = result
                    st.rerun()
                else:
                    st.error(f"❌ 生成失败: {result.get('error', '未知错误')}")
    
    st.divider()


def render_spending_trends():
    """渲染支出趋势分析"""
    if not st.session_state.current_user_id:
        return

    st.subheader("📈 支出趋势分析")

    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
    if not subscriptions:
        st.info("暂无数据用于分析")
        return

    # 模拟历史数据（实际应从数据库获取）
    months = ["1月", "2月", "3月", "4月", "5月", "6月"]
    current_monthly = sum(s.get("price", 0) for s in subscriptions)

    # 模拟趋势数据
    trends = [
        current_monthly * 0.8,
        current_monthly * 0.85,
        current_monthly * 0.9,
        current_monthly * 0.95,
        current_monthly * 0.98,
        current_monthly
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=trends,
        mode='lines+markers',
        name='月度支出',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title="最近6个月支出趋势",
        xaxis_title="月份",
        yaxis_title="支出金额 (¥)",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # 趋势分析
    col1, col2 = st.columns(2)
    with col1:
        growth_rate = ((trends[-1] - trends[0]) / trends[0]) * 100
        if growth_rate > 0:
            st.warning(f"📈 支出增长 {growth_rate:.1f}%")
        else:
            st.success(f"📉 支出减少 {abs(growth_rate):.1f}%")

    with col2:
        avg_monthly = sum(trends) / len(trends)
        st.info(f"💰 平均月支出: ¥{avg_monthly:.2f}")

def render_category_analysis():
    """渲染分类深度分析"""
    if not st.session_state.current_user_id:
        return

    st.subheader("🔍 分类深度分析")

    user_overview = data_manager.get_user_overview(st.session_state.current_user_id)
    if not user_overview or not user_overview.get("subscription_categories"):
        st.info("暂无分类数据")
        return

    categories = user_overview["subscription_categories"]

    # 创建子图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('支出分布', '服务数量', '平均单价', '分类对比'),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )

    # 准备数据
    category_names = []
    spending_amounts = []
    subscription_counts = []
    colors = []

    for category, stats in categories.items():
        category_display = {
            "entertainment": "娱乐",
            "productivity": "生产力",
            "health_fitness": "健康健身",
            "education": "教育",
            "business": "商务",
            "gaming": "游戏",
            "other": "其他"
        }.get(category, category)

        category_names.append(category_display)
        spending_amounts.append(stats["spending"])
        subscription_counts.append(stats["count"])
        colors.append(CATEGORY_COLORS.get(category, "#C8D6E5"))

    # 支出分布饼图
    fig.add_trace(
        go.Pie(labels=category_names, values=spending_amounts,
               marker=dict(colors=colors), showlegend=False),
        row=1, col=1
    )

    # 服务数量柱状图
    fig.add_trace(
        go.Bar(x=category_names, y=subscription_counts,
               marker=dict(color=colors), showlegend=False),
        row=1, col=2
    )

    # 平均单价
    avg_prices = [spending_amounts[i] / max(subscription_counts[i], 1) for i in range(len(category_names))]
    fig.add_trace(
        go.Bar(x=category_names, y=avg_prices,
               marker=dict(color=colors), showlegend=False),
        row=2, col=1
    )

    # 分类对比散点图
    fig.add_trace(
        go.Scatter(x=subscription_counts, y=spending_amounts,
                   mode='markers+text',
                   text=category_names,
                   textposition="top center",
                   marker=dict(size=[p*2 for p in avg_prices],
                              color=colors, opacity=0.7),
                   showlegend=False),
        row=2, col=2
    )

    fig.update_layout(height=800, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def render_cost_optimization():
    """渲染成本优化建议"""
    if not st.session_state.current_user_id:
        return

    st.subheader("💡 成本优化建议")

    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
    if not subscriptions:
        return

    # 分析数据
    total_monthly = sum(s.get("price", 0) for s in subscriptions)
    most_expensive = max(subscriptions, key=lambda x: x.get("price", 0))
    entertainment_subs = [s for s in subscriptions if s.get("category") == "entertainment"]
    entertainment_cost = sum(s.get("price", 0) for s in entertainment_subs)

    col1, col2 = st.columns(2)

    with col1:
        st.info("🎯 **优化机会**")

        optimization_tips = []

        if entertainment_cost > 50:
            optimization_tips.append(f"• 娱乐支出较高 (¥{entertainment_cost:.2f}/月)，可以考虑减少不常用服务")

        if len(subscriptions) > 6:
            optimization_tips.append(f"• 订阅服务较多 ({len(subscriptions)}个)，建议定期评估使用频率")

        if most_expensive["price"] > 100:
            optimization_tips.append(f"• {most_expensive['service_name']} 是最贵的服务 (¥{most_expensive['price']}/月)")

        # 查找潜在重复服务
        service_names_lower = [s.get("service_name", "").lower() for s in subscriptions]
        if any("spotify" in name for name in service_names_lower) and any("apple music" in name for name in service_names_lower):
            optimization_tips.append("• 检测到多个音乐服务，建议保留一个")

        if optimization_tips:
            for tip in optimization_tips:
                st.write(tip)
        else:
            st.write("✅ 您的订阅结构已经比较合理")

    with col2:
        st.success("💰 **节省潜力**")

        # 计算潜在节省
        potential_savings = 0
        savings_details = []

        if entertainment_cost > 30:
            potential_monthly = min(entertainment_cost * 0.3, 20)
            potential_savings += potential_monthly
            savings_details.append(f"• 优化娱乐服务: ¥{potential_monthly:.2f}/月")

        if len(subscriptions) > 5:
            potential_monthly = min(total_monthly * 0.1, 30)
            potential_savings += potential_monthly
            savings_details.append(f"• 减少冗余服务: ¥{potential_monthly:.2f}/月")

        if savings_details:
            for detail in savings_details:
                st.write(detail)
            st.write(f"**总计潜在节省: ¥{potential_savings:.2f}/月**")
            st.write(f"**年度节省: ¥{potential_savings * 12:.2f}**")
        else:
            st.write("🎯 继续保持良好的订阅管理习惯")

def render_usage_insights():
    """渲染使用洞察"""
    if not st.session_state.current_user_id:
        return

    st.subheader("🔍 使用洞察")

    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
    if not subscriptions:
        return

    # 模拟使用数据分析
    insights = []

    # 按价格分析
    expensive_subs = [s for s in subscriptions if s.get("price", 0) > 50]
    if expensive_subs:
        insights.append({
            "icon": "💸",
            "title": "高价值服务监控",
            "content": f"您有 {len(expensive_subs)} 个高价服务，建议重点关注使用频率",
            "type": "warning"
        })

    # 按类别分析
    categories = {}
    for sub in subscriptions:
        cat = sub.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1

    if categories.get("entertainment", 0) >= 3:
        insights.append({
            "icon": "🎬",
            "title": "娱乐服务集中",
            "content": f"您有 {categories['entertainment']} 个娱乐服务，可能存在功能重叠",
            "type": "info"
        })

    # 订阅密度分析
    if len(subscriptions) > 8:
        insights.append({
            "icon": "📱",
            "title": "订阅密度较高",
            "content": "建议设置月度预算限制，避免无意识支出增长",
            "type": "warning"
        })
    elif len(subscriptions) < 3:
        insights.append({
            "icon": "✨",
            "title": "订阅结构简洁",
            "content": "您的订阅数量适中，管理相对简单",
            "type": "success"
        })

    # 显示洞察
    for i, insight in enumerate(insights):
        if insight["type"] == "warning":
            st.warning(f"{insight['icon']} **{insight['title']}**\n\n{insight['content']}")
        elif insight["type"] == "success":
            st.success(f"{insight['icon']} **{insight['title']}**\n\n{insight['content']}")
        else:
            st.info(f"{insight['icon']} **{insight['title']}**\n\n{insight['content']}")

def render_forecast_analysis():
    """渲染预测分析"""
    if not st.session_state.current_user_id:
        return

    st.subheader("🔮 支出预测")

    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
    if not subscriptions:
        return

    current_monthly = sum(s.get("price", 0) for s in subscriptions)

    # 模拟预测数据
    months = ["当前", "1月后", "3月后", "6月后", "1年后"]
    forecasts = [
        current_monthly,
        current_monthly * 1.02,  # 假设轻微增长
        current_monthly * 1.05,
        current_monthly * 1.08,
        current_monthly * 1.15   # 年度预期增长
    ]

    # 预测图表
    fig = go.Figure()

    # 历史数据
    fig.add_trace(go.Scatter(
        x=months[:1],
        y=forecasts[:1],
        mode='markers',
        name='当前支出',
        marker=dict(color='#3498db', size=12)
    ))

    # 预测数据
    fig.add_trace(go.Scatter(
        x=months,
        y=forecasts,
        mode='lines+markers',
        name='预测支出',
        line=dict(color='#e74c3c', dash='dash'),
        marker=dict(color='#e74c3c', size=8)
    ))

    fig.update_layout(
        title="支出预测趋势",
        xaxis_title="时间",
        yaxis_title="支出金额 (¥)",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # 预测摘要
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("当前月支出", f"¥{current_monthly:.2f}")

    with col2:
        future_6m = forecasts[3]
        st.metric("6个月预测", f"¥{future_6m:.2f}", f"+¥{future_6m-current_monthly:.2f}")

    with col3:
        future_1y = forecasts[4]
        st.metric("1年预测", f"¥{future_1y:.2f}", f"+¥{future_1y-current_monthly:.2f}")

def render_analytics_page():
    """渲染完整的分析报告页面"""
    st.title("📈 分析报告")

    if not st.session_state.current_user_id:
        st.warning("请先选择用户")
        return

    # 1. 优先展示AI周报摘要
    render_weekly_ai_report()

    # 2. 渲染各个分析模块
    render_spending_trends()

    st.divider()

    render_category_analysis()

    st.divider()

    render_cost_optimization()

    st.divider()

    render_usage_insights()

    st.divider()

    render_forecast_analysis()

    # 导出功能
    st.divider()
    st.subheader("📋 报告导出")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 导出Excel报告", use_container_width=True):
            st.info("Excel导出功能开发中...")

    with col2:
        if st.button("📄 生成PDF报告", use_container_width=True):
            st.info("PDF导出功能开发中...")

    with col3:
        if st.button("📤 发送邮件报告", use_container_width=True):
            st.info("邮件发送功能开发中...")

if __name__ == "__main__":
    # 测试组件
    render_analytics_page()