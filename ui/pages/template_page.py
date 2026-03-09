"""
模板选择页面 - 独立页面用于从模板添加订阅
"""

import streamlit as st
from core.templates import (
    get_all_templates,
    get_templates_by_category,
    search_templates,
    get_template_categories,
    get_template
)
from core.database.data_interface import data_manager
from datetime import datetime


def render_template_page():
    """渲染模板选择页面"""
    st.title("📋 从模板快速添加")

    # 如果正在显示表单，渲染表单
    if st.session_state.get("show_template_form_page", False):
        render_template_form_page()
        return

    # 搜索框
    search_query = st.text_input(
        "🔍 搜索服务",
        placeholder="输入服务名称或关键词搜索...",
        key="template_search_page"
    )

    # 分类筛选
    categories = get_template_categories()
    category_display = {
        "entertainment": "🎬 娱乐",
        "productivity": "💼 生产力",
        "storage": "☁️ 存储",
        "education": "📚 教育",
        "health_fitness": "💪 健康健身",
        "business": "💼 商务",
        "other": "📦 其他"
    }

    col1, col2 = st.columns([3, 1])

    with col1:
        selected_category = st.selectbox(
            "分类筛选",
            ["全部"] + categories,
            format_func=lambda x: "📂 全部分类" if x == "全部" else category_display.get(x, x),
            key="category_select_page"
        )

    with col2:
        st.metric("模板数量", len(get_all_templates()))

    # 获取模板
    if search_query:
        templates = search_templates(search_query)
    elif selected_category != "全部":
        templates = get_templates_by_category(selected_category)
    else:
        templates = get_all_templates()

    if not templates:
        st.info("😕 没有找到匹配的服务模板")
        if st.button("🔙 返回首页", use_container_width=True):
            st.session_state.current_page = "首页"
            st.rerun()
        return

    # 显示模板卡片
    st.write(f"**找到 {len(templates)} 个服务模板:**")
    st.divider()

    # 使用columns布局显示模板
    cols_per_row = 3
    template_items = list(templates.items())

    for i in range(0, len(template_items), cols_per_row):
        cols = st.columns(cols_per_row)

        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(template_items):
                service_name, template = template_items[idx]

                with col:
                    with st.container():
                        # 模板卡片
                        st.markdown(f"### {template['icon']} {service_name}")

                        # 价格和周期
                        billing_cycle_display = {
                            "monthly": "月",
                            "yearly": "年",
                            "weekly": "周",
                            "daily": "日"
                        }.get(template["billing_cycle"], "月")

                        price_display = f"{template['currency']} {template['price']}/{billing_cycle_display}"
                        st.markdown(f"**💰 {price_display}**")

                        # 描述
                        st.caption(template.get("description", ""))

                        # 添加按钮
                        if st.button(
                            "➕ 选择",
                            key=f"select_template_page_{service_name}",
                            use_container_width=True
                        ):
                            st.session_state.selected_template_page = service_name
                            st.session_state.show_template_form_page = True
                            st.rerun()

    st.divider()

    # 返回按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 返回首页", use_container_width=True):
            st.session_state.current_page = "首页"
            st.rerun()
    with col2:
        if st.button("📊 查看订阅", use_container_width=True):
            st.session_state.current_page = "数据概览"
            st.rerun()


def render_template_form_page():
    """渲染从模板添加订阅的表单"""
    template_name = st.session_state.get("selected_template_page")
    if not template_name:
        st.session_state.show_template_form_page = False
        st.rerun()
        return

    template = get_template(template_name)
    if not template:
        st.error("❌ 模板不存在")
        st.session_state.show_template_form_page = False
        return

    st.title(f"{template['icon']} 添加 {template_name}")

    with st.form("template_subscription_form_page"):
        st.write("**确认订阅信息:**")

        col1, col2 = st.columns(2)

        with col1:
            service_name = st.text_input(
                "服务名称",
                value=template["service_name"]
            )

            price = st.number_input(
                "价格",
                min_value=0.0,
                value=float(template["price"]),
                step=0.01
            )

        with col2:
            currency = st.selectbox(
                "币种",
                ["CNY", "USD", "EUR", "GBP", "JPY"],
                index=["CNY", "USD", "EUR", "GBP", "JPY"].index(template["currency"])
            )

            billing_cycle = st.selectbox(
                "付费周期",
                ["monthly", "yearly", "weekly", "daily"],
                index=["monthly", "yearly", "weekly", "daily"].index(template["billing_cycle"]),
                format_func=lambda x: {
                    "monthly": "月付",
                    "yearly": "年付",
                    "weekly": "周付",
                    "daily": "日付"
                }[x]
            )

        col1, col2 = st.columns(2)

        with col1:
            categories = ["entertainment", "productivity", "health_fitness", "education", "business", "storage", "other"]
            category = st.selectbox(
                "分类",
                categories,
                index=categories.index(template["category"]),
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

        with col2:
            start_date = st.date_input(
                "开始日期",
                value=datetime.now(),
                help="首次订阅或上次续费的日期"
            )

        notes = st.text_area(
            "备注",
            placeholder="可选备注信息...",
            help="添加关于此订阅的其他信息"
        )

        # 显示模板描述
        if template.get("description"):
            st.info(f"💡 {template['description']}")

        # 按钮
        col1, col2, col3 = st.columns(3)

        with col1:
            submitted = st.form_submit_button("✅ 添加订阅", use_container_width=True, type="primary")

        with col2:
            if st.form_submit_button("🔙 返回模板", use_container_width=True):
                st.session_state.show_template_form_page = False
                st.rerun()

        with col3:
            if st.form_submit_button("🏠 首页", use_container_width=True):
                st.session_state.show_template_form_page = False
                st.session_state.current_page = "首页"
                st.rerun()

        if submitted:
            if not service_name or price <= 0:
                st.error("❌ 请填写完整信息")
            else:
                # 创建订阅数据
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

                # 保存订阅
                result = data_manager.create_subscription(
                    st.session_state.current_user_id,
                    subscription_data
                )

                if result:
                    st.success(f"✅ 成功添加订阅: {service_name}")
                    st.balloons()
                    st.session_state.show_template_form_page = False
                    st.info("💡 可以继续添加订阅，或通过左侧菜单查看数据概览")
                else:
                    st.error("❌ 添加订阅失败，请重试")


if __name__ == "__main__":
    render_template_page()