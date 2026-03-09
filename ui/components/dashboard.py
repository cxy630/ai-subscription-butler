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
import json
import csv
import io

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

        fig_bar.update_xaxes(tickangle=45)
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

    # 初始化批量选择状态
    if "batch_mode" not in st.session_state:
        st.session_state.batch_mode = False
    if "selected_subscriptions" not in st.session_state:
        st.session_state.selected_subscriptions = set()

    # 批量操作工具栏
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        batch_toggle = st.checkbox(
            "🎯 批量操作模式",
            value=st.session_state.batch_mode,
            key="batch_mode_toggle"
        )
        st.session_state.batch_mode = batch_toggle

    if st.session_state.batch_mode:
        selected_count = len(st.session_state.selected_subscriptions)

        with col2:
            if st.button(f"✅ 全选 ({len(subscriptions)})", use_container_width=True):
                st.session_state.selected_subscriptions = {sub["id"] for sub in subscriptions}
                st.rerun()

        with col3:
            if st.button("❌ 取消全选", use_container_width=True):
                st.session_state.selected_subscriptions = set()
                st.rerun()

        with col4:
            st.metric("已选", f"{selected_count}个")

        # 批量操作按钮
        if selected_count > 0:
            st.divider()
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button(f"🗑️ 批量删除 ({selected_count})", type="secondary", use_container_width=True):
                    st.session_state.show_batch_delete_confirm = True

            with col2:
                new_status = st.selectbox(
                    "批量更改状态",
                    ["", "active", "paused", "cancelled"],
                    format_func=lambda x: {
                        "": "选择状态...",
                        "active": "✅ 激活",
                        "paused": "⏸️ 暂停",
                        "cancelled": "❌ 已取消"
                    }[x]
                )
                if new_status and st.button("应用状态", use_container_width=True):
                    batch_update_status(list(st.session_state.selected_subscriptions), new_status)

            with col3:
                new_category = st.selectbox(
                    "批量更改分类",
                    ["", "entertainment", "productivity", "business", "education", "storage", "health", "other"],
                    format_func=lambda x: {
                        "": "选择分类...",
                        "entertainment": "🎬 娱乐",
                        "productivity": "⚡ 生产力",
                        "business": "💼 商务",
                        "education": "📚 教育",
                        "storage": "💾 存储",
                        "health": "🏃 健康",
                        "other": "📦 其他"
                    }[x]
                )
                if new_category and st.button("应用分类", use_container_width=True):
                    batch_update_category(list(st.session_state.selected_subscriptions), new_category)

            with col4:
                if st.button("📥 导出选中", use_container_width=True):
                    export_selected_subscriptions(list(st.session_state.selected_subscriptions), subscriptions)

    # 批量删除确认对话框
    if st.session_state.get("show_batch_delete_confirm", False):
        st.warning(f"⚠️ 确定要删除选中的 {len(st.session_state.selected_subscriptions)} 个订阅吗?此操作不可撤销!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 确认删除", type="primary", use_container_width=True):
                batch_delete_subscriptions(list(st.session_state.selected_subscriptions))
                st.session_state.show_batch_delete_confirm = False
                st.session_state.selected_subscriptions = set()
                st.rerun()
        with col2:
            if st.button("❌ 取消", use_container_width=True):
                st.session_state.show_batch_delete_confirm = False
                st.rerun()

    st.divider()

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

    # 排序选项（默认按添加时间降序）
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("排序方式", [
            "created_at", "service_name", "price", "category"
        ], format_func=lambda x: {
            "service_name": "服务名称",
            "price": "价格",
            "category": "类别",
            "created_at": "添加时间"
        }[x])

    with col2:
        sort_order = st.selectbox("排序顺序", ["desc", "asc"], format_func=lambda x: {"asc": "升序", "desc": "降序"}[x])

    # 排序订阅
    reverse = sort_order == "desc"
    filtered_subs.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)

    # 显示订阅卡片
    for sub in filtered_subs:
        render_subscription_card(sub)

        # 如果这个订阅正在编辑，在下方显示编辑表单
        edit_key = f"edit_subscription_{sub['id']}"
        if st.session_state.get(edit_key, False):
            render_inline_edit_form(sub)
            st.markdown("---")

