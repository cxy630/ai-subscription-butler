"""
AI订阅管家 - Streamlit主应用
"""

import streamlit as st
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 确保环境变量被正确加载
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

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
    from ui.components.reminders import render_reminders_page, render_reminder_banner
    from ui.pages.home import render_home_page
    from ui.pages.analytics_page import render_analytics_page
    from ui.pages.settings_page import render_settings_page
    from ui.pages.add_subscription_page import render_add_subscription_page
    from ui.pages.template_page import render_template_page
    from ui.pages.scan_bill_page import render_scan_bill_page
    from ui.pages.automation_settings_page import render_automation_settings_page
    from ui.pages.ai_insights_page import render_ai_insights_page
    from ui.pages.agent_activity_page import render_agent_activity_page
    from ui.pages.auth_page import render_auth_page
    from app.constants import SUCCESS_MESSAGES, ERROR_MESSAGES
except ImportError as e:
    st.error(f"导入错误: {e}")
    st.stop()

# 初始化会话状态
def init_session_state():
    """初始化会话状态"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "current_user_id" not in st.session_state:
        st.session_state.current_user_id = None

    if "current_user" not in st.session_state:
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
            "🔔 订阅提醒": "订阅提醒",
            "🤖 AI助手": "AI助手",
            "🧠 AI洞察": "AI洞察",
            "🤵 AI管家设置": "AI管家设置",
            "📋 Agent活动": "Agent活动",
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
            st.session_state.current_page = "添加订阅"
            st.rerun()

        if st.button("📋 从模板添加", use_container_width=True):
            st.session_state.current_page = "从模板添加"
            st.rerun()

        if st.button("📱 扫描账单", use_container_width=True):
            st.session_state.current_page = "扫描账单"
            st.rerun()

        # 退出登录
        st.divider()
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user_id = None
            st.session_state.current_user = None
            st.session_state.current_page = "首页"
            st.rerun()

        # 系统信息
        st.caption("💡 使用SQLite数据库")
        st.caption("🔄 支持实时数据同步")

def render_main_content():
    """渲染主要内容区域"""
    # 在所有页面顶部显示提醒横幅
    render_reminder_banner()

    current_page = st.session_state.current_page

    if current_page == "首页":
        render_home_page()
    elif current_page == "数据概览":
        render_dashboard()
    elif current_page == "订阅提醒":
        render_reminders_page()
    elif current_page == "AI助手":
        render_chat_interface()
    elif current_page == "分析报告":
        render_analytics_page()
    elif current_page == "设置":
        render_settings_page()
    elif current_page == "添加订阅":
        render_add_subscription_page()
    elif current_page == "从模板添加":
        render_template_page()
    elif current_page == "扫描账单":
        render_scan_bill_page()
    elif current_page == "AI管家设置":
        render_automation_settings_page()
    elif current_page == "AI洞察":
        render_ai_insights_page()
    elif current_page == "Agent活动":
        render_agent_activity_page()
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
                    "education", "business", "storage", "other"
                ], format_func=lambda x: {
                    "entertainment": "娱乐", "productivity": "生产力",
                    "health_fitness": "健康健身", "education": "教育",
                    "business": "商务", "storage": "存储", "other": "其他"
                }[x])

            col1, col2 = st.columns(2)
            with col1:
                from datetime import datetime
                start_date = st.date_input(
                    "开始日期",
                    value=datetime.now(),
                    help="首次订阅或上次续费的日期"
                )
            with col2:
                st.caption("💡 提示")
                st.caption("系统将根据此日期计算续费提醒")

            notes = st.text_area("备注", placeholder="可选备注信息")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.form_submit_button("✅ 添加", use_container_width=True):
                    if service_name and price > 0:
                        from datetime import datetime
                        subscription_data = {
                            "service_name": service_name,
                            "price": price,
                            "currency": "CNY",
                            "billing_cycle": billing_cycle,
                            "category": category,
                            "status": "active",
                            "start_date": datetime.combine(start_date, datetime.min.time()).isoformat(),
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

def render_bill_scanner_modal():
    """渲染账单扫描弹窗"""
    if st.session_state.get("show_bill_scanner", False):
        st.subheader("📱 账单扫描")

        # 文件上传
        uploaded_file = st.file_uploader(
            "上传账单图片",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="支持PNG、JPG、JPEG、PDF格式"
        )

        if uploaded_file is not None:
            # 显示上传的文件信息
            st.info(f"已上传文件: {uploaded_file.name} ({uploaded_file.size} bytes)")

            # 如果是图片，显示预览
            if uploaded_file.type in ['image/png', 'image/jpg', 'image/jpeg']:
                st.image(uploaded_file, caption="账单预览", use_container_width=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("🔍 开始识别", use_container_width=True):
                    with st.spinner("正在识别账单内容..."):
                        try:
                            # 使用Gemini OCR识别账单
                            from core.ai import get_gemini_client, is_gemini_available

                            if is_gemini_available():
                                gemini_client = get_gemini_client()

                                # 读取文件内容
                                file_bytes = uploaded_file.read()
                                file_type = uploaded_file.type

                                # 调用Gemini OCR
                                ocr_result = gemini_client.analyze_bill_image(file_bytes, file_type)

                                if ocr_result and ocr_result.get("success"):
                                    st.success("✅ 识别完成！")

                                    # 保存识别结果到session state
                                    st.session_state.ocr_result = ocr_result
                                    st.session_state.ocr_step = "confirm"
                                else:
                                    st.warning("⚠️ OCR识别失败，使用模拟结果")
                                    # 模拟识别结果
                                    mock_result = {
                                        "success": True,
                                        "confidence": 0.8,
                                        "extracted_data": {
                                            "service_name": "Netflix",
                                            "amount": "15.99",
                                            "currency": "USD",
                                            "billing_date": "2024-01-15",
                                            "billing_cycle": "monthly"
                                        },
                                        "raw_text": "Netflix 订阅服务\n月费: $15.99\n账单日期: 2024-01-15\n下次扣费: 2024-02-15",
                                        "description": "检测到Netflix流媒体服务的月度订阅账单，月费15.99美元。"
                                    }
                                    st.session_state.ocr_result = mock_result
                                    st.session_state.ocr_step = "confirm"
                            else:
                                st.warning("⚠️ Gemini API不可用，使用模拟结果")
                                # 模拟识别结果
                                mock_result = {
                                    "success": True,
                                    "confidence": 0.8,
                                    "extracted_data": {
                                        "service_name": "Netflix",
                                        "amount": "15.99",
                                        "currency": "USD",
                                        "billing_date": "2024-01-15",
                                        "billing_cycle": "monthly"
                                    },
                                    "raw_text": "Netflix 订阅服务\n月费: $15.99\n账单日期: 2024-01-15\n下次扣费: 2024-02-15",
                                    "description": "检测到Netflix流媒体服务的月度订阅账单，月费15.99美元。"
                                }
                                st.session_state.ocr_result = mock_result
                                st.session_state.ocr_step = "confirm"

                        except Exception as e:
                            st.error(f"❌ OCR识别出错: {str(e)}")
                            # 错误时的模拟结果
                            mock_result = {
                                "success": True,
                                "confidence": 0.6,
                                "extracted_data": {
                                    "service_name": "未知服务",
                                    "amount": "0.00",
                                    "currency": "CNY",
                                    "billing_date": "",
                                    "billing_cycle": "monthly"
                                },
                                "raw_text": "识别失败，请手动输入信息",
                                "description": "OCR识别遇到问题，请手动检查并输入正确信息。"
                            }
                            st.session_state.ocr_result = mock_result
                            st.session_state.ocr_step = "confirm"

                        st.rerun()

            # 显示识别内容确认步骤
            if st.session_state.get("ocr_step") == "confirm" and st.session_state.get("ocr_result"):
                ocr_result = st.session_state.ocr_result

                st.subheader("📋 识别结果确认")

                # 显示识别概述
                col_desc1, col_desc2 = st.columns([2, 1])
                with col_desc1:
                    st.info(f"📄 **识别描述**: {ocr_result.get('description', '已识别账单内容')}")
                with col_desc2:
                    confidence = ocr_result.get('confidence', 0.8)
                    confidence_color = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🔴"
                    st.metric("识别准确度", f"{confidence:.1%}", delta=f"{confidence_color}")

                # 显示原始识别文本
                with st.expander("🔍 查看原始识别文本", expanded=False):
                    raw_text = ocr_result.get('raw_text', '无识别文本')
                    st.text_area("原始文本", value=raw_text, height=100, disabled=True)

                # 确认按钮
                col_confirm1, col_confirm2, col_confirm3 = st.columns(3)
                with col_confirm1:
                    if st.button("✅ 确认识别结果", use_container_width=True, type="primary"):
                        st.session_state.ocr_step = "form"
                        st.session_state.recognized_data = ocr_result.get("extracted_data", {})
                        st.rerun()

                with col_confirm2:
                    if st.button("✏️ 重新识别", use_container_width=True):
                        if "ocr_result" in st.session_state:
                            del st.session_state.ocr_result
                        if "ocr_step" in st.session_state:
                            del st.session_state.ocr_step
                        st.rerun()

                with col_confirm3:
                    if st.button("📝 手动输入", use_container_width=True):
                        st.session_state.ocr_step = "form"
                        st.session_state.recognized_data = {
                            "service_name": "",
                            "amount": 0.0,
                            "currency": "CNY",
                            "billing_cycle": "monthly"
                        }
                        st.rerun()

            # 显示表单填写步骤
            if st.session_state.get("ocr_step") == "form":
                recognized_data = st.session_state.get("recognized_data", {})
                st.subheader("📋 确认订阅信息")

                with st.form("ocr_result_form"):
                    st.write("请确认识别结果并编辑：")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        service_name = st.text_input("服务名称", value=recognized_data.get("service_name", ""))
                        # 安全地获取金额值
                        amount_value = recognized_data.get("amount", recognized_data.get("price", 0.0))
                        try:
                            amount_float = float(amount_value) if amount_value not in [None, "", "N/A"] else 0.0
                            # 确保金额不为负数
                            if amount_float < 0:
                                amount_float = 0.0
                        except (ValueError, TypeError):
                            amount_float = 0.0

                        amount = st.number_input("金额", value=amount_float, min_value=0.0)

                    with col_b:
                        currency_value = recognized_data.get("currency", "CNY")
                        currency_options = ["CNY", "USD", "EUR"]
                        currency_index = currency_options.index(currency_value) if currency_value in currency_options else 0
                        currency = st.selectbox("币种", currency_options, index=currency_index)

                        cycle_value = recognized_data.get("billing_cycle", "monthly")
                        cycle_options = ["monthly", "yearly", "weekly"]
                        cycle_index = cycle_options.index(cycle_value) if cycle_value in cycle_options else 0
                        billing_cycle = st.selectbox("付费周期", cycle_options,
                            format_func=lambda x: {"monthly": "月付", "yearly": "年付", "weekly": "周付"}[x],
                            index=cycle_index
                        )

                    category = st.selectbox("分类", [
                        "entertainment", "productivity", "health_fitness", "education", "business", "storage", "other"
                    ], format_func=lambda x: {
                        "entertainment": "娱乐", "productivity": "生产力",
                        "health_fitness": "健康健身", "education": "教育",
                        "business": "商务", "storage": "存储", "other": "其他"
                    }[x])

                    notes = st.text_area("备注", placeholder="可选备注信息")

                    col_form1, col_form2 = st.columns(2)
                    with col_form1:
                        if st.form_submit_button("✅ 添加订阅", use_container_width=True):
                            subscription_data = {
                                "service_name": service_name,
                                "price": amount,
                                "currency": currency,
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
                                st.success(f"✅ 成功从账单识别并添加订阅: {service_name}")
                                st.session_state.show_bill_scanner = False
                                # 清理OCR相关的session state
                                if "ocr_result" in st.session_state:
                                    del st.session_state.ocr_result
                                if "ocr_step" in st.session_state:
                                    del st.session_state.ocr_step
                                if "recognized_data" in st.session_state:
                                    del st.session_state.recognized_data
                                st.rerun()
                            else:
                                st.error("❌ 添加订阅失败")

                    with col_form2:
                        if st.form_submit_button("❌ 取消", use_container_width=True):
                            st.session_state.show_bill_scanner = False
                            # 清理OCR相关的session state
                            if "ocr_result" in st.session_state:
                                del st.session_state.ocr_result
                            if "ocr_step" in st.session_state:
                                del st.session_state.ocr_step
                            if "recognized_data" in st.session_state:
                                del st.session_state.recognized_data
                            st.rerun()

            with col2:
                if st.button("❌ 取消", use_container_width=True):
                    st.session_state.show_bill_scanner = False
                    st.rerun()

        else:
            # 没有上传文件时的说明
            st.info("📄 请上传账单图片或PDF文件")
            st.markdown("""
            **支持的文件格式:**
            - 图片: PNG, JPG, JPEG
            - 文档: PDF

            **识别功能:**
            - 自动识别服务名称
            - 提取金额和币种
            - 识别账单周期
            - 智能分类建议
            """)

            if st.button("❌ 关闭", use_container_width=True):
                st.session_state.show_bill_scanner = False
                st.rerun()

def main():
    """主函数"""
    try:
        # 初始化
        init_session_state()

        # 未登录时显示认证页面
        if not st.session_state.authenticated or not st.session_state.current_user:
            render_auth_page()
            st.stop()

        # 渲染界面
        render_sidebar()

        # 主内容区域
        render_main_content()

        # 模态窗口
        render_add_subscription_modal()
        render_bill_scanner_modal()

        # 模板选择器
        from ui.components.template_selector import render_template_selector_modal, render_template_form
        render_template_selector_modal()
        render_template_form()

        # 页脚
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("🤖 基于Claude Code构建")
        with col2:
            st.caption("💾 SQLite数据库")
        with col3:
            st.caption("🔄 实时更新")

    except Exception as e:
        st.error(f"应用启动错误: {e}")
        st.exception(e)

if __name__ == "__main__":
    main()