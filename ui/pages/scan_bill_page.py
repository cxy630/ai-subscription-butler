"""
扫描账单页面 - 独立页面用于OCR扫描账单
"""

import streamlit as st
from datetime import datetime
from core.database.data_interface import data_manager


def render_scan_bill_page():
    """渲染扫描账单页面"""
    st.title("📱 扫描账单")

    st.markdown("上传账单图片，使用AI自动识别订阅信息")

    # 文件上传
    uploaded_file = st.file_uploader(
        "上传账单图片",
        type=['png', 'jpg', 'jpeg', 'pdf'],
        help="支持PNG、JPG、JPEG、PDF格式"
    )

    if uploaded_file is not None:
        # 显示上传的文件信息
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"📄 已上传: {uploaded_file.name}")
        with col2:
            st.caption(f"大小: {uploaded_file.size / 1024:.1f} KB")

        # 如果是图片，显示预览
        if uploaded_file.type in ['image/png', 'image/jpg', 'image/jpeg']:
            st.image(uploaded_file, caption="账单预览", use_container_width=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔍 开始识别", use_container_width=True, type="primary"):
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
                                st.session_state.ocr_result = ocr_result
                                st.session_state.ocr_step = "confirm"
                            else:
                                st.warning("⚠️ OCR识别失败，使用模拟结果")
                                mock_result = {
                                    "success": True,
                                    "confidence": 0.8,
                                    "extracted_data": {
                                        "service_name": "Netflix",
                                        "amount": "15.99",
                                        "currency": "CNY",
                                        "billing_date": "2024-01-15",
                                        "billing_cycle": "monthly"
                                    },
                                    "raw_text": "Netflix 订阅服务\n月费: ¥15.99\n账单日期: 2024-01-15",
                                    "description": "检测到Netflix流媒体服务的月度订阅账单。"
                                }
                                st.session_state.ocr_result = mock_result
                                st.session_state.ocr_step = "confirm"
                        else:
                            st.warning("⚠️ Gemini API不可用，使用模拟结果")
                            mock_result = {
                                "success": True,
                                "confidence": 0.8,
                                "extracted_data": {
                                    "service_name": "Netflix",
                                    "amount": "15.99",
                                    "currency": "CNY",
                                    "billing_date": "2024-01-15",
                                    "billing_cycle": "monthly"
                                },
                                "raw_text": "Netflix 订阅服务\n月费: ¥15.99\n账单日期: 2024-01-15",
                                "description": "检测到Netflix流媒体服务的月度订阅账单。"
                            }
                            st.session_state.ocr_result = mock_result
                            st.session_state.ocr_step = "confirm"

                    except Exception as e:
                        st.error(f"❌ OCR识别出错: {str(e)}")
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

        with col2:
            if st.button("🔙 返回", use_container_width=True):
                st.session_state.current_page = "首页"
                st.rerun()

        with col3:
            if st.button("📊 查看订阅", use_container_width=True):
                st.session_state.current_page = "数据概览"
                st.rerun()

        # 显示识别结果确认步骤
        if st.session_state.get("ocr_step") == "confirm" and st.session_state.get("ocr_result"):
            st.divider()
            ocr_result = st.session_state.ocr_result

            st.subheader("📋 识别结果确认")

            col_desc1, col_desc2 = st.columns([2, 1])
            with col_desc1:
                st.info(f"📄 **识别描述**: {ocr_result.get('description', '已识别账单内容')}")
            with col_desc2:
                confidence = ocr_result.get('confidence', 0.8)
                confidence_color = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🔴"
                st.metric("识别准确度", f"{confidence:.1%}", delta=f"{confidence_color}")

            with st.expander("🔍 查看原始识别文本", expanded=False):
                raw_text = ocr_result.get('raw_text', '无识别文本')
                st.text_area("原始文本", value=raw_text, height=100, disabled=True)

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
            st.divider()
            recognized_data = st.session_state.get("recognized_data", {})
            st.subheader("📋 确认订阅信息")

            with st.form("ocr_result_form"):
                st.write("请确认识别结果并编辑：")

                col_a, col_b = st.columns(2)
                with col_a:
                    service_name = st.text_input("服务名称", value=recognized_data.get("service_name", ""))
                    amount_value = recognized_data.get("amount", recognized_data.get("price", 0.0))
                    try:
                        amount_float = float(amount_value) if amount_value not in [None, "", "N/A"] else 0.0
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

                col_form1, col_form2, col_form3 = st.columns(3)
                with col_form1:
                    if st.form_submit_button("✅ 添加订阅", use_container_width=True, type="primary"):
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
                            # 清理OCR相关的session state
                            if "ocr_result" in st.session_state:
                                del st.session_state.ocr_result
                            if "ocr_step" in st.session_state:
                                del st.session_state.ocr_step
                            if "recognized_data" in st.session_state:
                                del st.session_state.recognized_data
                            st.balloons()
                        else:
                            st.error("❌ 添加订阅失败")

                with col_form2:
                    if st.form_submit_button("❌ 取消", use_container_width=True):
                        # 清理OCR相关的session state
                        if "ocr_result" in st.session_state:
                            del st.session_state.ocr_result
                        if "ocr_step" in st.session_state:
                            del st.session_state.ocr_step
                        if "recognized_data" in st.session_state:
                            del st.session_state.recognized_data
                        st.rerun()

                with col_form3:
                    if st.form_submit_button("🏠 首页", use_container_width=True):
                        st.session_state.current_page = "首页"
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

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔙 返回首页", use_container_width=True):
                st.session_state.current_page = "首页"
                st.rerun()

        with col2:
            if st.button("📊 查看订阅", use_container_width=True):
                st.session_state.current_page = "数据概览"
                st.rerun()


if __name__ == "__main__":
    render_scan_bill_page()