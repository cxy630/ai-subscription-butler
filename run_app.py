"""
启动脚本 - 运行AI订阅管家应用
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """启动Streamlit应用"""
    # 确保在项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # 检查并创建演示数据
    print("🔄 正在检查数据...")
    try:
        subprocess.run([sys.executable, "scripts/storage_demo.py"], check=True)
        print("✅ 数据准备完成")
    except subprocess.CalledProcessError:
        print("⚠️ 数据初始化失败，但应用仍可运行")
    except FileNotFoundError:
        print("ℹ️ 未找到初始化脚本，跳过数据准备")

    # 启动Streamlit应用
    print("🚀 正在启动AI订阅管家...")
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
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())