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
    subscriptions = user_context.get("subscriptions", [])
    monthly_spending = user_context.get("monthly_spending", 0)
    categories = user_context.get("subscription_categories", {})

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

    # 订阅数量查询
    elif any(word in message_lower for word in ["多少", "几个", "数量", "订阅"]):
        return f"📊 您目前有 {len(subscriptions)} 个活跃订阅。分类情况：" + \
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

def render_chat_message(message: dict, is_user: bool = True):
    """渲染单个聊天消息"""
    if is_user:
        with st.chat_message("user", avatar="👤"):
            st.write(message.get("message", message.get("content", "")))
    else:
        with st.chat_message("assistant", avatar="🤖"):
            response = message.get("response", message.get("content", ""))
            st.write(response)

            # 显示置信度（如果有）
            confidence = message.get("confidence")
            if confidence:
                st.caption(f"置信度: {confidence:.2%}")

def render_chat_history():
    """渲染聊天历史"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 显示历史消息
    for i, message_pair in enumerate(st.session_state.chat_history):
        if isinstance(message_pair, dict):
            # 单个消息
            is_user = message_pair.get("role") == "user"
            render_chat_message(message_pair, is_user)
        elif isinstance(message_pair, tuple):
            # 消息对
            user_msg, ai_msg = message_pair
            render_chat_message({"content": user_msg}, True)
            render_chat_message({"content": ai_msg}, False)

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
                # 将建议问题添加到输入框
                st.session_state.user_input = suggestion
                st.rerun()

def get_ai_response_smart(user_message: str, user_context: dict) -> dict:
    """
    智能AI响应 - 优先使用OpenAI API，失败时使用模拟响应

    Args:
        user_message: 用户输入的消息
        user_context: 用户上下文信息

    Returns:
        AI响应结果字典
    """
    # 检查AI助手是否可用
    if is_ai_assistant_available():
        try:
            ai_assistant = get_ai_assistant()

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

            # 调用AI助手
            response = ai_assistant.chat_sync(user_message, user_context, conversation_history)
            return response

        except Exception as e:
            st.error(f"AI助手调用失败: {str(e)}")
            # 降级到模拟响应

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

    # 显示AI状态
    render_ai_status()
    st.divider()

    # 获取用户上下文
    user_context = data_manager.get_user_overview(st.session_state.current_user_id) or {}

    # 聊天容器
    chat_container = st.container()

    with chat_container:
        # 显示欢迎消息
        if "chat_initialized" not in st.session_state:
            st.session_state.chat_initialized = True
            # 使用智能响应生成欢迎消息
            welcome_response = get_ai_response_smart("你好", user_context)
            welcome_msg = welcome_response["response"] if isinstance(welcome_response, dict) else welcome_response
            st.session_state.chat_history = [(None, welcome_msg)]

        # 显示聊天历史
        render_chat_history()

    # 输入区域
    st.divider()

    # 用户输入
    user_input = st.text_input(
        "💬 向AI助手提问：",
        placeholder="例如：我每月在娱乐上花多少钱？",
        key="user_input_field",
        value=st.session_state.get("user_input", "")
    )

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        send_button = st.button("📤 发送", use_container_width=True, type="primary")

    with col2:
        if st.button("🗑️ 清空", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.user_input = ""
            st.session_state.chat_initialized = False
            st.rerun()

    with col3:
        if st.button("💡 建议", use_container_width=True):
            st.session_state.show_suggestions = not st.session_state.get("show_suggestions", False)
            st.rerun()

    with col4:
        if st.button("⚙️ 设置", use_container_width=True):
            st.session_state.show_chat_settings = not st.session_state.get("show_chat_settings", False)
            st.rerun()

    # 处理用户输入
    if send_button and user_input.strip():
        # 显示处理状态
        with st.spinner("🤖 AI助手正在思考..."):
            # 获取AI响应
            ai_response_data = get_ai_response_smart(user_input, user_context)

            # 提取响应文本
            if isinstance(ai_response_data, dict):
                ai_response = ai_response_data["response"]
                intent = ai_response_data.get("intent", "general_query")
                confidence = ai_response_data.get("confidence", 0.8)
            else:
                ai_response = ai_response_data
                intent = "general_query"
                confidence = 0.8

            # 保存对话到历史
            st.session_state.chat_history.append((user_input, ai_response_data))

            # 保存到数据库
            data_manager.save_conversation(
                user_id=st.session_state.current_user_id,
                session_id=st.session_state.chat_session_id,
                message=user_input,
                response=ai_response,
                intent=intent,
                confidence=confidence
            )

            # 清空输入
            st.session_state.user_input = ""
            st.rerun()

    # 清空临时输入状态
    if "user_input" in st.session_state:
        del st.session_state.user_input

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