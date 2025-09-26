#!/usr/bin/env python3
"""
测试运行脚本 - 运行项目的所有测试
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """运行所有测试"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("🧪 运行AI订阅管家测试套件")
    print("=" * 50)

    # 检查pytest是否安装
    try:
        import pytest
        print("✅ pytest已安装")
    except ImportError:
        print("❌ pytest未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])
            import pytest
            print("✅ pytest安装成功")
        except subprocess.CalledProcessError:
            print("❌ pytest安装失败")
            return False

    # 运行测试
    print("\n🔍 运行单元测试...")

    try:
        # 运行pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--color=yes"
        ], capture_output=True, text=True)

        print(result.stdout)

        if result.stderr:
            print("警告信息:")
            print(result.stderr)

        if result.returncode == 0:
            print("\n🎉 所有测试通过！")
            return True
        else:
            print(f"\n❌ 测试失败 (退出代码: {result.returncode})")
            return False

    except FileNotFoundError:
        print("❌ 无法运行pytest")
        return False
    except Exception as e:
        print(f"❌ 测试执行出错: {e}")
        return False

def run_specific_tests(test_pattern):
    """运行特定的测试"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print(f"🔍 运行匹配 '{test_pattern}' 的测试...")

    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            f"tests/{test_pattern}",
            "-v"
        ], capture_output=True, text=True)

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ 测试执行出错: {e}")
        return False

def show_test_coverage():
    """显示测试覆盖率"""
    print("📊 计算测试覆盖率...")

    try:
        # 尝试安装coverage
        subprocess.check_call([sys.executable, "-m", "pip", "install", "coverage"],
                             capture_output=True)

        # 运行coverage
        subprocess.run([
            sys.executable, "-m", "coverage", "run", "--source=core", "-m", "pytest", "tests/"
        ], capture_output=True)

        # 显示报告
        result = subprocess.run([
            sys.executable, "-m", "coverage", "report"
        ], capture_output=True, text=True)

        print(result.stdout)

        # 生成HTML报告
        subprocess.run([
            sys.executable, "-m", "coverage", "html"
        ], capture_output=True)

        print("📄 HTML覆盖率报告已生成: htmlcov/index.html")

    except Exception as e:
        print(f"⚠️ 覆盖率分析失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--coverage":
            show_test_coverage()
        elif sys.argv[1] == "--help":
            print("测试运行选项:")
            print("  python scripts/run_tests.py           # 运行所有测试")
            print("  python scripts/run_tests.py --coverage # 运行测试并生成覆盖率报告")
            print("  python scripts/run_tests.py test_*.py  # 运行特定测试文件")
        else:
            # 运行特定测试
            success = run_specific_tests(sys.argv[1])
            sys.exit(0 if success else 1)
    else:
        # 运行所有测试
        success = run_tests()
        if success:
            print("\n💡 提示:")
            print("  运行覆盖率分析: python scripts/run_tests.py --coverage")
            print("  运行特定测试: python scripts/run_tests.py test_openai_client.py")

        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()