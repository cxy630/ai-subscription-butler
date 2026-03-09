#!/usr/bin/env python3
"""
测试环境变量加载
"""
import os
from pathlib import Path

# 手动加载.env文件
env_path = Path('.env')
if env_path.exists():
    print("Loading .env file...")
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

print("Environment Variables:")
print(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY', 'NOT SET')[:20]}...")
print(f"GEMINI_MODEL: {os.getenv('GEMINI_MODEL', 'NOT SET')}")
print(f"AI_PROVIDER: {os.getenv('AI_PROVIDER', 'NOT SET')}")

# 测试Gemini客户端
from core.ai.gemini_client import is_gemini_available
from core.ai.assistant import is_ai_assistant_available

print()
print("Client Status:")
print(f"Gemini available: {is_gemini_available()}")
print(f"AI Assistant available: {is_ai_assistant_available()}")