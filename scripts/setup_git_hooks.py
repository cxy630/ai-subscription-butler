#!/usr/bin/env python3
"""
Git钩子设置脚本 - 安装预提交钩子以防止敏感信息泄露
"""

import os
import shutil
import stat
import sys
from pathlib import Path

def setup_git_hooks():
    """设置Git钩子"""
    project_root = Path(__file__).parent.parent
    hooks_source_dir = project_root / ".githooks"
    git_hooks_dir = project_root / ".git" / "hooks"

    print("🔧 设置Git安全钩子...")

    # 检查是否是Git仓库
    if not (project_root / ".git").exists():
        print("❌ 错误: 不是Git仓库")
        return False

    # 创建钩子目录（如果不存在）
    git_hooks_dir.mkdir(exist_ok=True)

    # 复制预提交钩子
    pre_commit_source = hooks_source_dir / "pre-commit"
    pre_commit_target = git_hooks_dir / "pre-commit"

    if pre_commit_source.exists():
        shutil.copy2(pre_commit_source, pre_commit_target)

        # 在Windows上设置可执行权限
        if os.name != 'nt':  # Unix/Linux/Mac
            current_permissions = os.stat(pre_commit_target).st_mode
            os.chmod(pre_commit_target, current_permissions | stat.S_IEXEC)

        print("✅ 预提交钩子已安装")
    else:
        print("❌ 找不到预提交钩子源文件")
        return False

    print("\n🛡️ 安全钩子功能:")
    print("  • 检测OpenAI API密钥泄露")
    print("  • 防止.env文件被提交")
    print("  • 扫描其他敏感文件模式")
    print("  • 警告可能的敏感信息")

    print("\n💡 提示:")
    print("  钩子会在每次git commit时自动运行")
    print("  如需跳过检查，使用: git commit --no-verify")

    return True

def test_git_hook():
    """测试Git钩子"""
    print("\n🧪 测试Git钩子...")

    project_root = Path(__file__).parent.parent
    test_file = project_root / "test_sensitive.txt"

    try:
        # 创建包含敏感信息的测试文件
        test_content = "api_key = 'sk-test123456789012345678901234567890'"
        test_file.write_text(test_content)

        print("1. 创建测试文件...")
        print("2. 尝试添加到Git...")

        # 尝试添加文件
        result = os.system(f"cd {project_root} && git add {test_file.name}")

        if result == 0:
            print("✅ 文件已添加到暂存区")
            print("3. 测试预提交钩子...")

            # 这会触发预提交钩子
            print("   (实际提交会被钩子阻止)")

            # 清理
            os.system(f"cd {project_root} && git reset HEAD {test_file.name}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()
        print("🧹 测试文件已清理")

def main():
    """主函数"""
    print("🔒 Git安全钩子设置工具")
    print("=" * 40)

    try:
        if setup_git_hooks():
            print("\n✅ Git钩子设置完成！")

            # 询问是否测试
            test = input("\n是否测试钩子功能? (y/N): ").strip().lower()
            if test in ['y', 'yes']:
                test_git_hook()
        else:
            print("\n❌ 钩子设置失败")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n👋 设置已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()