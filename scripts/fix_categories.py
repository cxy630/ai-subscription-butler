"""
批量修正订阅分类
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def fix_categories():
    """修正订阅分类"""
    print("\n" + "="*60)
    print("Fixing Subscription Categories")
    print("="*60 + "\n")

    # 定义需要修正的服务和对应的正确分类
    corrections = {
        "百度云盘": "storage",
        "Aliyun": "business",
        "夸克网盘": "storage"
    }

    # 读取订阅数据
    subscriptions_file = project_root / "data" / "subscriptions.json"

    if not subscriptions_file.exists():
        print(f"[ERROR] Subscriptions file not found: {subscriptions_file}")
        return

    # 加载数据
    with open(subscriptions_file, 'r', encoding='utf-8') as f:
        subscriptions = json.load(f)

    print(f"Total subscriptions: {len(subscriptions)}\n")

    total_fixed = 0
    modified = False

    for sub in subscriptions:
        service_name = sub.get("service_name")
        current_category = sub.get("category")

        # 检查是否需要修正
        if service_name in corrections:
            correct_category = corrections[service_name]

            if current_category != correct_category:
                print(f"[FIXING] {service_name}")
                print(f"  Current category: {current_category}")
                print(f"  Correct category: {correct_category}")

                # 更新分类
                sub["category"] = correct_category
                modified = True

                print(f"  Status: [SUCCESS] Updated!")
                total_fixed += 1
                print()
            else:
                print(f"[OK] {service_name} - already correct: {current_category}")
                print()

    # 保存修改
    if modified:
        print("Saving changes...")
        with open(subscriptions_file, 'w', encoding='utf-8') as f:
            json.dump(subscriptions, f, ensure_ascii=False, indent=2)
        print("[SUCCESS] Changes saved to file!")
        print()

    print("="*60)
    print(f"Summary: Fixed {total_fixed} subscription(s)")
    print("="*60 + "\n")

    # 显示修正后的结果
    if total_fixed > 0:
        print("Verification - Updated categories:")
        print("-"*60)

        for sub in subscriptions:
            if sub.get("service_name") in corrections:
                print(f"  {sub['service_name']}: {sub['category']}")

        print()


if __name__ == "__main__":
    try:
        fix_categories()
    except Exception as e:
        print(f"\n[ERROR] Script failed: {e}")
        import traceback
        traceback.print_exc()