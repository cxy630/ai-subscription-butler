"""
首页组件 - 欢迎页面和快速操作
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.database.data_interface import data_manager
from app.constants import CATEGORY_ICONS

def render_welcome_section():
    """渲染欢迎区域"""
    st.title("🏠 欢迎使用AI订阅管家")

    if st.session_state.current_user:
        user_name = st.session_state.current_user.get("name", "用户")
        current_hour = datetime.now().hour

        # 根据时间显示不同问候语
        if 5 <= current_hour < 12:
            greeting = "🌅 早上好"
        elif 12 <= current_hour < 18:
            greeting = "☀️ 下午好"
        else:
            greeting = "🌙 晚上好"

        st.markdown(f"## {greeting}, {user_name}!")
        st.markdown("**让我们一起管理您的订阅服务，节省时间和金钱。**")

    else:
        st.markdown("## 👋 欢迎！")
        st.markdown("**AI驱动的智能订阅管理助手**")

def render_quick_overview():
    """渲染快速概览"""
    if not st.session_state.current_user_id:
        return

    user_overview = data_manager.get_user_overview(st.session_state.current_user_id)
    if not user_overview:
        return

    st.subheader("📊 今日概览")

    # 主要指标
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"""
        **📱 活跃订阅**
        **{user_overview['active_subscriptions']}** 个服务
        总共 {user_overview['total_subscriptions']} 个订阅
        """)

    with col2:
        monthly_spending = user_overview['monthly_spending']
        yearly_estimate = monthly_spending * 12
        st.success(f"""
        **💰 月度支出**
        **¥{monthly_spending:.2f}**
        年度估算: ¥{yearly_estimate:.2f}
        """)

    with col3:
        categories_count = len(user_overview.get('subscription_categories', {}))
        st.warning(f"""
        **📂 服务类别**
        **{categories_count}** 个不同类别
        多样化的订阅组合
        """)

def render_recent_activity():
    """渲染最近活动"""
    if not st.session_state.current_user_id:
        return

    st.subheader("📈 最近活动")

    # 获取最近的订阅
    subscriptions = data_manager.get_user_subscriptions(st.session_state.current_user_id)
    if not subscriptions:
        st.info("暂无订阅记录")
        return

    # 按创建时间排序，获取最近的3个
    recent_subs = sorted(subscriptions, key=lambda x: x.get('created_at', ''), reverse=True)[:3]

    for sub in recent_subs:
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 2])

            with col1:
                category = sub.get('category', 'other')
                icon = CATEGORY_ICONS.get(category, '📦')
                st.markdown(f"## {icon}")

            with col2:
                service_name = sub.get('service_name', '未知服务')
                price = sub.get('price', 0)
                status = sub.get('status', 'active')

                st.markdown(f"**{service_name}**")
                st.caption(f"¥{price}/月 • {status}")

            with col3:
                created_at = sub.get('created_at', '')
                if created_at:
                    try:
                        # 解析创建时间
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        days_ago = (datetime.now() - created_date.replace(tzinfo=None)).days
                        if days_ago == 0:
                            time_str = "今天"
                        elif days_ago == 1:
                            time_str = "昨天"
                        else:
                            time_str = f"{days_ago}天前"
                        st.caption(f"添加于 {time_str}")
                    except:
                        st.caption("最近添加")

            st.divider()

def render_quick_actions():
    """渲染快速操作"""
    st.subheader("⚡ 快速操作")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("➕ 添加新订阅", use_container_width=True, type="primary"):
            st.session_state.show_add_subscription = True
            st.rerun()

        if st.button("📊 查看详细分析", use_container_width=True):
            st.session_state.current_page = "分析报告"
            st.rerun()

    with col2:
        if st.button("🤖 咨询AI助手", use_container_width=True):
            st.session_state.current_page = "AI助手"
            st.rerun()

        if st.button("📱 扫描账单", use_container_width=True):
            st.session_state.show_bill_scanner = True
            st.rerun()

    with col3:
        if st.button("🔍 搜索订阅", use_container_width=True):
            st.session_state.current_page = "数据概览"
            st.rerun()

        if st.button("⚙️ 系统设置", use_container_width=True):
            st.session_state.current_page = "设置"
            st.rerun()

def render_insights_preview():
    """渲染洞察预览"""
    if not st.session_state.current_user_id:
        return

    st.subheader("💡 智能洞察")

    user_overview = data_manager.get_user_overview(st.session_state.current_user_id)
    if not user_overview:
        return

    subscriptions = user_overview.get('subscriptions', [])
    monthly_spending = user_overview.get('monthly_spending', 0)
    categories = user_overview.get('subscription_categories', {})

    insights = []

    # 生成智能洞察
    if monthly_spending > 200:
        insights.append({
            "type": "warning",
            "icon": "⚠️",
            "title": "支出较高提醒",
            "content": f"您的月度订阅支出为¥{monthly_spending:.2f}，建议定期评估各服务的使用频率。"
        })

    if len(subscriptions) > 5:
        insights.append({
            "type": "info",
            "icon": "📱",
            "title": "订阅数量提醒",
            "content": f"您有{len(subscriptions)}个活跃订阅，可以考虑整合相似功能的服务。"
        })

    # 娱乐支出分析
    entertainment_cost = categories.get('entertainment', {}).get('spending', 0)
    if entertainment_cost > 50:
        insights.append({
            "type": "info",
            "icon": "🎬",
            "title": "娱乐支出分析",
            "content": f"娱乐类支出¥{entertainment_cost:.2f}/月，可以考虑选择性保留最常用的服务。"
        })

    # 显示洞察
    if insights:
        for insight in insights[:2]:  # 只显示前2个洞察
            icon = insight["icon"]
            title = insight["title"]
            content = insight["content"]

            if insight["type"] == "warning":
                st.warning(f"{icon} **{title}**\n\n{content}")
            else:
                st.info(f"{icon} **{title}**\n\n{content}")

        if len(insights) > 2:
            st.caption(f"还有{len(insights) - 2}个洞察，点击'分析报告'查看更多")
    else:
        st.success("✅ **订阅结构良好**\n\n您的订阅管理情况很不错，继续保持定期评估的习惯！")

def render_tips_section():
    """渲染使用技巧"""
    with st.expander("💡 使用技巧", expanded=False):
        st.markdown("""
        **🎯 如何更好地使用AI订阅管家：**

        1. **📱 定期添加订阅**
           - 每次新订阅服务时及时记录
           - 使用扫描账单功能快速添加

        2. **🤖 善用AI助手**
           - 询问具体的支出情况
           - 获取个性化的节省建议

        3. **📊 关注数据分析**
           - 定期查看分析报告
           - 关注支出趋势变化

        4. **🔄 定期清理**
           - 每月评估订阅使用情况
           - 及时取消不需要的服务

        5. **🎯 设置预算目标**
           - 为不同类别设置支出预算
           - 使用提醒功能避免超支
        """)

def render_home_page():
    """渲染完整的首页"""
    # 欢迎区域
    render_welcome_section()

    st.divider()

    # 快速概览
    render_quick_overview()

    st.divider()

    # 智能洞察
    render_insights_preview()

    st.divider()

    # 快速操作
    render_quick_actions()

    st.divider()

    # 最近活动
    render_recent_activity()

    # 使用技巧
    render_tips_section()

if __name__ == "__main__":
    # 测试组件
    render_home_page()