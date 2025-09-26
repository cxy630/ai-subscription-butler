"""
AI配置管理 - 处理AI相关的配置和设置
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

@dataclass
class AIConfig:
    """AI配置类"""

    # OpenAI配置
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.7

    # 响应配置
    max_conversation_history: int = 10
    default_language: str = "zh-CN"
    response_timeout: int = 30

    # 功能开关
    enable_insights_generation: bool = True
    enable_conversation_memory: bool = True
    enable_fallback_responses: bool = True

    # 安全配置
    content_filter_enabled: bool = True
    max_daily_requests: int = 1000

    @classmethod
    def from_env(cls) -> "AIConfig":
        """从环境变量创建配置"""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            openai_max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
            openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            max_conversation_history=int(os.getenv("AI_MAX_HISTORY", "10")),
            default_language=os.getenv("AI_DEFAULT_LANGUAGE", "zh-CN"),
            response_timeout=int(os.getenv("AI_RESPONSE_TIMEOUT", "30")),
            enable_insights_generation=os.getenv("AI_ENABLE_INSIGHTS", "true").lower() == "true",
            enable_conversation_memory=os.getenv("AI_ENABLE_MEMORY", "true").lower() == "true",
            enable_fallback_responses=os.getenv("AI_ENABLE_FALLBACK", "true").lower() == "true",
            content_filter_enabled=os.getenv("AI_CONTENT_FILTER", "true").lower() == "true",
            max_daily_requests=int(os.getenv("AI_MAX_DAILY_REQUESTS", "1000"))
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "openai_api_key": "***" if self.openai_api_key else None,  # 隐藏敏感信息
            "openai_model": self.openai_model,
            "openai_max_tokens": self.openai_max_tokens,
            "openai_temperature": self.openai_temperature,
            "max_conversation_history": self.max_conversation_history,
            "default_language": self.default_language,
            "response_timeout": self.response_timeout,
            "enable_insights_generation": self.enable_insights_generation,
            "enable_conversation_memory": self.enable_conversation_memory,
            "enable_fallback_responses": self.enable_fallback_responses,
            "content_filter_enabled": self.content_filter_enabled,
            "max_daily_requests": self.max_daily_requests
        }

    def is_valid(self) -> bool:
        """检查配置是否有效"""
        return self.openai_api_key is not None and len(self.openai_api_key.strip()) > 0

# 全局配置实例
_ai_config = None

def get_ai_config() -> AIConfig:
    """获取AI配置实例"""
    global _ai_config

    if _ai_config is None:
        _ai_config = AIConfig.from_env()

    return _ai_config

def update_ai_config(**kwargs) -> None:
    """更新AI配置"""
    global _ai_config

    if _ai_config is None:
        _ai_config = AIConfig.from_env()

    for key, value in kwargs.items():
        if hasattr(_ai_config, key):
            setattr(_ai_config, key, value)

def is_ai_configured() -> bool:
    """检查AI是否已正确配置"""
    config = get_ai_config()
    return config.is_valid()

def get_env_template() -> str:
    """获取环境变量模板"""
    return """# AI订阅管家 - AI配置
# 复制此文件为 .env 并填入实际值

# OpenAI配置 (必需)
OPENAI_API_KEY=sk-your-openai-api-key-here

# OpenAI模型配置 (可选)
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# AI助手配置 (可选)
AI_MAX_HISTORY=10
AI_DEFAULT_LANGUAGE=zh-CN
AI_RESPONSE_TIMEOUT=30

# 功能开关 (可选)
AI_ENABLE_INSIGHTS=true
AI_ENABLE_MEMORY=true
AI_ENABLE_FALLBACK=true
AI_CONTENT_FILTER=true
AI_MAX_DAILY_REQUESTS=1000
"""