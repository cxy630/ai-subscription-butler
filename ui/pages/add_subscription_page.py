"""
添加订阅页面 - 独立页面用于添加新订阅
"""

import streamlit as st
from datetime import datetime
from core.database.data_interface import data_manager


def render_add_subscription_page():
    """渲染添加订阅页面"""
    st.title("➕ 添加新订阅")

    st.markdown("填写以下信息以添加新的订阅服务")

    with st.form("add_subscription_form_page"):
        col1, col2 = st.columns(2)

        with col1:
            service_name = st.text_input("服务名称*", placeholder="例如: Netflix")
            price = st.number_input("价格*", min_value=0.01, value=15.99, step=0.01)

        with col2:
            currency = st.selectbox("币种", ["CNY", "USD", "EUR", "GBP", "JPY"], index=0)

            billing_cycle = st.selectbox("付费周期*",
                ["monthly", "yearly", "weekly", "daily"],
                format_func=lambda x: {
                    "monthly": "月付", "yearly": "年付",
                    "weekly": "周付", "daily": "日付"
                }[x])

        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox("分类*", [
                "entertainment", "productivity", "health_fitness",
                "education", "business", "storage", "other"
            ], format_func=lambda x: {
                "entertainment": "娱乐", "productivity": "生产力",
                "health_fitness": "健康健身", "education": "教育",
                "business": "商务", "storage": "存储", "other": "其他"
            }[x])

        with col2:
            start_date = st.date_input(
                "开始日期*",
                value=datetime.now(),
                help="首次订阅或上次续费的日期"
            )

        notes = st.text_area("备注", placeholder="可选备注信息（选填）")

        st.caption("💡 系统将根据开始日期自动计算续费提醒")

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            submitted = st.form_submit_button("✅ 添加订阅", use_container_width=True, type="primary")

        with col2:
            if st.form_submit_button("🔙 返回", use_container_width=True):
                st.session_state.current_page = "数据概览"
                st.rerun()

        with col3:
            if st.form_submit_button("🏠 首页", use_container_width=True):
                st.session_state.current_page = "首页"
                st.rerun()

        if submitted:
            if not service_name or price <= 0:
                st.error("❌ 请填写完整的必填信息")
            else:
                subscription_data = {
                    "service_name": service_name,
                    "price": price,
                    "currency": currency,
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
                    st.balloons()
                    st.info("💡 可以继续添加订阅，或通过左侧菜单查看数据概览")
                else:
                    st.error("❌ 添加订阅失败，请重试")


if __name__ == "__main__":
    render_add_subscription_page()