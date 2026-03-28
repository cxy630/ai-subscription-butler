"""
AI聊天界面组件 - 与AI助手对话
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
import asyncio

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.database.data_interface import data_manager
from core.ai import get_ai_assistant, is_ai_assistant_available
import json

def export_conversation():
    """导出对话历史为JSON文件"""
    if not st.session_state.get("chat_history"):
        st.warning("没有对话历史可导出")
        return

    # 准备导出数据
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "user_id": st.session_state.get("current_user_id", "unknown"),
        "conversation_count": len(st.session_state.chat_history),
        "conversations": []
    }

    # 转换对话格式
    for i, message_pair in enumerate(st.session_state.chat_history):
        if isinstance(message_pair, tuple):
            user_msg, ai_msg = message_pair
            export_data["conversations"].append({
                "index": i + 1,
                "user_message": user_msg,
                "ai_response": ai_msg if isinstance(ai_msg, str) else ai_msg.get("response", ""),
                "timestamp": datetime.now().isoformat()
            })

    # 生成JSON
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)

    # 提供下载
    st.download_button(
        label="💾 下载对话记录 (JSON)",
        data=json_str,
        file_name=f"conversation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def get_enhanced_user_context(user_id: str) -> dict:
    """
    获取增强的用户上下文，包含完整订阅详情

    Args:
        user_id: 用户ID

    Returns:
        包含详细订阅信息的上下文字典
    """
    # 获取基础概览
    context = data_manager.get_user_overview(user_id) or {}

    # 添加用户ID到context中(供Gemini的_build_context_string使用)
    if "user" not in context:
        context["user"] = {}
    context["user"]["id"] = user_id

    # 获取完整订阅列表
    subscriptions = data_manager.get_active_subscriptions(user_id)

    # 添加订阅详情列表
    context["subscription_details"] = [
        {
            "service_name": sub.get("service_name"),
            "price": sub.get("price"),
            "currency": sub.get("currency", "CNY"),
            "billing_cycle": sub.get("billing_cycle"),
            "category": sub.get("category"),
            "status": sub.get("status"),
            "start_date": sub.get("start_date"),
            "notes": sub.get("notes")
        }
        for sub in subscriptions
    ]

    # 添加统计信息
    context["total_subscriptions"] = len(subscriptions)
    context["active_subscriptions"] = len([s for s in subscriptions if s.get("status") == "active"])

    return context

def get_ai_response_mock(user_message: str, user_context: dict) -> str:
    """
    模拟AI响应 - 在没有OpenAI API的情况下提供智能响应

    Args:
        user_message: 用户输入的消息
        user_context: 用户上下文信息

    Returns:
        AI响应字符串
    """
    message_lower = user_message.lower()

    # 获取用户数据用于智能响应
    subscriptions = user_context.get("subscription_details", [])
    monthly_spending = user_context.get("monthly_spending", 0)
    categories = user_context.get("subscription_categories", {})
    total_subscriptions = user_context.get("total_subscriptions", len(subscriptions))

    # 支出相关查询
    if any(word in message_lower for word in ["花费", "支出", "钱", "费用", "成本"]):
        if "娱乐" in message_lower or "entertainment" in message_lower:
            entertainment_cost = categories.get("entertainment", {}).get("spending", 0)
            return f"🎬 您在娱乐类订阅上的月度支出为 ¥{entertainment_cost:.2f}，包括视频、音乐等服务。建议定期评估使用频率，取消不常用的服务。"

        elif "生产力" in message_lower or "productivity" in message_lower:
            productivity_cost = categories.get("productivity", {}).get("spending", 0)
            return f"⚡ 您在生产力工具上的月度支出为 ¥{productivity_cost:.2f}。这类投资通常能提高工作效率，但建议避免功能重叠的工具。"

        else:
            return f"💰 您的总月度订阅支出为 ¥{monthly_spending:.2f}，年度支出约 ¥{monthly_spending * 12:.2f}。其中包含 {len(subscriptions)} 个活跃订阅，涵盖 {len(categories)} 个不同类别。"

    # 订阅详情查询
    elif any(word in message_lower for word in ["哪些", "有什么", "什么订阅", "列表"]):
        if not subscriptions:
            return "您目前还没有添加任何订阅。可以通过'添加订阅'或'扫描账单'功能来添加。"

        # 按分类组织订阅
        by_category = {}
        for sub in subscriptions:
            cat = sub.get("category", "other")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(sub)

        # 格式化输出
        response = f"📊 您目前有 {total_subscriptions} 个活跃订阅:\n\n"
        for cat, subs in by_category.items():
            cat_name = {"entertainment": "娱乐", "productivity": "生产力", "business": "商务",
                       "storage": "存储", "education": "教育", "health": "健康"}.get(cat, cat)
            response += f"**{cat_name}类** ({len(subs)}个):\n"
            for sub in subs:
                price = sub.get("price", 0)
                cycle = {"monthly": "月", "yearly": "年", "weekly": "周"}.get(sub.get("billing_cycle"), "月")
                response += f"  • {sub['service_name']}: ¥{price}/{cycle}\n"
            response += "\n"

        return response

    # 订阅数量查询
    elif any(word in message_lower for word in ["多少", "几个", "数量"]):
        return f"📊 您目前有 {total_subscriptions} 个活跃订阅。分类情况：" + \
               "".join([f"\n• {cat}: {stats['count']}个服务" for cat, stats in categories.items()])

    # 取消订阅相关
    elif any(word in message_lower for word in ["取消", "停止", "删除"]):
        if subscriptions:
            most_expensive = max(subscriptions, key=lambda x: x.get("price", 0))
            unused_suggestions = [s for s in subscriptions if s.get("category") == "entertainment"]

            response = "🤔 关于取消订阅的建议：\n"
            response += f"• 最贵的订阅是 {most_expensive['service_name']} (¥{most_expensive['price']}/月)\n"
            if unused_suggestions:
                response += f"• 可以考虑暂停不常用的娱乐服务\n"
            response += "• 建议先暂停而不是直接取消，观察一段时间后再决定"
            return response
        else:
            return "您目前没有活跃的订阅需要取消。"

    # 节省建议
    elif any(word in message_lower for word in ["节省", "省钱", "优化", "建议"]):
        suggestions = []

        if monthly_spending > 200:
            suggestions.append("💡 您的月度订阅支出较高，建议定期评估各服务的使用频率")

        if len(categories) > 1:
            entertainment_cost = categories.get("entertainment", {}).get("spending", 0)
            if entertainment_cost > 50:
                suggestions.append("🎬 娱乐类订阅支出较多，可以考虑选择性保留最常用的服务")

        # 查找可能的重复服务
        service_names = [s.get("service_name", "") for s in subscriptions]
        if any("spotify" in s.lower() and "apple music" in " ".join(service_names).lower() for s in service_names):
            suggestions.append("🎵 检测到多个音乐服务，建议只保留一个")

        if not suggestions:
            suggestions.append("✅ 您的订阅结构比较合理，继续保持定期评估的习惯")

        return "💡 个性化节省建议：\n" + "\n".join(suggestions)

    # 添加订阅
    elif any(word in message_lower for word in ["添加", "新增", "订阅"]):
        return "➕ 您可以通过以下方式添加订阅：\n• 点击侧边栏的'添加订阅'按钮\n• 使用'扫描账单'功能自动识别\n• 告诉我具体的服务名称和价格，我来帮您添加"

    # 默认响应
    else:
        return f"🤖 您好！我是您的AI订阅管家助手。\n\n" \
               f"📊 您目前的状况：\n" \
               f"• 活跃订阅：{len(subscriptions)} 个\n" \
               f"• 月度支出：¥{monthly_spending:.2f}\n" \
               f"• 服务类别：{len(categories)} 个\n\n" \
               f"💡 我可以帮您：\n" \
               f"• 分析订阅支出和使用情况\n" \
               f"• 提供节省和优化建议\n" \
               f"• 管理订阅的添加和取消\n" \
               f"• 回答任何关于订阅的问题\n\n" \
               f"请告诉我您想了解什么？"

def render_chat_message(message: dict, is_user: bool = True, message_index: int = 0):
    """
    渲染单个聊天消息 - 增强版

    Args:
        message: 消息字典
        is_user: 是否是用户消息
        message_index: 消息索引（用于唯一key）
    """
    if is_user:
        with st.chat_message("user", avatar="👤"):
            st.write(message.get("message", message.get("content", "")))
    else:
        with st.chat_message("assistant", avatar="🤖"):
            # 获取响应内容
            response = message.get("response", message.get("content", ""))

            # 如果是字典（Gemini返回的完整响应），提取文本
            if isinstance(response, dict):
                display_text = response.get("response", "")
                raw_data = response
            else:
                display_text = response
                raw_data = {"response": response}

            # 显示友好的文本内容
            st.markdown(display_text)

            # 底部工具栏（使用列布局）
            col1, col2, col3, col4, col5 = st.columns([6, 1, 1, 1, 1])

            with col1:
                # 置信度或时间戳
                confidence = message.get("confidence")
                if confidence:
                    st.caption(f"置信度: {confidence:.2%}")

            with col2:
                # 复制按钮
                if st.button("📋", key=f"copy_{message_index}", help="复制回答"):
                    st.session_state[f"show_copy_{message_index}"] = True
                    st.rerun()

            with col3:
                # 点赞按钮
                liked = st.session_state.get(f"liked_{message_index}", False)
                like_icon = "👍" if liked else "👍"
                if st.button(like_icon, key=f"like_{message_index}", help="有帮助"):
                    st.session_state[f"liked_{message_index}"] = not liked
                    st.rerun()

            with col4:
                # 反馈按钮
                if st.button("💬", key=f"feedback_{message_index}", help="提供反馈"):
                    st.session_state[f"show_feedback_{message_index}"] = True
                    st.rerun()

            with col5:
                # Debug按钮
                debug_icon = "🔽" if st.session_state.get(f"show_debug_{message_index}", False) else "🔧"
                if st.button(debug_icon, key=f"btn_debug_{message_index}", help="调试信息"):
                    current_state = st.session_state.get(f"show_debug_{message_index}", False)
                    st.session_state[f"show_debug_{message_index}"] = not current_state
                    st.rerun()

            # 显示复制文本框（如果激活）
            if st.session_state.get(f"show_copy_{message_index}", False):
                st.code(display_text, language="text")
                if st.button("✅ 关闭", key=f"close_copy_{message_index}"):
                    st.session_state[f"show_copy_{message_index}"] = False
                    st.rerun()

            # 显示反馈表单（如果激活）
            if st.session_state.get(f"show_feedback_{message_index}", False):
                with st.form(key=f"feedback_form_{message_index}"):
                    feedback_type = st.radio(
                        "反馈类型",
                        ["回答不准确", "格式不清晰", "信息不全", "其他"],
                        key=f"feedback_type_{message_index}"
                    )
                    feedback_text = st.text_area(
                        "详细说明（可选）",
                        key=f"feedback_text_{message_index}",
                        height=100
                    )

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.form_submit_button("提交反馈"):
                            # 保存反馈（可以记录到日志或数据库）
                            st.success("✅ 感谢您的反馈！")
                            st.session_state[f"show_feedback_{message_index}"] = False
                            st.rerun()
                    with col_b:
                        if st.form_submit_button("取消"):
                            st.session_state[f"show_feedback_{message_index}"] = False
                            st.rerun()

            # 显示Debug信息（如果激活）
            if st.session_state.get(f"show_debug_{message_index}", False):
                with st.expander("🔧 调试信息", expanded=True):
                    st.json(raw_data)

def render_chat_history():
    """渲染聊天历史"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 顶部操作按钮
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        # 显示当前会话ID(短格式)
        session_id = st.session_state.get("current_session_id", "new")
        if session_id != "new":
            short_id = session_id[:8]
            st.caption(f"💬 会话 {short_id} | {len(st.session_state.chat_history)} 条")
        else:
            st.caption(f"💬 新会话 | {len(st.session_state.chat_history)} 条")

    with col2:
        if st.button("🆕 新会话", use_container_width=True, help="开始新的对话会话"):
            # 生成新的会话ID
            import uuid
            st.session_state.current_session_id = str(uuid.uuid4())
            st.session_state.chat_history = []
            st.session_state.chat_initialized = False
            st.success("✅ 已开始新会话")
            st.rerun()

    with col3:
        if st.button("🗑️ 清空", use_container_width=True, help="清空当前会话历史"):
            st.session_state.chat_history = []
            st.success("✅ 对话历史已清空")
            st.rerun()

    with col4:
        if st.button("📥 导出", use_container_width=True, help="导出对话记录"):
            export_conversation()

    st.divider()

    # 显示历史消息
    for i, message_pair in enumerate(st.session_state.chat_history):
        if isinstance(message_pair, dict):
            # 单个消息
            is_user = message_pair.get("role") == "user"
            render_chat_message(message_pair, is_user, message_index=i)
        elif isinstance(message_pair, tuple):
            # 消息对
            user_msg, ai_msg = message_pair
            render_chat_message({"content": user_msg}, True, message_index=i*2)
            render_chat_message({"content": ai_msg}, False, message_index=i*2+1)

