"""
AI洞察仪表板 - 展示AI管家的分析和建议
"""

import streamlit as st
from datetime import datetime
import asyncio
from core.database.data_interface import data_manager
from core.agents.butler_agent import ButlerAgent
from core.agents.base_agent import AgentContext


def render_ai_insights_page():
    """渲染AI洞察页面"""
    st.title("🤖 AI管家洞察")

    st.markdown("""
    AI管家每天分析您的订阅，提供智能建议和预警。
    """)

    # 获取用户和订阅数据
    user = data_manager.get_user_by_id(st.session_state.current_user_id)
    if not user:
        st.error("❌ 无法加载用户数据")
        return

    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)

    # 创建Agent上下文
    automation_prefs = user.get("automation_preferences", {})
    context = AgentContext(
        user_id=st.session_state.current_user_id,
        subscriptions=subscriptions,
        user_preferences=user.get("notification_preferences", {}),
        automation_level=automation_prefs.get("automation_level", "manual"),
        budget_limit=automation_prefs.get("budget_limit")
    )

    # === 快速操作按钮 ===
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔍 立即扫描", use_container_width=True, type="primary"):
            with st.spinner("AI管家正在扫描订阅..."):
                butler = ButlerAgent()

                # 使用asyncio运行异步任务
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        butler.monitoring_agent.scan_all_subscriptions(context)
                    )
                    st.session_state.last_scan_result = result
                    st.session_state.last_scan_time = datetime.now()
                    st.success("✅ 扫描完成!")
                    st.rerun()
                finally:
                    loop.close()

    with col2:
        if st.button("📊 生成洞察", use_container_width=True):
            # 清除旧的缓存数据
            if "insights_result" in st.session_state:
                del st.session_state.insights_result

            with st.spinner("AI管家正在分析..."):
                butler = ButlerAgent()

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        butler.generate_insights(context)
                    )
                    st.session_state.insights_result = result
                    st.success("✅ 分析完成!")
                    st.rerun()
                finally:
                    loop.close()

    with col3:
        if st.button("💰 成本分析", use_container_width=True):
            with st.spinner("分析成本结构..."):
                butler = ButlerAgent()

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        butler.optimization_agent.analyze_costs(context)
                    )
                    st.session_state.cost_analysis_result = result
                    st.success("✅ 成本分析完成!")
                    st.rerun()
                finally:
                    loop.close()

    with col4:
        if st.button("💡 省钱建议", use_container_width=True):
            with st.spinner("寻找省钱机会..."):
                butler = ButlerAgent()

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        butler.optimization_agent.find_savings_opportunities(context)
                    )
                    st.session_state.savings_result = result
                    st.success(f"✅ 找到 {len(result.get('opportunities', []))} 个省钱机会!")
                    st.rerun()
                finally:
                    loop.close()

    # === 谈判策略 (如果选择了特定订阅) ===
    if st.session_state.get("negotiation_sub_id"):
        sub_id = st.session_state.negotiation_sub_id
        subscription = next((s for s in subscriptions if s["id"] == sub_id), None)
        
        if subscription:
            st.info(f"🤝 **谈判助手**: 正在为 **{subscription['service_name']}** 制定策略")
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                if st.button("🚀 生成策略", use_container_width=True, type="primary"):
                    with st.spinner("寻找筹码中..."):
                        butler = ButlerAgent()
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            result = loop.run_until_complete(
                                butler.execute_task({"type": "generate_negotiation_strategy", "subscription_id": sub_id}, context)
                            )
                            st.session_state.negotiation_strategy = result
                        finally:
                            loop.close()
            with col_n2:
                if st.button("❌ 关闭谈判助手", use_container_width=True):
                    del st.session_state.negotiation_sub_id
                    if "negotiation_strategy" in st.session_state: del st.session_state.negotiation_strategy
                    if "negotiation_draft" in st.session_state: del st.session_state.negotiation_draft
                    st.rerun()
            
            if st.session_state.get("negotiation_strategy"):
                strat = st.session_state.negotiation_strategy
                if strat.get("status") == "success":
                    st.success("✅ 策略生成成功")
                    st.markdown("### 📋 建议策略")
                    st.write(strat.get("strategy_text"))
                    
                    if st.button("✉️ 起草联系消息", use_container_width=True):
                        with st.spinner("起草消息中..."):
                            butler = ButlerAgent()
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                draft_result = loop.run_until_complete(
                                    butler.execute_task({
                                        "type": "draft_negotiation_message", 
                                        "strategy": strat.get("strategy_text")
                                    }, context)
                                )
                                st.session_state.negotiation_draft = draft_result
                            finally:
                                loop.close()
                    
                    if st.session_state.get("negotiation_draft"):
                        draft = st.session_state.negotiation_draft
                        if draft.get("status") == "success":
                            st.markdown("### ✉️ 消息初稿")
                            st.code(draft.get("draft_text"), language="markdown")
                else:
                    st.error(f"❌ 出错: {strat.get('message')}")

    st.divider()

    # === 最近扫描结果 ===
    if st.session_state.get("last_scan_result"):
        st.subheader("🔍 最近扫描结果")

        scan_result = st.session_state.last_scan_result
        scan_time = st.session_state.get("last_scan_time", datetime.now())

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("扫描时间", scan_time.strftime("%H:%M:%S"))
        with col2:
            st.metric("订阅数量", scan_result.get("subscriptions_count", 0))
        with col3:
            issues_count = len(scan_result.get("issues", []))
            st.metric("发现问题", issues_count, delta=f"{issues_count} 个")

        # 显示问题列表
        issues = scan_result.get("issues", [])
        if issues:
            st.warning(f"⚠️ 发现 {len(issues)} 个需要关注的问题:")

            issue_type_display = {
                "renewal_alert": "🔔 续费提醒",
                "renewal_urgent": "🚨 紧急续费",
                "cost_warning": "💰 成本警告",
                "cost_alert": "💰 成本提醒",
                "high_cost": "💎 高成本",
                "unused": "⚠️ 未使用",
                "duplicate": "🔄 重复服务",
                "budget_exceeded": "💸 预算超支"
            }

            for i, issue in enumerate(issues, 1):
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                emoji = severity_emoji.get(issue.get("severity", "low"), "⚪")

                issue_type = issue.get('type', '未知')
                issue_type_text = issue_type_display.get(issue_type, issue_type)

                with st.expander(f"{emoji} {issue_type_text} - {issue.get('service_name', '未知服务')}"):
                    severity_display = {"high": "高", "medium": "中", "low": "低"}
                    st.markdown(f"**严重程度**: {severity_display.get(issue.get('severity', 'low'), '未知')}")
                    st.markdown(f"**消息**: {issue.get('message', '无详情')}")
                    if issue.get("next_billing_date"):
                        st.markdown(f"**下次续费**: {issue.get('next_billing_date')}")
                    if issue.get("amount"):
                        st.markdown(f"**金额**: ¥{issue.get('amount')}")
        else:
            st.success("✅ 未发现任何问题，所有订阅运行正常!")

        # 显示洞察
        insights = scan_result.get("insights", [])
        if insights:
            st.info("💡 AI洞察:")
            for insight in insights:
                st.markdown(f"- {insight}")

    # === 智能洞察 ===
    if st.session_state.get("insights_result"):
        st.subheader("💡 智能洞察与建议")

        insights_result = st.session_state.insights_result
        insights = insights_result.get("insights", [])

        if insights:
            type_display = {
                "warning": "⚠️ 警告",
                "suggestion": "💡 建议",
                "info": "ℹ️ 信息",
                "cost_alert": "💰 成本提醒",
                "cost_warning": "💰 成本警告",
                "high_cost_subscriptions": "💸 高成本订阅",
                "category_redundancy": "📦 分类冗余",
                "renewal_alert": "🔔 续费提醒",
                "renewal_urgent": "🚨 紧急续费",
                "optimization": "⚡ 优化建议",
                "duplicate_service": "🔄 重复服务",
                "unused_subscription": "⚠️ 未使用订阅",
                "budget_exceeded": "💸 预算超支"
            }

            import json

            for i, insight in enumerate(insights, 1):
                if isinstance(insight, dict):
                    severity_color = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢"
                    }
                    color = severity_color.get(insight.get("severity", "low"), "💡")
                    insight_type = insight.get('type', '')
                    message = insight.get('message', '')

                    # 如果type在映射字典中，显示映射后的中文类型
                    if insight_type in type_display:
                        type_text = type_display[insight_type]
                        st.markdown(f"{color} **{type_text}**: {message}")
                    else:
                        # 如果type不在映射字典中，只显示message
                        st.markdown(f"{color} {message}")
                elif isinstance(insight, str):
                    # 尝试解析可能的JSON字符串
                    try:
                        parsed = json.loads(insight)
                        if isinstance(parsed, dict) and "suggestions" in parsed:
                            # 如果是suggestions格式，展开显示每个建议
                            for suggestion in parsed["suggestions"]:
                                st.markdown(f"💡 {suggestion}")
                            continue  # 跳过后面的显示
                        else:
                            # 解析成功但不是suggestions格式
                            st.markdown(f"💡 {insight}")
                    except (json.JSONDecodeError, TypeError):
                        # 不是JSON，检查是否是 "type: message" 格式
                        if ": " in insight:
                            parts = insight.split(": ", 1)
                            if len(parts) == 2:
                                insight_type, message = parts
                                # 使用type映射
                                if insight_type in type_display:
                                    type_text = type_display[insight_type]
                                    st.markdown(f"💡 **{type_text}**: {message}")
                                else:
                                    st.markdown(f"💡 {insight}")
                            else:
                                st.markdown(f"💡 {insight}")
                        else:
                            st.markdown(f"💡 {insight}")
                else:
                    st.markdown(f"💡 {insight}")
        else:
            st.info("暂无特殊洞察")

        # 优先行动项
        priority_actions = insights_result.get("priority_actions", [])
        if priority_actions:
            st.markdown("### ⚡ 优先行动项")
            action_type_display = {
                "review": "📋 审查",
                "cancel": "❌ 取消",
                "optimize": "⚡ 优化",
                "upgrade": "⬆️ 升级",
                "downgrade": "⬇️ 降级",
                "switch": "🔄 切换",
                "cost_warning": "💰 成本警告",
                "cost_alert": "💰 成本提醒",
                "renewal_alert": "🔔 续费提醒",
                "renewal_urgent": "🚨 紧急续费",
                "duplicate_service": "🔄 重复服务",
                "unused_subscription": "⚠️ 未使用订阅",
                "budget_exceeded": "💸 预算超支",
                "high_cost_review": "💎 高成本审查",
                "high_cost_subscriptions": "💸 高成本订阅",
                "budget_cut": "✂️ 预算削减",
                "category_concentration": "📦 分类集中",
                "category_redundancy": "📦 分类冗余"
            }

            for action in priority_actions[:5]:  # 只显示前5个
                if isinstance(action, dict):
                    action_type = action.get('type', '行动')
                    type_text = action_type_display.get(action_type, "⚡ " + action_type)
                    st.markdown(f"- **{type_text}**: {action.get('message', '')}")
                else:
                    st.markdown(f"- {action}")

    # === 成本分析结果 ===
    if st.session_state.get("cost_analysis_result"):
        st.subheader("💰 成本分析报告")

        cost_result = st.session_state.cost_analysis_result

        if cost_result.get("status") == "success":
            # 总成本展示
            col1, col2, col3 = st.columns(3)

            with col1:
                total_monthly = cost_result.get("total_monthly_cost", {})
                cny_cost = total_monthly.get("CNY", 0)
                st.metric("月度总支出", f"¥{cny_cost:.2f}")

            with col2:
                avg_cost = cost_result.get("average_cost_per_subscription", 0)
                st.metric("平均每个订阅", f"¥{avg_cost:.2f}")

            with col3:
                cycle_breakdown = cost_result.get("cost_by_billing_cycle", {})
                most_common_cycle = max(cycle_breakdown.items(), key=lambda x: x[1]["count"])[0] if cycle_breakdown else "N/A"
                cycle_display = {"monthly": "月付", "yearly": "年付", "weekly": "周付"}.get(most_common_cycle, most_common_cycle)
                st.metric("最常用周期", cycle_display)

            # 按分类成本
            category_costs = cost_result.get("cost_by_category", {})
            if category_costs:
                st.markdown("### 📊 分类成本分布")

                category_display = {
                    "entertainment": "🎬 娱乐",
                    "productivity": "💼 生产力",
                    "storage": "☁️ 存储",
                    "education": "📚 教育",
                    "health_fitness": "💪 健康",
                    "business": "💼 商务",
                    "other": "📦 其他"
                }

                # 创建可视化数据
                sorted_categories = sorted(category_costs.items(), key=lambda x: x[1]["total_cost"], reverse=True)

                for category, data in sorted_categories[:5]:  # 显示前5个
                    display_name = category_display.get(category, category)
                    cost = data["total_cost"]
                    count = data["count"]
                    percentage = data.get("percentage", 0)

                    st.markdown(f"**{display_name}**: ¥{cost:.2f} ({count}个订阅) - {percentage:.1f}%")
                    st.progress(percentage / 100)

            # 趋势分析
            trends = cost_result.get("trends", {})
            if trends:
                st.markdown("### 📈 趋势洞察")
                for trend in trends.get("insights", []):
                    st.info(f"💡 {trend}")

    # === 省钱建议 ===
    if st.session_state.get("savings_result"):
        st.subheader("💡 省钱机会")

        savings_result = st.session_state.savings_result

        if savings_result.get("status") == "success":
            opportunities = savings_result.get("opportunities", [])
            total_potential = savings_result.get("total_savings_potential", 0)

            # 总省钱潜力
            if total_potential > 0:
                st.success(f"🎉 发现潜在年度节省: ¥{total_potential:.2f}")

            if opportunities:
                st.markdown("### 💰 具体建议")

                # 按优先级排序
                priority_order = {"high": 0, "medium": 1, "low": 2}
                sorted_opportunities = sorted(
                    opportunities,
                    key=lambda x: (priority_order.get(x.get("severity", "low"), 3), -x.get("savings_potential", 0))
                )

                for i, opp in enumerate(sorted_opportunities[:10], 1):  # 显示前10个
                    priority = opp.get("severity", "low")  # 使用severity字段
                    opp_type = opp.get("type", "未知")
                    message = opp.get("description", "")  # 使用description字段
                    savings = opp.get("savings_potential", 0)  # 使用savings_potential字段

                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    emoji = priority_emoji.get(priority, "⚪")

                    type_display_map = {
                        "duplicate": "🔄 重复服务",
                        "duplicate_service": "🔄 重复服务",
                        "unused": "⚠️ 未使用订阅",
                        "unused_subscription": "⚠️ 未使用订阅",
                        "annual_discount": "💰 年付优惠",
                        "annual_billing_discount": "💰 年付优惠",
                        "budget_exceeded": "💸 预算超支",
                        "high_cost": "💎 高成本订阅",
                        "high_cost_review": "💎 高成本审查",
                        "budget_cut": "✂️ 预算削减",
                        "category_concentration": "📦 分类集中"
                    }
                    type_display_text = type_display_map.get(opp_type, "💡 " + opp_type)

                    # 对于月度成本，显示月度节省；对于年度成本，显示年度节省
                    savings_label = f"可省¥{savings:.2f}/月"
                    if "annual" in opp_type or opp_type == "annual_billing_discount":
                        savings_label = f"可省¥{savings:.2f}/年"

                    with st.expander(f"{emoji} {type_display_text} - {savings_label}"):
                        priority_display = {"high": "高", "medium": "中", "low": "低"}
                        st.markdown(f"**优先级**: {priority_display.get(priority, '未知')}")
                        st.markdown(f"**详情**: {message}")

                        # 显示建议
                        if "recommendation" in opp:
                            st.markdown(f"**建议**: {opp['recommendation']}")

                        # 如果有服务名称，显示
                        if "service" in opp:
                            st.markdown(f"**服务**: {opp['service']}")

                        # 如果有相关服务列表，显示
                        if "services" in opp:
                            st.markdown(f"**相关服务**: {', '.join(opp['services'][:5])}")
                        
                        # 谈判功能入口
                        sub_id = opp.get("subscription_id")
                        if sub_id:
                            if st.button("🤝 获取谈判策略", key=f"neg_btn_{sub_id}_{i}"):
                                st.session_state.negotiation_sub_id = sub_id
                                # 清除之前的策略缓存以防混淆
                                if "negotiation_strategy" in st.session_state: del st.session_state.negotiation_strategy
                                if "negotiation_draft" in st.session_state: del st.session_state.negotiation_draft
                                st.rerun()
            else:
                st.info("🎉 暂未发现明显的省钱机会，您的订阅管理很健康！")

    # === 每日检查报告 ===
    if st.session_state.get("daily_checkup_result"):
        st.subheader("📈 每日检查报告")

        checkup = st.session_state.daily_checkup_result

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_cost = checkup.get("total_monthly_cost", {})
            cny_cost = total_cost.get("CNY", 0)
            st.metric("月度支出 (CNY)", f"¥{cny_cost:.2f}")

        with col2:
            scan_data = checkup.get("scan_results", {})
            issues_count = len(scan_data.get("issues", []))
            st.metric("发现问题", issues_count)

        with col3:
            renewal_data = checkup.get("upcoming_renewals", {})
            renewals_count = len(renewal_data.get("upcoming_renewals", []))
            st.metric("即将续费", renewals_count)

        with col4:
            action_items = checkup.get("action_items", [])
            st.metric("行动项", len(action_items))

        # 即将续费的订阅
        renewals = renewal_data.get("upcoming_renewals", [])
        if renewals:
            st.markdown("### 📅 即将续费的订阅")
            for renewal in renewals:
                days = renewal.get("days_until_renewal", 0)
                color = "🔴" if days <= 3 else "🟡" if days <= 7 else "🟢"
                st.markdown(
                    f"{color} **{renewal.get('service_name')}** - "
                    f"{days} 天后续费 (¥{renewal.get('amount', 0)})"
                )

        # 行动项
        if action_items:
            st.markdown("### ⚡ 需要采取的行动")
            for item in action_items:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                emoji = priority_emoji.get(item.get("priority", "low"), "⚪")
                st.markdown(f"{emoji} {item.get('description', '无描述')}")

    # === 订阅健康概览 ===
    st.divider()
    st.subheader("📊 订阅健康概览")

    if subscriptions:
        # 按分类统计
        category_stats = {}
        for sub in subscriptions:
            category = sub.get("category", "other")
            if category not in category_stats:
                category_stats[category] = {"count": 0, "total_cost": 0}
            category_stats[category]["count"] += 1
            category_stats[category]["total_cost"] += sub.get("price", 0)

        # 显示统计卡片
        cols = st.columns(min(len(category_stats), 4))
        category_display = {
            "entertainment": "🎬 娱乐",
            "productivity": "💼 生产力",
            "storage": "☁️ 存储",
            "education": "📚 教育",
            "health_fitness": "💪 健康",
            "business": "💼 商务",
            "other": "📦 其他"
        }

        for i, (category, stats) in enumerate(category_stats.items()):
            with cols[i % 4]:
                display_name = category_display.get(category, category)
                st.metric(
                    display_name,
                    f"{stats['count']} 个",
                    delta=f"¥{stats['total_cost']:.2f}/月"
                )

    else:
        st.info("暂无活跃订阅")

    st.divider()

    # 返回按钮
    if st.button("🔙 返回首页", use_container_width=True):
        st.session_state.current_page = "首页"
        st.rerun()


if __name__ == "__main__":
    render_ai_insights_page()
