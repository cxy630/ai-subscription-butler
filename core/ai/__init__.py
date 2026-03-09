"""
AI模块 - 人工智能相关功能模块
"""

from .config import AIConfig, get_ai_config, is_ai_configured, get_env_template
from .openai_client import OpenAIClient, get_openai_client, is_openai_available
from .gemini_client import GeminiClient, get_gemini_client, is_gemini_available
from .assistant import (
    AIAssistant,
    get_ai_assistant,
    is_ai_assistant_available,
    chat_with_ai,
    chat_with_ai_sync,
    generate_ai_insights
)

__all__ = [
    # 配置
    "AIConfig",
    "get_ai_config",
    "is_ai_configured",
    "get_env_template",

    # OpenAI客户端
    "OpenAIClient",
    "get_openai_client",
    "is_openai_available",

    # Gemini客户端
    "GeminiClient",
    "get_gemini_client",
    "is_gemini_available",

    # AI助手
    "AIAssistant",
    "get_ai_assistant",
    "is_ai_assistant_available",
    "chat_with_ai",
    "chat_with_ai_sync",
    "generate_ai_insights"
]