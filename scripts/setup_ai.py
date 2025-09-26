#!/usr/bin/env python3
"""
AI配置设置脚本 - 帮助用户配置OpenAI API
"""

import os
import sys
from pathlib import Path
import re

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.ai import get_env_template, is_ai_configured, get_ai_config

def print_header():
    """打印标题"""
    print("=" * 60)
    print("🤖 AI订阅管家 - OpenAI API配置向导")
    print("=" * 60)
    print()

def check_current_status():
    """检查当前配置状态"""
    print("📋 当前配置状态:")

    env_file = project_root / ".env"
    if env_file.exists():
        print(f"✅ 环境配置文件存在: {env_file}")
    else:
        print(f"❌ 环境配置文件不存在: {env_file}")

    if is_ai_configured():
        config = get_ai_config()
        print("✅ OpenAI API已配置")
        print(f"   模型: {config.openai_model}")
        print(f"   最大令牌: {config.openai_max_tokens}")
        print(f"   温度: {config.openai_temperature}")
    else:
        print("❌ OpenAI API未配置")

    print()

def validate_api_key(api_key: str) -> bool:
    """验证API密钥格式"""
    if not api_key or api_key.strip() == "":
        return False

    # OpenAI API密钥格式检查
    if not api_key.startswith("sk-"):
        return False

    # 基本长度检查
    if len(api_key) < 20:
        return False

    return True

def create_env_file():
    """创建.env文件"""
    print("📝 创建环境配置文件...")

    env_file = project_root / ".env"
    example_file = project_root / ".env.example"

    if env_file.exists():
        overwrite = input(f".env文件已存在，是否覆盖? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("取消操作")
            return False

    # 读取示例文件
    if example_file.exists():
        with open(example_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        # 使用内置模板
        content = get_env_template()

    # 写入.env文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 环境配置文件已创建: {env_file}")
    return True

def configure_openai():
    """配置OpenAI API"""
    print("🔑 配置OpenAI API...")
    print()

    print("📌 获取OpenAI API密钥:")
    print("   1. 访问 https://platform.openai.com/api-keys")
    print("   2. 登录您的OpenAI账户")
    print("   3. 点击 'Create new secret key'")
    print("   4. 复制生成的API密钥")
    print()

    # 获取API密钥
    while True:
        api_key = input("请输入您的OpenAI API密钥 (或按回车跳过): ").strip()

        if not api_key:
            print("⚠️ 跳过OpenAI配置，将使用模拟响应")
            return False

        if validate_api_key(api_key):
            break
        else:
            print("❌ API密钥格式不正确，请重新输入 (应以'sk-'开头)")

    # 获取其他配置
    model = input(f"选择模型 (默认: gpt-3.5-turbo): ").strip() or "gpt-3.5-turbo"

    try:
        max_tokens = int(input(f"最大令牌数 (默认: 1000): ").strip() or "1000")
    except ValueError:
        max_tokens = 1000

    try:
        temperature = float(input(f"温度参数 (默认: 0.7): ").strip() or "0.7")
    except ValueError:
        temperature = 0.7

    # 更新.env文件
    env_file = project_root / ".env"
    if not env_file.exists():
        if not create_env_file():
            return False

    # 读取现有内容
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 更新配置
    content = re.sub(r'OPENAI_API_KEY=.*', f'OPENAI_API_KEY={api_key}', content)
    content = re.sub(r'OPENAI_MODEL=.*', f'OPENAI_MODEL={model}', content)
    content = re.sub(r'OPENAI_MAX_TOKENS=.*', f'OPENAI_MAX_TOKENS={max_tokens}', content)
    content = re.sub(r'OPENAI_TEMPERATURE=.*', f'OPENAI_TEMPERATURE={temperature}', content)

    # 写入文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ OpenAI配置已保存")
    return True

def test_configuration():
    """测试配置"""
    print("🧪 测试AI配置...")

    try:
        from core.ai import get_openai_client, is_openai_available

        if is_openai_available():
            print("✅ OpenAI客户端初始化成功")

            # 简单的API测试（注释掉避免消耗令牌）
            # client = get_openai_client()
            # test_response = client.get_ai_response_sync(
            #     "测试", {"subscriptions": [], "monthly_spending": 0}
            # )
            # print(f"✅ API调用测试成功")

        else:
            print("⚠️ OpenAI API不可用，将使用模拟响应")

    except Exception as e:
        print(f"❌ 配置测试失败: {e}")

def print_usage_instructions():
    """打印使用说明"""
    print("\n" + "=" * 60)
    print("🚀 配置完成！使用说明:")
    print("=" * 60)
    print()
    print("1. 启动应用:")
    print("   python run_app.py")
    print("   或")
    print("   streamlit run app/main.py")
    print()
    print("2. AI功能说明:")
    print("   - 如果配置了OpenAI API，将使用真实的AI响应")
    print("   - 如果未配置，将使用智能模拟响应")
    print("   - 在AI助手页面可以看到当前状态")
    print()
    print("3. 配置文件位置:")
    print(f"   环境配置: {project_root / '.env'}")
    print(f"   示例文件: {project_root / '.env.example'}")
    print()
    print("4. 获取帮助:")
    print("   - 查看文档: docs/ai-integration.md")
    print("   - GitHub问题: https://github.com/cxy630/ai-subscription-butler/issues")
    print()

def main():
    """主函数"""
    print_header()

    # 检查当前状态
    check_current_status()

    # 询问用户操作
    if is_ai_configured():
        action = input("OpenAI已配置。选择操作: [T]测试 [R]重新配置 [Q]退出 (T/r/q): ").strip().lower()

        if action == 'r':
            configure_openai()
            test_configuration()
        elif action == 't':
            test_configuration()
        else:
            print("退出配置向导")
            return
    else:
        action = input("选择操作: [C]配置OpenAI [S]跳过配置 [Q]退出 (C/s/q): ").strip().lower()

        if action == 'c':
            if configure_openai():
                test_configuration()
        elif action == 's':
            print("✅ 跳过OpenAI配置，应用将使用模拟响应")
        else:
            print("退出配置向导")
            return

    print_usage_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 配置向导已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()