def batch_delete_subscriptions(subscription_ids: list):
    """批量删除订阅"""
    success_count = 0
    for sub_id in subscription_ids:
        if data_manager.delete_subscription(sub_id):
            success_count += 1

    if success_count > 0:
        st.success(f"✅ 成功删除 {success_count} 个订阅")
    else:
        st.error("❌ 删除失败")

def batch_update_status(subscription_ids: list, new_status: str):
    """批量更新订阅状态"""
    success_count = 0
    for sub_id in subscription_ids:
        if data_manager.update_subscription(sub_id, {"status": new_status}):
            success_count += 1

    if success_count > 0:
        st.success(f"✅ 成功更新 {success_count} 个订阅的状态")
        st.session_state.selected_subscriptions = set()
        st.rerun()
    else:
        st.error("❌ 更新失败")

def batch_update_category(subscription_ids: list, new_category: str):
    """批量更新订阅分类"""
    success_count = 0
    for sub_id in subscription_ids:
        if data_manager.update_subscription(sub_id, {"category": new_category}):
            success_count += 1

    if success_count > 0:
        st.success(f"✅ 成功更新 {success_count} 个订阅的分类")
        st.session_state.selected_subscriptions = set()
        st.rerun()
    else:
        st.error("❌ 更新失败")

def export_selected_subscriptions(subscription_ids: list, all_subscriptions: list):
    """导出选中的订阅"""
    selected_subs = [sub for sub in all_subscriptions if sub["id"] in subscription_ids]

    if not selected_subs:
        st.warning("没有选中的订阅")
        return

    # 生成JSON
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "subscription_count": len(selected_subs),
        "subscriptions": selected_subs
    }

    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)

    # 提供下载
    st.download_button(
        label=f"💾 下载选中的 {len(selected_subs)} 个订阅 (JSON)",
        data=json_str,
        file_name=f"selected_subscriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def render_subscription_card(subscription):
    """渲染单个订阅卡片"""
    with st.container():
        # 如果是批量模式,添加checkbox列
        if st.session_state.get("batch_mode", False):
            col_check, col1, col2, col3, col4, col5 = st.columns([0.5, 2.5, 2, 2, 2, 2])
            with col_check:
                is_selected = subscription["id"] in st.session_state.selected_subscriptions
                if st.checkbox("", value=is_selected, key=f"select_{subscription['id']}", label_visibility="collapsed"):
                    st.session_state.selected_subscriptions.add(subscription["id"])
                else:
                    st.session_state.selected_subscriptions.discard(subscription["id"])
        else:
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])

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
            # 日期信息
            from datetime import datetime
            from core.services.reminder_system import reminder_system

            # 订阅日期
            start_date_str = subscription.get("start_date") or subscription.get("created_at")
            if start_date_str:
                try:
                    start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
                    st.markdown(f"**📅 订阅日期**")
                    st.caption(start_date.strftime("%Y-%m-%d"))
                except:
                    st.markdown(f"**📅 订阅日期**")
                    st.caption("未知")
            else:
                st.markdown(f"**📅 订阅日期**")
                st.caption("未知")

            # 计算下次续费日期
            if start_date_str:
                try:
                    now = datetime.now()
                    billing_cycle = subscription.get("billing_cycle", "monthly")
                    next_billing = reminder_system._calculate_next_billing_from_start(
                        start_date, billing_cycle, now
                    )
                    days_until = reminder_system.calculate_days_until_renewal(next_billing)

                    # 根据剩余天数设置颜色
                    if days_until < 0:
                        color_icon = "🔴"
                    elif days_until == 0:
                        color_icon = "🟠"
                    elif days_until <= 3:
                        color_icon = "🟡"
                    elif days_until <= 7:
                        color_icon = "🟢"
                    else:
                        color_icon = "⚪"

                    st.markdown(f"**⏰ 续费日期**")
                    st.caption(f"{color_icon} {next_billing.strftime('%Y-%m-%d')} ({days_until}天)")
                except:
                    st.markdown(f"**⏰ 续费日期**")
                    st.caption("计算中...")
            else:
                st.markdown(f"**⏰ 续费日期**")
                st.caption("未设置")

        with col4:
            # 类别和状态
            category_display = {
                "entertainment": "娱乐",
                "productivity": "生产力",
                "health_fitness": "健康健身",
                "education": "教育",
                "business": "商务",
                "storage": "存储",
                "gaming": "游戏",
                "other": "其他"
            }.get(category, category)

            st.markdown(f"**📂 {category_display}**")

            status = subscription.get("status", "active")
            status_color = {"active": "🟢", "paused": "🟡", "cancelled": "🔴"}.get(status, "⚪")
            st.caption(f"{status_color} {status}")

        with col5:
            # 操作按钮
            edit_key = f"edit_subscription_{subscription['id']}"

            # 使用button触发编辑,点击后立即显示
            if st.session_state.get(edit_key, False):
                # 正在编辑状态 - 显示取消按钮
                if st.button("❌ 取消", key=f"cancel_edit_{subscription['id']}", use_container_width=True):
                    st.session_state[edit_key] = False
                    st.rerun()
            else:
                # 未编辑状态 - 显示编辑按钮
                if st.button("✏️ 编辑", key=f"edit_{subscription['id']}", use_container_width=True):
                    st.session_state[edit_key] = True
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