def render_suggested_questions():
    """渲染建议问题"""
    st.subheader("💡 试试问我这些问题：")

    suggestions = [
        "我每月在娱乐上花多少钱？",
        "有什么节省建议吗？",
        "我有几个订阅服务？",
        "最贵的订阅是什么？",
        "哪些服务可以取消？",
        "我的订阅结构合理吗？"
    ]

    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(f"💭 {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                # 直接发送建议问题
                st.session_state.send_suggestion = suggestion
                st.rerun()

def get_ai_response_smart(user_message: str, user_context: dict) -> dict:
    """
    智能AI响应 - 优先使用Gemini API，失败时使用模拟响应

    Args:
        user_message: 用户输入的消息
        user_context: 用户上下文信息

    Returns:
        AI响应结果字典
    """
    # 快速失败：如果AI助手不可用，直接返回降级响应
    if not is_ai_assistant_available():
        mock_response = get_ai_response_mock(user_message, user_context)
        return {
            "response": mock_response,
            "intent": "fallback",
            "confidence": 0.6,
            "model": "fallback",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        ai_assistant = get_ai_assistant()
        
        # 检查客户端是否真的可用
        if not ai_assistant or not ai_assistant.is_available():
            raise ValueError("AI助手不可用")

        # 获取对话历史
        conversation_history = []
        if "chat_history" in st.session_state:
            for i, (user_msg, ai_msg) in enumerate(st.session_state.chat_history):
                if user_msg:  # 跳过欢迎消息
                    conversation_history.append({"role": "user", "content": user_msg})
                    if isinstance(ai_msg, str):
                        conversation_history.append({"role": "assistant", "content": ai_msg})
                    elif isinstance(ai_msg, dict):
                        conversation_history.append({"role": "assistant", "content": ai_msg.get("response", "")})

        # 调用AI助手（内部已有超时保护）
        response = ai_assistant.chat_sync(user_message, user_context, conversation_history)
        
        # 验证响应格式
        if response and isinstance(response, dict) and response.get("response"):
            return response
        else:
            # 响应格式异常，使用降级
            raise ValueError("AI响应格式异常")
            
    except TimeoutError as e:
        # 超时错误，使用降级响应
        import logging
        logging.getLogger(__name__).warning(f"AI响应超时: {str(e)}")
    except Exception as e:
        # 其他错误，记录并降级
        import logging
        logging.getLogger(__name__).error(f"AI助手调用失败: {str(e)}", exc_info=True)

    # 使用模拟响应作为降级
    mock_response = get_ai_response_mock(user_message, user_context)
    return {
        "response": mock_response,
        "intent": "fallback",
        "confidence": 0.6,
        "model": "fallback",
        "timestamp": datetime.now().isoformat()
    }

def render_ai_status():
    """渲染AI状态信息"""
    if is_ai_assistant_available():
        ai_assistant = get_ai_assistant()
        status = ai_assistant.get_status()

        col1, col2 = st.columns(2)
        with col1:
            st.success(f"🤖 AI助手: 在线 ({status['model']})")
        with col2:
            requests_used = status['daily_requests_used']
            daily_limit = status['daily_limit']
            st.info(f"📊 今日使用: {requests_used}/{daily_limit}")
    else:
        st.warning("🤖 AI助手: 离线 (使用模拟响应)")

def render_chat_interface():
    """渲染完整的聊天界面"""
    st.title("🤖 AI助手")

    if not st.session_state.current_user_id:
        st.warning("请先选择用户")
        return

    # 清理旧的debug状态键（避免冲突）
    keys_to_remove = [k for k in st.session_state.keys()
                      if (k.startswith("debug_") and not k.startswith("show_debug_") and not k.startswith("btn_debug_"))
                      or k.startswith("debug_cb_")
                      or k.startswith("debug_state_")]
    for key in keys_to_remove:
        del st.session_state[key]

    # 显示AI状态
    render_ai_status()
    st.divider()

    # 获取增强的用户上下文(包含完整订阅详情)
    user_context = get_enhanced_user_context(st.session_state.current_user_id)

    # 初始化会话ID
    if "current_session_id" not in st.session_state:
        import uuid
        st.session_state.current_session_id = str(uuid.uuid4())

    # 聊天容器
    chat_container = st.container()

    with chat_container:
        # 显示欢迎消息
        if "chat_initialized" not in st.session_state:
            st.session_state.chat_initialized = True
            # 使用简单的欢迎消息，避免初始化时调用API导致卡住
            welcome_msg = "👋 你好！我是AI订阅管家助手，可以帮助你管理订阅、分析支出、提供优化建议。有什么我可以帮你的吗？"
            st.session_state.chat_history = [(None, welcome_msg)]

        # 显示聊天历史
        render_chat_history()

    # ===== 新增：显示订阅确认UI（在聊天历史之后立即显示） =====
    if st.session_state.get("show_subscription_confirmation"):
        st.divider()
        render_subscription_confirmation()

    if st.session_state.get("show_duplicate_warning"):
        st.divider()
        render_duplicate_warning()
    # ===== 确认UI结束 =====

    # 输入区域
    st.divider()

    # 检查是否有建议问题需要发送
    auto_send = False
    if "send_suggestion" in st.session_state:
        # 直接使用建议问题作为用户输入
        user_input = st.session_state.send_suggestion
        del st.session_state.send_suggestion
        auto_send = True
        # 创建一个隐藏的占位输入框
        st.empty()
    else:
        # 使用动态key来确保发送后输入框被清空
        # 每次发送后递增input_counter，这样输入框会完全重新创建
        if "input_counter" not in st.session_state:
            st.session_state.input_counter = 0

        # 正常的用户输入
        user_input = st.text_input(
            "💬 向AI助手提问（按回车发送）：",
            placeholder="例如：我每月在娱乐上花多少钱？",
            key=f"user_input_field_{st.session_state.input_counter}"
        )

    # 检测回车键发送：当输入框有内容且与上次记录不同时，说明用户刚按了回车
    enter_pressed = False
    if not auto_send and user_input.strip():
        last_input = st.session_state.get("last_user_input", "")
        if user_input != last_input:
            # 用户输入了新内容或修改了内容，按回车触发
            enter_pressed = True
            st.session_state.last_user_input = user_input

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        send_button = st.button("📤 发送", use_container_width=True, type="primary")

    with col2:
        if st.button("🗑️ 清空", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.last_user_input = ""
            st.session_state.chat_initialized = False
            # 清空输入框 - 递增counter
            st.session_state.input_counter += 1
            st.rerun()

    with col3:
        if st.button("💡 建议", use_container_width=True):
            st.session_state.show_suggestions = not st.session_state.get("show_suggestions", False)
            st.rerun()

    with col4:
        if st.button("⚙️ 设置", use_container_width=True, key="chat_settings"):
            st.session_state.show_chat_settings = not st.session_state.get("show_chat_settings", False)
            st.rerun()

    # 处理用户输入（包括建议问题的自动发送和回车发送）
    if (send_button or auto_send or enter_pressed) and user_input.strip():
        # 显示处理状态
        ai_response = None
        intent = "general_query"
        confidence = 0.8
        
        # 显示处理状态并获取AI响应
        with st.spinner("🤖 AI助手正在思考..."):
            try:
                # 直接调用，内部已有超时保护
                ai_response_data = get_ai_response_smart(user_input, user_context)
                
                # 提取响应文本
                if isinstance(ai_response_data, dict):
                    ai_response = ai_response_data.get("response", "抱歉，无法获取响应。")
                    intent = ai_response_data.get("intent", "general_query")
                    confidence = ai_response_data.get("confidence", 0.8)
                else:
                    ai_response = str(ai_response_data) if ai_response_data else "抱歉，无法获取响应。"
                    intent = "general_query"
                    confidence = 0.8
                    
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"AI响应获取失败: {str(e)}", exc_info=True)
                # 使用降级响应
                ai_response = "抱歉，AI服务暂时不可用，请稍后重试。"
                intent = "error"
                confidence = 0.0
        
        # 确保有响应
        if not ai_response:
            ai_response = "抱歉，无法获取响应，请稍后重试。"
            intent = "error"
            confidence = 0.0

        # ===== 检测订阅添加意图 =====
        try:
            from core.ai.subscription_extractor import SubscriptionExtractor, check_duplicate_subscription
            extractor = SubscriptionExtractor()

            subscription_info = extractor.extract_subscription_info(
                user_message=user_input,
                ai_response=ai_response
            )

            if subscription_info:
                # 检查重复
                subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
                is_duplicate, existing_sub = check_duplicate_subscription(
                    subscription_info['service_name'],
                    subscriptions
                )

                if is_duplicate:
                    st.session_state.pending_subscription = subscription_info
                    st.session_state.duplicate_subscription = existing_sub
                    st.session_state.show_duplicate_warning = True
                else:
                    st.session_state.pending_subscription = subscription_info
                    st.session_state.show_subscription_confirmation = True
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"订阅检测失败: {str(e)}")
        # ===== 订阅检测结束 =====

        # 保存对话到历史
        try:
            st.session_state.chat_history.append((user_input, ai_response))

            # 保存到数据库
            try:
                data_manager.save_conversation(
                    user_id=st.session_state.current_user_id,
                    session_id=st.session_state.chat_session_id,
                    message=user_input,
                    response=ai_response,
                    intent=intent,
                    confidence=confidence
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"保存对话失败: {str(e)}")

            # 清空输入框和记录状态 - 递增counter会创建新的输入框
            st.session_state.input_counter += 1
            st.session_state.last_user_input = ""
            st.rerun()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"保存对话历史失败: {str(e)}")
            # 即使保存失败，也继续执行，清空输入框
            st.session_state.input_counter += 1
            st.session_state.last_user_input = ""
            st.rerun()

    # 显示建议问题
    if st.session_state.get("show_suggestions", False):
        st.divider()
        render_suggested_questions()

    # 显示聊天设置
    if st.session_state.get("show_chat_settings", False):
        st.divider()
        render_chat_settings()

    # 聊天统计
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💬 对话轮数", len(st.session_state.get("chat_history", [])))

    with col2:
        # 获取数据库中的历史对话数
        session_history = data_manager.get_session_history(st.session_state.chat_session_id)
        st.metric("📜 历史记录", len(session_history))

    with col3:
        st.metric("🎯 会话ID", st.session_state.chat_session_id[:8] + "...")

    with col4:
        # 显示AI模型信息
        if is_ai_assistant_available():
            ai_assistant = get_ai_assistant()
            status = ai_assistant.get_status()
            st.metric("🧠 AI模型", status["model"])
        else:
            st.metric("🧠 AI模型", "模拟响应")

