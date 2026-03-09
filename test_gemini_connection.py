#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Gemini模型连接
验证API密钥和模型配置是否正确
"""

import os
import sys
import io
from pathlib import Path

# 设置UTF-8编码输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
env_path = project_root / '.env'
if env_path.exists():
    print("📄 加载 .env 文件...")
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value
    print("✅ .env 文件加载完成\n")
else:
    print("⚠️  未找到 .env 文件\n")

# 显示配置信息
print("=" * 60)
print("🔍 Gemini 模型连接测试")
print("=" * 60)
print()

api_key = os.getenv('GEMINI_API_KEY', '')
model_name = os.getenv('GEMINI_MODEL', 'gemini-3-flash')
ai_provider = os.getenv('AI_PROVIDER', 'gemini')

print("📋 配置信息:")
print(f"  AI Provider: {ai_provider}")
print(f"  Model Name: {model_name}")
print(f"  API Key: {api_key[:20]}..." if api_key else "  API Key: ❌ 未设置")
print()

# 测试1: 检查API密钥
if not api_key:
    print("❌ 错误: GEMINI_API_KEY 未设置")
    print("   请在 .env 文件中设置 GEMINI_API_KEY")
    sys.exit(1)

print("✅ API密钥已配置")

# 测试2: 尝试导入Gemini客户端
try:
    print("\n📦 导入Gemini客户端...")
    from core.ai.gemini_client import get_gemini_client, is_gemini_available
    print("✅ Gemini客户端模块导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("   请确保已安装依赖: pip install -r requirements.txt")
    sys.exit(1)

# 测试3: 检查客户端是否可用
print("\n🔌 检查Gemini客户端可用性...")
if not is_gemini_available():
    print("❌ Gemini客户端不可用")
    print("   可能原因:")
    print("   - API密钥无效")
    print("   - 网络连接问题")
    print("   - 依赖包未安装")
    sys.exit(1)

print("✅ Gemini客户端可用")

# 测试4: 获取客户端实例
print("\n🔧 初始化Gemini客户端...")
try:
    client = get_gemini_client()
    if client is None:
        print("❌ 无法创建Gemini客户端实例")
        sys.exit(1)
    
    print(f"✅ 客户端初始化成功")
    print(f"   模型名称: {client.model_name}")
except Exception as e:
    print(f"❌ 客户端初始化失败: {e}")
    sys.exit(1)

# 测试5: 发送测试请求
print("\n🚀 发送测试请求...")
print("   测试消息: '你好，请回复OK'")
print("   模型: " + model_name)
print()

try:
    # 使用同步方法测试
    test_message = "你好，请回复OK"
    response = client.get_ai_response_sync(
        user_message=test_message,
        user_context={"user": {"id": "test_user"}},
        user_id="test_user"
    )
    
    if response and response.get("response"):
        print("=" * 60)
        print("✅ 连接测试成功！")
        print("=" * 60)
        print()
        print("📨 模型响应:")
        print("-" * 60)
        print(response.get("response", ""))
        print("-" * 60)
        print()
        print("📊 响应详情:")
        print(f"  意图: {response.get('intent', 'N/A')}")
        print(f"  置信度: {response.get('confidence', 'N/A')}")
        print(f"  模型: {response.get('model', 'N/A')}")
        if 'tokens_used' in response:
            print(f"  Token使用: {response.get('tokens_used', 0)}")
        print()
        print("🎉 Gemini模型连接正常，可以正常使用！")
        
    else:
        print("⚠️  收到响应，但响应格式异常")
        print(f"   响应内容: {response}")
        
except Exception as e:
    print("=" * 60)
    print("❌ 连接测试失败")
    print("=" * 60)
    print()
    print(f"错误信息: {str(e)}")
    print()
    print("可能的原因:")
    print("  1. API密钥无效或已过期")
    print("  2. 模型名称不正确 (当前: " + model_name + ")")
    print("  3. 网络连接问题")
    print("  4. API配额已用完")
    print("  5. 模型不可用或需要特殊权限")
    print()
    print("建议:")
    print("  - 检查 .env 文件中的 GEMINI_API_KEY")
    print("  - 确认模型名称是否正确 (gemini-3-flash)")
    print("  - 访问 https://aistudio.google.com/ 检查API状态")
    print()
    sys.exit(1)

print("=" * 60)