def render_spending_trends():
    """渲染支出趋势分析"""
    if not st.session_state.current_user_id:
        return

    st.subheader("📈 支出趋势分析")

    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
    if not subscriptions:
        return

    # 计算当前月度支出
    monthly_total = sum(s.get("price", 0) for s in subscriptions)

    # 模拟未来6个月的支出趋势（假设订阅保持不变）
    months = ["当前月", "1个月后", "2个月后", "3个月后", "4个月后", "5个月后", "6个月后"]
    spending = [monthly_total] * 7

    # 创建趋势图
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=spending,
        mode='lines+markers',
        name='预计支出',
        line=dict(color='#5DADE2', width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title="未来6个月支出预测",
        xaxis_title="时间",
        yaxis_title="支出 (CNY)",
        height=300,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

def render_category_insights():
    """渲染分类洞察"""
    if not st.session_state.current_user_id:
        return

    st.subheader("🎯 分类深度分析")

    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
    if not subscriptions:
        return

    # 按分类统计
    category_stats = {}
    for sub in subscriptions:
        category = sub.get("category", "other")
        if category not in category_stats:
            category_stats[category] = {
                "count": 0,
                "total_cost": 0,
                "services": []
            }
        category_stats[category]["count"] += 1
        category_stats[category]["total_cost"] += sub.get("price", 0)
        category_stats[category]["services"].append(sub.get("service_name", "未知"))

    # 显示每个分类的详细信息
    for category, stats in sorted(category_stats.items(), key=lambda x: x[1]["total_cost"], reverse=True):
        category_display = {
            "entertainment": "娱乐",
            "productivity": "生产力",
            "health_fitness": "健康健身",
            "education": "教育",
            "business": "商务",
            "storage": "存储",
            "other": "其他"
        }.get(category, category)

        icon = CATEGORY_ICONS.get(category, "📦")

        with st.expander(f"{icon} {category_display} - ¥{stats['total_cost']:.2f}/月 ({stats['count']}个服务)"):
            st.write(f"**服务列表:** {', '.join(stats['services'])}")
            avg_cost = stats['total_cost'] / stats['count']
            st.write(f"**平均成本:** ¥{avg_cost:.2f}/服务")
            percentage = (stats['total_cost'] / sum(s['total_cost'] for s in category_stats.values())) * 100
            st.write(f"**占比:** {percentage:.1f}%")

def render_inline_edit_form(subscription: dict):
    """渲染内联编辑表单（手风琴式展开）"""
    # 使用带边框的container来突出显示编辑区域
    st.markdown(f"""
    <div style="
        background-color: #f0f8ff;
        border-left: 5px solid #4CAF50;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    ">
    <h4 style="margin: 0; color: #2E7D32;">✏️ 正在编辑: {subscription['service_name']}</h4>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        with st.form(f"inline_edit_form_{subscription['id']}"):
                col1, col2 = st.columns(2)

                with col1:
                    service_name = st.text_input(
                        "服务名称 *",
                        value=subscription.get("service_name", ""),
                        placeholder="例如: Netflix"
                    )

                    price = st.number_input(
                        "价格 *",
                        min_value=0.0,
                        value=float(subscription.get("price", 0)),
                        step=0.01,
                        format="%.2f"
                    )

                    currency = st.selectbox(
                        "币种",
                        ["CNY", "USD", "EUR", "GBP", "JPY"],
                        index=["CNY", "USD", "EUR", "GBP", "JPY"].index(subscription.get("currency", "CNY"))
                    )

                with col2:
                    billing_cycle = st.selectbox(
                        "付费周期",
                        ["monthly", "yearly", "weekly", "daily"],
                        index=["monthly", "yearly", "weekly", "daily"].index(subscription.get("billing_cycle", "monthly")),
                        format_func=lambda x: {
                            "monthly": "月付",
                            "yearly": "年付",
                            "weekly": "周付",
                            "daily": "日付"
                        }[x]
                    )

                    categories = ["entertainment", "productivity", "health_fitness", "education", "business", "storage", "other"]
                    current_category = subscription.get("category", "other")
                    category_index = categories.index(current_category) if current_category in categories else 0

                    category = st.selectbox(
                        "分类",
                        categories,
                        index=category_index,
                        format_func=lambda x: {
                            "entertainment": "娱乐",
                            "productivity": "生产力",
                            "health_fitness": "健康健身",
                            "education": "教育",
                            "business": "商务",
                            "storage": "存储",
                            "other": "其他"
                        }[x]
                    )

                    status = st.selectbox(
                        "状态",
                        ["active", "paused", "cancelled"],
                        index=["active", "paused", "cancelled"].index(subscription.get("status", "active")),
                        format_func=lambda x: {
                            "active": "✅ 活跃",
                            "paused": "⏸️ 暂停",
                            "cancelled": "❌ 已取消"
                        }[x]
                    )

                st.divider()

                col1, col2 = st.columns(2)
                with col1:
                    from datetime import datetime
                    # 获取现有的开始日期
                    existing_start_date = subscription.get("start_date") or subscription.get("created_at")
                    if existing_start_date:
                        try:
                            start_date_value = datetime.fromisoformat(existing_start_date.replace("Z", "+00:00")).date()
                        except:
                            start_date_value = datetime.now().date()
                    else:
                        start_date_value = datetime.now().date()

                    start_date = st.date_input(
                        "订阅开始日期",
                        value=start_date_value,
                        help="首次订阅或上次续费的日期"
                    )

                with col2:
                    # 显示计算的续费日期
                    from core.services.reminder_system import reminder_system
                    try:
                        now = datetime.now()
                        next_billing = reminder_system._calculate_next_billing_from_start(
                            datetime.combine(start_date, datetime.min.time()),
                            billing_cycle,
                            now
                        )
                        days_until = reminder_system.calculate_days_until_renewal(next_billing)
                        st.info(f"📅 下次续费: {next_billing.strftime('%Y-%m-%d')} ({days_until}天后)")
                    except:
                        st.info("📅 下次续费: 计算中...")

                notes = st.text_area(
                    "备注",
                    value=subscription.get("notes", "") or "",
                    placeholder="添加关于此订阅的备注信息",
                    height=80
                )

                st.divider()

                # 操作按钮
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    submit = st.form_submit_button("💾 保存更改", use_container_width=True, type="primary")

                with col2:
                    cancel = st.form_submit_button("❌ 取消", use_container_width=True)

                with col3:
                    delete = st.form_submit_button("🗑️ 删除订阅", use_container_width=True, type="secondary")

                with col4:
                    # 空列，用于布局
                    pass

                # 处理表单提交
                if submit:
                    if service_name and price >= 0:
                        from datetime import datetime
                        updates = {
                            "service_name": service_name,
                            "price": price,
                            "currency": currency,
                            "billing_cycle": billing_cycle,
                            "category": category,
                            "status": status,
                            "start_date": datetime.combine(start_date, datetime.min.time()).isoformat(),
                            "notes": notes or None
                        }

                        success = data_manager.update_subscription(subscription['id'], updates)

                        if success:
                            st.success(f"✅ 已成功更新 {service_name}")
                            st.session_state[f"edit_subscription_{subscription['id']}"] = False
                            st.rerun()
                        else:
                            st.error("❌ 更新失败，请重试")
                    else:
                        st.error("❌ 请填写完整信息（服务名称和价格不能为空）")

                elif cancel:
                    # 取消编辑，关闭编辑表单
                    st.session_state[f"edit_subscription_{subscription['id']}"] = False
                    st.rerun()

                elif delete:
                    if data_manager.delete_subscription(subscription['id']):
                        st.success(f"✅ 已删除 {subscription['service_name']}")
                        st.session_state[f"edit_subscription_{subscription['id']}"] = False
                        st.rerun()
                    else:
                        st.error("❌ 删除失败，请重试")

def render_quick_stats():
    """渲染快速统计信息"""
    if not st.session_state.current_user_id:
        return

    st.subheader("⚡ 智能洞察")

    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
    if not subscriptions:
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("💡 **节省建议**")

        # 找出最贵的订阅
        most_expensive = max(subscriptions, key=lambda x: x.get("price", 0))
        st.write(f"• 最贵订阅: {most_expensive['service_name']} (¥{most_expensive['price']:.2f}/月)")

        # 找出最便宜的订阅（排除0元）
        paid_subs = [s for s in subscriptions if s.get("price", 0) > 0]
        if paid_subs:
            cheapest = min(paid_subs, key=lambda x: x.get("price", 0))
            st.write(f"• 最便宜订阅: {cheapest['service_name']} (¥{cheapest['price']:.2f}/月)")

        # 统计娱乐类支出
        entertainment_subs = [s for s in subscriptions if s.get("category") == "entertainment"]
        if entertainment_subs:
            entertainment_cost = sum(s.get("price", 0) for s in entertainment_subs)
            st.write(f"• 娱乐支出: ¥{entertainment_cost:.2f}/月 ({len(entertainment_subs)}个)")

    with col2:
        st.success("📊 **统计数据**")

        # 订阅数量建议
        total_subs = len(subscriptions)
        if total_subs > 10:
            st.write(f"• 您有{total_subs}个订阅，建议优化整合")
        elif total_subs > 5:
            st.write(f"• 您有{total_subs}个订阅，数量较多")
        else:
            st.write(f"• 订阅数量适中 ({total_subs}个)")

        # 年度支出预估
        monthly_total = sum(s.get("price", 0) for s in subscriptions)
        yearly_total = monthly_total * 12
        st.write(f"• 预计年支出: ¥{yearly_total:.2f}")

        # 平均订阅成本
        avg_cost = monthly_total / len(subscriptions) if subscriptions else 0
        st.write(f"• 平均成本: ¥{avg_cost:.2f}/服务")

    with col3:
        st.warning("🎯 **优化建议**")

        # 检查是否有重复类别的服务
        category_counts = {}
        for sub in subscriptions:
            cat = sub.get("category", "other")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # 找出服务最多的分类
        if category_counts:
            max_category = max(category_counts.items(), key=lambda x: x[1])
            cat_display = {
                "entertainment": "娱乐",
                "productivity": "生产力",
                "business": "商务",
                "storage": "存储"
            }.get(max_category[0], max_category[0])
            st.write(f"• 主要分类: {cat_display} ({max_category[1]}个)")

        # 免费订阅统计
        free_subs = [s for s in subscriptions if s.get("price", 0) == 0]
        if free_subs:
            st.write(f"• 免费服务: {len(free_subs)}个")

        # 高价订阅提醒
        expensive_subs = [s for s in subscriptions if s.get("price", 0) > 50]
        if expensive_subs:
            st.write(f"• 高价订阅: {len(expensive_subs)}个 (>¥50/月)")

def render_export_section():
    """渲染数据导出功能"""
    if not st.session_state.current_user_id:
        return

    st.subheader("📥 数据导出")

    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
    if not subscriptions:
        st.info("暂无数据可导出")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        # 导出为CSV
        if st.button("📄 导出为 CSV", use_container_width=True):
            # 准备CSV数据
            csv_buffer = io.StringIO()
            csv_writer = csv.writer(csv_buffer)

            # 写入表头
            csv_writer.writerow([
                "服务名称", "价格", "币种", "计费周期", "分类",
                "状态", "添加日期", "备注"
            ])

            # 写入数据
            for sub in subscriptions:
                csv_writer.writerow([
                    sub.get("service_name", ""),
                    sub.get("price", 0),
                    sub.get("currency", "CNY"),
                    sub.get("billing_cycle", "monthly"),
                    sub.get("category", "other"),
                    sub.get("status", "active"),
                    sub.get("created_at", ""),
                    sub.get("notes", "")
                ])

            # 提供下载
            csv_data = csv_buffer.getvalue()
            st.download_button(
                label="⬇️ 下载 CSV 文件",
                data=csv_data,
                file_name=f"subscriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    with col2:
        # 导出为JSON
        if st.button("📋 导出为 JSON", use_container_width=True):
            # 准备JSON数据
            export_data = {
                "export_date": datetime.now().isoformat(),
                "user_id": st.session_state.current_user_id,
                "total_subscriptions": len(subscriptions),
                "subscriptions": subscriptions
            }

            json_data = json.dumps(export_data, ensure_ascii=False, indent=2)

            st.download_button(
                label="⬇️ 下载 JSON 文件",
                data=json_data,
                file_name=f"subscriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

    with col3:
        # 导出为Excel格式的CSV（带统计信息）
        if st.button("📊 导出详细报告", use_container_width=True):
            # 创建详细报告
            report_buffer = io.StringIO()

            # 写入标题和统计信息
            report_buffer.write(f"订阅服务详细报告\n")
            report_buffer.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            report_buffer.write(f"用户ID: {st.session_state.current_user_id}\n")
            report_buffer.write(f"\n")

            # 写入汇总统计
            monthly_total = sum(s.get("price", 0) for s in subscriptions)
            report_buffer.write(f"订阅总数: {len(subscriptions)}\n")
            report_buffer.write(f"月度总支出: ¥{monthly_total:.2f}\n")
            report_buffer.write(f"年度预计支出: ¥{monthly_total * 12:.2f}\n")
            report_buffer.write(f"\n")

            # 写入详细订阅列表
            report_buffer.write(f"详细订阅列表:\n")
            report_buffer.write(f"{'='*80}\n")

            csv_writer = csv.writer(report_buffer)
            csv_writer.writerow([
                "服务名称", "价格", "币种", "计费周期", "分类",
                "状态", "添加日期", "备注"
            ])

            for sub in subscriptions:
                csv_writer.writerow([
                    sub.get("service_name", ""),
                    sub.get("price", 0),
                    sub.get("currency", "CNY"),
                    sub.get("billing_cycle", "monthly"),
                    sub.get("category", "other"),
                    sub.get("status", "active"),
                    sub.get("created_at", ""),
                    sub.get("notes", "")
                ])

            report_data = report_buffer.getvalue()
            st.download_button(
                label="⬇️ 下载详细报告",
                data=report_data,
                file_name=f"subscription_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

def render_dashboard():
    """渲染完整仪表板"""
    st.title("📊 数据概览")

    if not st.session_state.current_user_id:
        st.warning("请先选择用户")
        return

    # 数据导出功能
    render_export_section()

    st.divider()

    # 指标概览
    render_subscription_metrics()

    st.divider()

    # 分类统计
    render_category_breakdown()

    st.divider()

    # 支出趋势分析
    render_spending_trends()

    st.divider()

    # 智能洞察
    render_quick_stats()

    st.divider()

    # 分类深度分析
    render_category_insights()

    st.divider()

    # 订阅列表
    render_subscription_list()

if __name__ == "__main__":
    # 测试组件
    render_dashboard()