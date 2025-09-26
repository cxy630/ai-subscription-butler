"""
简化存储方案测试 - 无依赖版本
演示JSON存储的基本功能
"""

import sys
from pathlib import Path
import json
import uuid
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_json_storage():
    """测试JSON存储基本功能"""
    print("JSON存储功能测试")
    print("=" * 50)

    # 确保data目录存在
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    # 测试数据文件
    users_file = data_dir / "users.json"
    subscriptions_file = data_dir / "subscriptions.json"

    # 1. 创建用户
    print("\n1️⃣  创建测试用户")
    user_data = {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "name": "测试用户",
        "created_at": datetime.now().isoformat(),
        "subscription_tier": "free"
    }

    users = []
    if users_file.exists():
        with open(users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)

    # 检查用户是否已存在
    existing_user = None
    for user in users:
        if user["email"] == user_data["email"]:
            existing_user = user
            break

    if not existing_user:
        users.append(user_data)
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        print(f"  ✅ 用户已创建: {user_data['name']} ({user_data['email']})")
    else:
        user_data = existing_user
        print(f"  ✅ 用户已存在: {existing_user['name']} ({existing_user['email']})")

    user_id = user_data["id"]

    # 2. 添加订阅
    print("\n2️⃣  添加测试订阅")
    test_subscriptions = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "service_name": "Netflix",
            "price": 15.99,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "entertainment",
            "status": "active",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "service_name": "ChatGPT Plus",
            "price": 140.0,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "productivity",
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
    ]

    subscriptions = []
    if subscriptions_file.exists():
        with open(subscriptions_file, 'r', encoding='utf-8') as f:
            subscriptions = json.load(f)

    # 添加新订阅（如果不存在）
    added_count = 0
    for sub_data in test_subscriptions:
        # 检查是否已存在
        exists = any(
            sub["user_id"] == user_id and sub["service_name"] == sub_data["service_name"]
            for sub in subscriptions
        )

        if not exists:
            subscriptions.append(sub_data)
            added_count += 1
            print(f"  ➕ 添加: {sub_data['service_name']} - ¥{sub_data['price']}/{sub_data['billing_cycle']}")

    if added_count > 0:
        with open(subscriptions_file, 'w', encoding='utf-8') as f:
            json.dump(subscriptions, f, ensure_ascii=False, indent=2)
        print(f"  ✅ 成功添加 {added_count} 个订阅")
    else:
        print("  ✅ 订阅已存在，无需重复添加")

    # 3. 查询和分析
    print("\n3️⃣  数据查询和分析")

    # 获取用户的所有订阅
    user_subscriptions = [sub for sub in subscriptions if sub["user_id"] == user_id]
    active_subscriptions = [sub for sub in user_subscriptions if sub.get("status") == "active"]

    print(f"  📊 总订阅数: {len(user_subscriptions)}")
    print(f"  🔥 活跃订阅: {len(active_subscriptions)}")

    # 计算月度支出
    monthly_spending = 0
    category_stats = {}

    for sub in active_subscriptions:
        price = sub.get("price", 0)
        cycle = sub.get("billing_cycle", "monthly")
        category = sub.get("category", "other")

        # 转换为月度成本
        if cycle == "monthly":
            monthly_price = price
        elif cycle == "yearly":
            monthly_price = price / 12
        elif cycle == "weekly":
            monthly_price = price * 4.33
        else:
            monthly_price = price

        monthly_spending += monthly_price

        # 分类统计
        if category not in category_stats:
            category_stats[category] = {"count": 0, "spending": 0}
        category_stats[category]["count"] += 1
        category_stats[category]["spending"] += monthly_price

    print(f"  💰 月度支出: ¥{monthly_spending:.2f}")

    print(f"\n  📂 分类统计:")
    for category, stats in category_stats.items():
        print(f"    {category}: {stats['count']}个服务, ¥{stats['spending']:.2f}/月")

    # 4. 文件大小统计
    print("\n4️⃣  存储文件统计")
    if users_file.exists():
        users_size = users_file.stat().st_size
        print(f"  📄 用户文件: {users_size} 字节")

    if subscriptions_file.exists():
        subs_size = subscriptions_file.stat().st_size
        print(f"  📄 订阅文件: {subs_size} 字节")

    return {
        "users_count": len(users),
        "subscriptions_count": len(user_subscriptions),
        "monthly_spending": monthly_spending,
        "categories": len(category_stats)
    }


def show_storage_pros_cons():
    """显示存储方案优缺点"""
    print("\n📋 数据存储方案对比")
    print("=" * 80)

    print("\n📄 JSON文件存储:")
    print("  ✅ 优点:")
    print("    • 无需安装数据库服务")
    print("    • 文件格式直观，便于调试")
    print("    • 适合快速原型开发")
    print("    • 便携性好，易于备份")
    print("  ❌ 缺点:")
    print("    • 不支持复杂查询")
    print("    • 并发访问有限制")
    print("    • 大数据量时性能下降")
    print("    • 没有数据完整性保证")

    print("\n🗄️ SQLite数据库:")
    print("  ✅ 优点:")
    print("    • 支持标准SQL查询")
    print("    • ACID事务保证")
    print("    • 性能较好")
    print("    • 单文件数据库，便于部署")
    print("  ❌ 缺点:")
    print("    • 并发写入有限制")
    print("    • 不适合大型应用")
    print("    • 功能相对简单")

    print("\n🐘 PostgreSQL (生产环境):")
    print("  ✅ 优点:")
    print("    • 功能完整，性能优秀")
    print("    • 优秀的并发支持")
    print("    • 丰富的数据类型和扩展")
    print("    • 成熟的生态系统")
    print("  ❌ 缺点:")
    print("    • 需要安装和配置服务器")
    print("    • 部署复杂度较高")
    print("    • 资源消耗相对较大")


def main():
    """主函数"""
    print("🚀 AI订阅管家 - 存储方案演示")
    print("=" * 60)

    try:
        # 测试JSON存储
        results = test_json_storage()

        # 显示方案对比
        show_storage_pros_cons()

        print(f"\n✅ 测试完成！")
        print(f"  📊 测试结果:")
        print(f"    • 用户数量: {results['users_count']}")
        print(f"    • 订阅数量: {results['subscriptions_count']}")
        print(f"    • 月度支出: ¥{results['monthly_spending']:.2f}")
        print(f"    • 服务类别: {results['categories']}个")

        print(f"\n💡 当前建议:")
        print(f"  • 开发阶段: 使用JSON存储，快速开始")
        print(f"  • 有Python环境: 可以使用SQLite获得更好性能")
        print(f"  • 生产部署: 考虑PostgreSQL或云数据库")

        print(f"\n📁 数据文件位置: {project_root / 'data'}")

    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()