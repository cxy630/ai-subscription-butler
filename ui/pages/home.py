"""
首页组件 - 欢迎页面和快速操作
(Redesigned: Savings War Room)
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import asyncio

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.database.data_interface import data_manager
from core.ai import get_ai_assistant, is_ai_assistant_available
from core.agents.optimization_agent import OptimizationAgent
from core.agents.base_agent import AgentContext
from app.constants import CATEGORY_ICONS
from ui.components.activity_stream import render_recent_activity_stream

def render_hero_section():
    """
    渲染顶部 'Hero Section'
    核心目标：展示 AI 带来的财务价值（省钱金额）
    """
    if not st.session_state.current_user_id:
        return

    # 获取实时节省数据
    user_id = st.session_state.current_user_id
    subscriptions = data_manager.get_active_subscriptions(user_id)
    
    # 临时计算节省潜力（如果不通过 Agent 走全流程，就用快速估算）
    # 这里我们复用 Agent 逻辑来获取真实数据
    opt_agent = OptimizationAgent()
    context = AgentContext(
        user_id=user_id,
        subscriptions=subscriptions,
        user_preferences={},
        automation_level="manual"
    )
    
    # 异步获取结果
    try:
        results = asyncio.run(opt_agent.find_savings_opportunities(context))
        potential_savings = results.get("total_savings_potential", 0)
        opportunities_count = results.get("opportunities_count", 0)
    except Exception as e:
        potential_savings = 0
        opportunities_count = 0
    
    # 布局：左侧大数字，右侧状态
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💰 本月潜在节省")
        if potential_savings > 0:
            st.markdown(f"""
            <h1 style='color: #2ecc71; font-size: 3.5rem; margin-top: -20px;'>
                ¥{potential_savings:.2f}
            </h1>
            """, unsafe_allow_html=True)
            st.caption(f"🚀 AI 发现了 {opportunities_count} 个可优化项，建议立即行动。")
        else:
            st.markdown(f"""
            <h1 style='color: #3498db; font-size: 3.5rem; margin-top: -20px;'>
                ¥0.00
            </h1>
            """, unsafe_allow_html=True)
            st.caption("✨ 您的订阅组合非常健康，暂无明显浪费。")

    with col2:
        st.info("🤖 **AI 管家状态**")
        st.markdown("**🟢 实时监控中**")
        st.markdown(f"上次扫描: {datetime.now().strftime('%H:%M')}")
        st.markdown(f"活跃订阅: {len(subscriptions)} 个")

def render_action_center():
    """
    渲染 '行动中心'
    直接展示 Top 3 谈判/省钱建议，提供快速入口
    """
    if not st.session_state.current_user_id:
        return

    st.subheader("🔥 待处理建议 (Action Center)")
    
    # 获取建议
    user_id = st.session_state.current_user_id
    subscriptions = data_manager.get_active_subscriptions(user_id)
    opt_agent = OptimizationAgent()
    context = AgentContext(user_id=user_id, subscriptions=subscriptions, user_preferences={})
    
    try:
        results = asyncio.run(opt_agent.find_savings_opportunities(context))
        opportunities = results.get("opportunities", [])
    except:
        opportunities = []

    if not opportunities:
        st.success("🎉 目前没有紧急行动项，您可以去喝杯咖啡了！")
        return

    # 展示 Top 3
    for opp in opportunities[:3]:
        with st.container():
            col_icon, col_info, col_action = st.columns([0.5, 3, 1])
            
            with col_icon:
                st.markdown("## 💡")
            
            with col_info:
                st.markdown(f"**{opp.get('description', '省钱机会')}**")
                st.caption(f"可节省: ¥{opp.get('savings_potential', 0):.2f}/月 | 优先级: {opp.get('severity', 'normal')}")
                
            with col_action:
                # 直接跳转到谈判页面的逻辑
                sub_id = opp.get("subscription_id")
                if sub_id:
                    if st.button("🤝 解决", key=f"home_solve_{sub_id}"):
                        st.session_state.current_page = "AI洞察"
                        st.session_state.negotiation_sub_id = sub_id
                        st.rerun()
            
            st.divider()
    
    if len(opportunities) > 3:
        if st.button("查看全部建议", use_container_width=True):
            st.session_state.current_page = "AI洞察"
            st.rerun()

def render_quick_entry_points():
    """
    渲染快速功能入口（一行图标）
    """
    cols = st.columns(4)
    with cols[0]:
        if st.button("➕ 记一笔", use_container_width=True):
            st.session_state.show_add_subscription = True
            st.rerun()
    with cols[1]:
        if st.button("📱 扫账单", use_container_width=True):
            st.session_state.show_bill_scanner = True
            st.rerun()
    with cols[2]:
        if st.button("📊 看报表", use_container_width=True):
            st.session_state.current_page = "分析报告"
            st.rerun()
    with cols[3]:
        if st.button("⚙️ 设置", use_container_width=True):
            st.session_state.current_page = "设置"
            st.rerun()

def render_home_page():
    """渲染完整的首页 (Savings War Room 版)"""
    
    # 1. 顶部：省钱大数字
    render_hero_section()
    
    st.divider()
    
    # 2. 中部：快速行动建议
    render_action_center()
    
    st.divider()
    
    # 3. 功能入口
    render_quick_entry_points()
    
    st.divider()
    
    # 4. 底部：AI 实时工作流（增强活跃感）
    render_recent_activity_stream(limit=3)

if __name__ == "__main__":
    render_home_page()