def render_subscription_confirmation():
    """渲染订阅确认UI组件"""
    st.success("✅ AI已识别到订阅信息")

    pending_sub = st.session_state.pending_subscription

    with st.container():
        st.markdown("### ➕ 确认添加订阅")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("服务名称", pending_sub['service_name'])
            billing_cycle_map = {
                'monthly': '每月',
                'yearly': '每年',
                'weekly': '每周',
                'daily': '每天'
            }
            st.metric("计费周期", billing_cycle_map.get(pending_sub['billing_cycle'], '每月'))

        with col2:
            st.metric("价格", f"{pending_sub['currency']} {pending_sub['price']}")
            category_map = {
                'entertainment': '娱乐',
                'productivity': '生产力',
                'storage': '存储',
                'business': '商务',
                'education': '教育',
                'health': '健康',
                'other': '其他'
            }
            st.metric("分类", category_map.get(pending_sub['category'], '其他'))

        # 显示订阅日期
        from datetime import datetime, timedelta
        start_date_str = pending_sub.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            formatted_date = start_date.strftime('%Y年%m月%d日')

            # 判断是否是今天
            today = datetime.now().date()
            if start_date.date() == today:
                date_label = f"{formatted_date} (今天)"
            elif start_date.date() == today - timedelta(days=1):
                date_label = f"{formatted_date} (昨天)"
            elif start_date.date() > today:
                days_diff = (start_date.date() - today).days
                date_label = f"{formatted_date} ({days_diff}天后)"
            else:
                days_diff = (today - start_date.date()).days
                date_label = f"{formatted_date} ({days_diff}天前)"

            st.info(f"📅 订阅日期: {date_label}")
        except:
            st.info(f"📅 订阅日期: {start_date_str}")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("✅ 确认添加", type="primary", use_container_width=True, key="confirm_add_sub"):
                # 添加到数据库
                try:
                    from datetime import datetime

                    # 准备订阅数据字典
                    subscription_data = {
                        'service_name': pending_sub['service_name'],
                        'price': pending_sub['price'],
                        'billing_cycle': pending_sub['billing_cycle'],
                        'currency': pending_sub.get('currency', 'CNY'),
                        'category': pending_sub.get('category', 'other'),
                        'status': 'active',
                        'start_date': pending_sub.get('start_date', datetime.now().strftime('%Y-%m-%d'))  # 使用提取的日期
                    }

                    # 调用create_subscription方法
                    result = data_manager.create_subscription(
                        user_id=st.session_state.current_user_id,
                        subscription_data=subscription_data
                    )

                    if result:
                        st.success(f"✅ 已成功添加 {pending_sub['service_name']} 订阅！")
                        # 清理session state
                        if "show_subscription_confirmation" in st.session_state:
                            del st.session_state.show_subscription_confirmation
                        if "pending_subscription" in st.session_state:
                            del st.session_state.pending_subscription
                        if "editing_subscription" in st.session_state:
                            del st.session_state.editing_subscription
                        st.rerun()
                    else:
                        st.error("❌ 添加失败，请重试")
                except Exception as e:
                    st.error(f"❌ 添加失败: {str(e)}")

        with col_b:
            if st.button("✏️ 修改信息", use_container_width=True, key="edit_sub"):
                st.session_state.editing_subscription = True
                st.rerun()

        with col_c:
            if st.button("❌ 取消", use_container_width=True, key="cancel_sub"):
                if "show_subscription_confirmation" in st.session_state:
                    del st.session_state.show_subscription_confirmation
                if "pending_subscription" in st.session_state:
                    del st.session_state.pending_subscription
                if "editing_subscription" in st.session_state:
                    del st.session_state.editing_subscription
                st.rerun()

        # 编辑表单
        if st.session_state.get("editing_subscription"):
            st.divider()
            with st.form("edit_subscription_form"):
                st.markdown("#### ✏️ 修改订阅信息")

                new_service_name = st.text_input("服务名称", value=pending_sub['service_name'])
                new_price = st.number_input("价格", value=float(pending_sub['price']), min_value=0.0, step=0.01)

                currency_options = ['CNY', 'USD', 'EUR', 'GBP', 'JPY']
                current_currency = pending_sub.get('currency', 'CNY')
                currency_index = currency_options.index(current_currency) if current_currency in currency_options else 0
                new_currency = st.selectbox("币种", currency_options, index=currency_index)

                cycle_options = ['monthly', 'yearly', 'weekly', 'daily']
                cycle_labels = {'monthly': '每月', 'yearly': '每年', 'weekly': '每周', 'daily': '每天'}
                current_cycle = pending_sub.get('billing_cycle', 'monthly')
                cycle_index = cycle_options.index(current_cycle) if current_cycle in cycle_options else 0
                new_billing_cycle = st.selectbox(
                    "计费周期",
                    cycle_options,
                    index=cycle_index,
                    format_func=lambda x: cycle_labels.get(x, x)
                )

                category_options = ['entertainment', 'productivity', 'storage', 'business', 'education', 'health', 'other']
                category_labels = {
                    'entertainment': '娱乐', 'productivity': '生产力', 'storage': '存储',
                    'business': '商务', 'education': '教育', 'health': '健康', 'other': '其他'
                }
                current_category = pending_sub.get('category', 'other')
                category_index = category_options.index(current_category) if current_category in category_options else 0
                new_category = st.selectbox(
                    "分类",
                    category_options,
                    index=category_index,
                    format_func=lambda x: category_labels.get(x, x)
                )

                # 添加订阅日期选择
                from datetime import datetime, date
                current_start_date = pending_sub.get('start_date')
                if current_start_date:
                    try:
                        default_date = datetime.strptime(current_start_date, '%Y-%m-%d').date()
                    except:
                        default_date = date.today()
                else:
                    default_date = date.today()

                new_start_date = st.date_input(
                    "订阅日期",
                    value=default_date,
                    help="选择订阅开始日期，用于计算下次续费时间"
                )

                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 保存修改", use_container_width=True):
                        # 更新pending_subscription
                        st.session_state.pending_subscription = {
                            'service_name': new_service_name,
                            'price': new_price,
                            'currency': new_currency,
                            'billing_cycle': new_billing_cycle,
                            'category': new_category,
                            'start_date': new_start_date.strftime('%Y-%m-%d')
                        }
                        st.session_state.editing_subscription = False
                        st.rerun()

                with col_cancel:
                    if st.form_submit_button("❌ 取消编辑", use_container_width=True):
                        st.session_state.editing_subscription = False
                        st.rerun()

