"""
启动脚本 - 运行AI订阅管家应用
"""

import subprocess
import sys
import os
from pathlib import Path

def check_ai_configuration():
    """检查AI配置"""
    try:
        # 添加项目路径
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))

        from core.ai import is_ai_configured, get_ai_config

        if is_ai_configured():
            config = get_ai_config()
            print(f"✅ AI配置正常 (模型: {config.openai_model})")
            return True
        else:
            print("⚠️ OpenAI API未配置，将使用模拟响应")
            print("💡 运行 'python scripts/setup_ai.py' 配置AI功能")
            return False

    except ImportError:
        print("⚠️ AI模块不可用")
        return False
    except Exception as e:
        print(f"⚠️ AI配置检查失败: {e}")
        return False

def main():
    """启动Streamlit应用"""
    # 确保在项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)

    print("🤖 AI订阅管家启动中...")
    print("=" * 50)

    # 检查AI配置
    print("🔍 检查AI配置...")
    check_ai_configuration()

    # 检查并创建演示数据
    print("\n📊 检查演示数据...")
    try:
        subprocess.run([sys.executable, "scripts/storage_demo.py"], check=True)
        print("✅ 演示数据准备完成")
    except subprocess.CalledProcessError:
        print("⚠️ 数据初始化失败，但应用仍可运行")
    except FileNotFoundError:
        print("ℹ️ 未找到初始化脚本，跳过数据准备")

    print("\n🚀 启动Streamlit应用...")
    print("=" * 50)

    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app/main.py",
            "--server.port=8501",
            "--server.headless=false",
            "--browser.gatherUsageStats=false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        print("\n💡 请确保已安装依赖:")
        print("   pip install -r requirements.txt")
        print("\n🔧 如需配置AI功能:")
        print("   python scripts/setup_ai.py")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())