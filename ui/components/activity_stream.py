import streamlit as st
from datetime import datetime
from core.agents.activity_logger import activity_logger

def render_recent_activity_stream(limit: int = 5):
    """
    渲染最近的活动日志流
    模拟 'AI正在工作' 的实时感
    """
    st.subheader("🤖 AI 管家工作日志")
    
    # 获取最新的活动
    activities = activity_logger.get_activities(limit=limit)
    
    if not activities:
        st.info("AI 管家正在待命，暂无活动记录。")
        return

    # 使用容器创建一个类似终端或聊天流的效果
    with st.container():
        for act in activities:
            # 根据状态选择图标和颜色
            status_style = {
                "success": ("✅", "green"),
                "failed": ("❌", "red"),
                "pending": ("⏳", "orange")
            }
            icon, color = status_style.get(act.status, ("📝", "grey"))
            
            # 格式化时间 (极其稳健的处理)
            try:
                if act.timestamp is None:
                    time_obj = datetime.now()
                elif isinstance(act.timestamp, str):
                    time_obj = datetime.fromisoformat(act.timestamp)
                elif hasattr(act.timestamp, "strftime"):
                    time_obj = act.timestamp
                else:
                    time_obj = datetime.now()
                time_str = time_obj.strftime("%H:%M")
            except Exception as te:
                st.error(f"Time format error: {te} for {act.timestamp}")
                time_str = "00:00"
            
            # 使用 Chat Message 风格展示，让它看起来更像是一个对话/汇报
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f"**{time_str}** | {act.description}")
                if act.details:
                    with st.expander("查看详情"):
                        st.json(act.details)

    # 底部添加一个小提示，增强活跃感
    st.caption(f"⚡ 系统正在后台实时监控您的 {len(activities)}+ 个数据点...")