def render_duplicate_warning():
    """渲染重复订阅警告UI组件"""
    st.warning("⚠️ 发现重复订阅")

    pending_sub = st.session_state.pending_subscription
    existing_sub = st.session_state.duplicate_subscription

    with st.container():
        st.markdown("### 🔄 已存在相同订阅")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**要添加的订阅：**")
            billing_cycle_map = {'monthly': '每月', 'yearly': '每年', 'weekly': '每周', 'daily': '每天'}
            st.info(f"""
            - 服务名称: {pending_sub['service_name']}
            - 价格: {pending_sub.get('currency', 'CNY')} {pending_sub['price']}
            - 周期: {billing_cycle_map.get(pending_sub['billing_cycle'], pending_sub['billing_cycle'])}
            """)

        with col2:
            st.markdown("**现有订阅：**")
            existing_cycle = billing_cycle_map.get(existing_sub.get('billing_cycle'), existing_sub.get('billing_cycle'))
            existing_status = existing_sub.get('status', 'unknown')
            status_map = {'active': '活跃', 'paused': '暂停', 'cancelled': '已取消'}
            st.warning(f"""
            - 服务名称: {existing_sub.get('service_name')}
            - 价格: {existing_sub.get('currency', 'CNY')} {existing_sub.get('price')}
            - 周期: {existing_cycle}
            - 状态: {status_map.get(existing_status, existing_status)}
            """)

        st.markdown("---")
        st.markdown("**💡 建议操作：**")
        st.markdown("1. 修改新订阅的名称（例如：Netflix 个人版 / Netflix 家庭版）")
        st.markdown("2. 取消添加，保留现有订阅")
        st.markdown("3. 添加为新订阅（如果确实是不同的账号）")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("✏️ 修改名称", type="primary", use_container_width=True, key="modify_dup_name"):
                st.session_state.editing_duplicate = True
                if "show_duplicate_warning" in st.session_state:
                    del st.session_state.show_duplicate_warning
                st.session_state.show_subscription_confirmation = True
                st.rerun()

        with col_b:
            if st.button("➕ 仍然添加", use_container_width=True, key="add_anyway"):
                # 在服务名称后添加后缀以避免重复
                original_name = pending_sub['service_name']
                suffix = 2
                max_attempts = 100  # 防止无限循环
                attempts = 0
                while attempts < max_attempts:
                    new_name = f"{original_name} ({suffix})"
                    subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
                    from core.ai.subscription_extractor import check_duplicate_subscription
                    is_dup, _ = check_duplicate_subscription(new_name, subscriptions)
                    if not is_dup:
                        break
                    suffix += 1
                    attempts += 1
                
                if attempts >= max_attempts:
                    # 如果尝试次数过多，使用时间戳作为后缀
                    import time
                    new_name = f"{original_name} ({int(time.time())})"

                st.session_state.pending_subscription['service_name'] = new_name
                if "show_duplicate_warning" in st.session_state:
                    del st.session_state.show_duplicate_warning
                st.session_state.show_subscription_confirmation = True
                st.rerun()

        with col_c:
            if st.button("❌ 取消添加", use_container_width=True, key="cancel_dup_add"):
                if "show_duplicate_warning" in st.session_state:
                    del st.session_state.show_duplicate_warning
                if "pending_subscription" in st.session_state:
                    del st.session_state.pending_subscription
                if "duplicate_subscription" in st.session_state:
                    del st.session_state.duplicate_subscription
                st.rerun()

def render_chat_settings():
    """渲染聊天设置"""
    with st.expander("⚙️ 聊天设置"):
        st.subheader("AI助手配置")

        # 响应风格
        response_style = st.selectbox(
            "响应风格",
            ["friendly", "professional", "concise"],
            format_func=lambda x: {"friendly": "友好", "professional": "专业", "concise": "简洁"}[x]
        )

        # 详细程度
        detail_level = st.slider("响应详细程度", 1, 5, 3)

        # 是否包含建议
        include_suggestions = st.checkbox("包含优化建议", value=True)

        if st.button("💾 保存设置"):
            st.session_state.chat_settings = {
                "response_style": response_style,
                "detail_level": detail_level,
                "include_suggestions": include_suggestions
            }
            st.success("设置已保存")

if __name__ == "__main__":
    # 测试组件
    render_chat_interface()