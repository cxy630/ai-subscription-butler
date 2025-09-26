"""
AI订阅管家 - Streamlit主应用
"""

import streamlit as st
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置页面配置
st.set_page_config(
    page_title="AI订阅管家",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/cxy630/ai-subscription-butler',
        'Report a bug': 'https://github.com/cxy630/ai-subscription-butler/issues',
        'About': "AI订阅管家 - 智能订阅管理助手"
    }
)

# 导入应用组件
try:
    from core.database.data_interface import data_manager
    from ui.components.dashboard import render_dashboard
    from ui.components.chat import render_chat_interface
    from ui.pages.home import render_home_page
    from ui.pages.analytics_page import render_analytics_page
    from ui.pages.settings_page import render_settings_page
    from app.constants import SUCCESS_MESSAGES, ERROR_MESSAGES
except ImportError as e:
    st.error(f"导入错误: {e}")
    st.stop()

# 初始化会话状态
def init_session_state():
    """初始化会话状态"""
    if "current_user_id" not in st.session_state:
        # 使用演示用户
        demo_user = data_manager.get_user_by_email("demo@example.com")
        if demo_user:
            st.session_state.current_user_id = demo_user["id"]
            st.session_state.current_user = demo_user
        else:
            st.session_state.current_user_id = None
            st.session_state.current_user = None

    if "current_page" not in st.session_state:
        st.session_state.current_page = "首页"

    if "chat_session_id" not in st.session_state:
        import uuid
        st.session_state.chat_session_id = str(uuid.uuid4())

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("💳 AI订阅管家")

        # 用户信息
        if st.session_state.current_user:
            user = st.session_state.current_user
            st.success(f"👋 欢迎，{user.get('name', '用户')}!")

            # 快速统计
            user_overview = data_manager.get_user_overview(st.session_state.current_user_id)
            if user_overview:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("订阅数", user_overview["total_subscriptions"])
                with col2:
                    st.metric("月支出", f"¥{user_overview['monthly_spending']:.2f}")
        else:
            st.warning("请先创建或选择用户")

        st.divider()

        # 导航菜单
        pages = {
            "🏠 首页": "首页",
            "📊 数据概览": "数据概览",
            "🤖 AI助手": "AI助手",
            "📈 分析报告": "分析报告",
            "⚙️ 设置": "设置"
        }

        for page_icon, page_name in pages.items():
            if st.sidebar.button(page_icon, use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()

        st.divider()

        # 快速操作
        st.subheader("⚡ 快速操作")

        if st.button("➕ 添加订阅", use_container_width=True):
            st.session_state.show_add_subscription = True
            st.rerun()

        if st.button("📱 扫描账单", use_container_width=True):
            st.session_state.show_bill_scanner = True
            st.rerun()

        # 系统信息
        st.divider()
        st.caption("💡 使用JSON文件存储")
        st.caption("🔄 支持实时数据同步")

def render_main_content():
    """渲染主要内容区域"""
    current_page = st.session_state.current_page

    if current_page == "首页":
        render_home_page()
    elif current_page == "数据概览":
        render_dashboard()
    elif current_page == "AI助手":
        render_chat_interface()
    elif current_page == "分析报告":
        render_analytics_page()
    elif current_page == "设置":
        render_settings_page()
    else:
        st.error(f"未知页面: {current_page}")

def render_add_subscription_modal():
    """渲染添加订阅弹窗"""
    if st.session_state.get("show_add_subscription", False):
        with st.form("add_subscription_form"):
            st.subheader("➕ 添加新订阅")

            col1, col2 = st.columns(2)
            with col1:
                service_name = st.text_input("服务名称", placeholder="例如: Netflix")
                price = st.number_input("价格", min_value=0.01, value=15.99, step=0.01)

            with col2:
                billing_cycle = st.selectbox("付费周期",
                    ["monthly", "yearly", "weekly", "daily"],
                    format_func=lambda x: {
                        "monthly": "月付", "yearly": "年付",
                        "weekly": "周付", "daily": "日付"
                    }[x])

                category = st.selectbox("分类", [
                    "entertainment", "productivity", "health_fitness",
                    "education", "business", "gaming", "other"
                ], format_func=lambda x: {
                    "entertainment": "娱乐", "productivity": "生产力",
                    "health_fitness": "健康健身", "education": "教育",
                    "business": "商务", "gaming": "游戏", "other": "其他"
                }[x])

            notes = st.text_area("备注", placeholder="可选备注信息")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.form_submit_button("✅ 添加", use_container_width=True):
                    if service_name and price > 0:
                        subscription_data = {
                            "service_name": service_name,
                            "price": price,
                            "currency": "CNY",
                            "billing_cycle": billing_cycle,
                            "category": category,
                            "status": "active",
                            "notes": notes or None
                        }

                        result = data_manager.create_subscription(
                            st.session_state.current_user_id,
                            subscription_data
                        )

                        if result:
                            st.success(f"✅ 成功添加订阅: {service_name}")
                            st.session_state.show_add_subscription = False
                            st.rerun()
                        else:
                            st.error("❌ 添加订阅失败")
                    else:
                        st.error("❌ 请填写完整信息")

            with col2:
                if st.form_submit_button("❌ 取消", use_container_width=True):
                    st.session_state.show_add_subscription = False
                    st.rerun()

def main():
    """主函数"""
    try:
        # 初始化
        init_session_state()

        # 检查是否有用户
        if not st.session_state.current_user:
            st.error("❌ 未找到演示用户，请运行存储演示脚本创建数据")
            st.code("python scripts/storage_demo.py")
            st.stop()

        # 渲染界面
        render_sidebar()

        # 主内容区域
        render_main_content()

        # 模态窗口
        render_add_subscription_modal()

        # 页脚
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("🤖 基于Claude Code构建")
        with col2:
            st.caption("💾 JSON文件存储")
        with col3:
            st.caption("🔄 实时更新")

    except Exception as e:
        st.error(f"应用启动错误: {e}")
        st.exception(e)

if __name__ == "__main__":
    main()