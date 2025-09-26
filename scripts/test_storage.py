"""
存储方案测试脚本
演示JSON和SQLite两种存储方案的使用
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database.data_interface import DataManager, StorageBackend
from datetime import datetime
import time


def test_storage_performance():
    """测试存储性能对比"""
    print("🧪 存储方案性能测试")
    print("=" * 50)

    # 测试数据
    test_user_data = {
        "email": "perf_test@example.com",
        "password_hash": "$2b$12$test_hash",
        "name": "性能测试用户"
    }

    test_subscription_data = {
        "service_name": "测试服务",
        "price": 29.99,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "category": "productivity",
        "status": "active",
        "next_billing_date": "2025-03-01"
    }

    # JSON存储测试
    print("\n📄 JSON存储测试:")
    json_manager = DataManager(StorageBackend.JSON)

    start_time = time.time()

    # 创建用户
    user = json_manager.create_user(**test_user_data)
    user_id = user["id"] if user else None

    # 创建多个订阅
    if user_id:
        for i in range(10):
            subscription_data = test_subscription_data.copy()
            subscription_data["service_name"] = f"测试服务{i+1}"
            subscription_data["price"] = 29.99 + i
            json_manager.create_subscription(user_id, subscription_data)

    # 查询用户概览
    overview = json_manager.get_user_overview(user_id) if user_id else None

    json_time = time.time() - start_time
    print(f"  ⏱️  耗时: {json_time:.3f}秒")
    print(f"  📊  结果: {overview['total_subscriptions'] if overview else 0}个订阅，月度支出: ¥{overview['monthly_spending'] if overview else 0}")

    # SQLite存储测试
    print("\n🗄️  SQLite存储测试:")
    sqlite_manager = DataManager(StorageBackend.SQLITE)

    start_time = time.time()

    # 创建用户（可能已存在）
    sqlite_user = sqlite_manager.create_user("perf_sqlite@example.com", "$2b$12$test_hash", "SQLite测试用户")
    if not sqlite_user:
        sqlite_user = sqlite_manager.get_user_by_email("perf_sqlite@example.com")

    sqlite_user_id = sqlite_user["id"] if sqlite_user else None

    # 创建多个订阅
    if sqlite_user_id:
        for i in range(10):
            subscription_data = test_subscription_data.copy()
            subscription_data["service_name"] = f"SQLite测试服务{i+1}"
            subscription_data["price"] = 29.99 + i
            sqlite_manager.create_subscription(sqlite_user_id, subscription_data)

    # 查询用户概览
    sqlite_overview = sqlite_manager.get_user_overview(sqlite_user_id) if sqlite_user_id else None

    sqlite_time = time.time() - start_time
    print(f"  ⏱️  耗时: {sqlite_time:.3f}秒")
    print(f"  📊  结果: {sqlite_overview['total_subscriptions'] if sqlite_overview else 0}个订阅，月度支出: ¥{sqlite_overview['monthly_spending'] if sqlite_overview else 0}")

    # 对比总结
    print("\n📈 性能对比总结:")
    print(f"  JSON存储: {json_time:.3f}秒")
    print(f"  SQLite存储: {sqlite_time:.3f}秒")
    if json_time > 0 and sqlite_time > 0:
        faster = "SQLite" if sqlite_time < json_time else "JSON"
        ratio = max(json_time, sqlite_time) / min(json_time, sqlite_time)
        print(f"  🏆 {faster}存储更快 (快{ratio:.1f}倍)")


def demo_storage_features():
    """演示存储功能"""
    print("\n🎭 存储功能演示")
    print("=" * 50)

    # 使用JSON存储演示
    manager = DataManager(StorageBackend.JSON)

    print("\n1️⃣  创建演示用户")
    user = manager.get_user_by_email("demo@example.com")
    if not user:
        user = manager.create_user("demo@example.com", "$2b$12$demo_hash", "演示用户")
    print(f"  ✅ 用户: {user['name']} ({user['email']})")

    user_id = user["id"]

    print("\n2️⃣  添加订阅服务")
    demo_subscriptions = [
        {
            "service_name": "Netflix",
            "price": 15.99,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "entertainment",
            "status": "active"
        },
        {
            "service_name": "Spotify",
            "price": 9.99,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "entertainment",
            "status": "active"
        },
        {
            "service_name": "ChatGPT Plus",
            "price": 140.0,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "productivity",
            "status": "active"
        }
    ]

    existing_subscriptions = manager.get_user_subscriptions(user_id)
    for sub_data in demo_subscriptions:
        # 检查是否已存在
        exists = any(sub["service_name"] == sub_data["service_name"] for sub in existing_subscriptions)
        if not exists:
            subscription = manager.create_subscription(user_id, sub_data)
            print(f"  ➕ 添加: {subscription['service_name']} - ¥{subscription['price']}/{subscription['billing_cycle']}")

    print("\n3️⃣  用户概览分析")
    overview = manager.get_user_overview(user_id)
    if overview:
        print(f"  📊 总订阅数: {overview['total_subscriptions']}")
        print(f"  🔥 活跃订阅: {overview['active_subscriptions']}")
        print(f"  💰 月度支出: ¥{overview['monthly_spending']}")

        print(f"\n  📂 分类统计:")
        for category, stats in overview.get('subscription_categories', {}).items():
            print(f"    {category}: {stats['count']}个服务, ¥{stats['spending']:.2f}/月")

    print("\n4️⃣  搜索功能测试")
    search_results = manager.search_subscriptions(user_id, "Netflix")
    if search_results:
        for result in search_results:
            print(f"  🔍 找到: {result['service_name']} - {result['category']}")

    print("\n5️⃣  对话记录功能")
    session_id = "demo_session_001"
    conversation = manager.save_conversation(
        user_id=user_id,
        session_id=session_id,
        message="我每月在娱乐上花多少钱？",
        response="根据您的订阅记录，您每月在娱乐类服务上花费约¥25.98，包括Netflix和Spotify。",
        intent="query_spending_by_category",
        confidence=0.95
    )
    print(f"  💬 保存对话: {conversation['message'][:30]}...")

    # 获取对话历史
    history = manager.get_session_history(session_id, 5)
    print(f"  📜 会话历史: {len(history)}条记录")


def show_storage_comparison():
    """显示存储方案对比"""
    print("\n📋 存储方案对比")
    print("=" * 80)

    comparison_data = [
        ("特性", "JSON文件", "SQLite", "PostgreSQL(未来)"),
        ("安装要求", "无", "内置", "需要服务器"),
        ("性能", "中等", "好", "很好"),
        ("查询能力", "基础", "SQL查询", "高级SQL"),
        ("并发支持", "有限", "支持", "优秀"),
        ("数据完整性", "基础", "ACID", "ACID"),
        ("适用场景", "开发/演示", "中小型应用", "生产环境"),
        ("部署复杂度", "简单", "简单", "复杂"),
        ("扩展性", "有限", "中等", "优秀")
    ]

    for row in comparison_data:
        print(f"  {row[0]:<12} | {row[1]:<12} | {row[2]:<12} | {row[3]:<15}")
        if row[0] == "特性":
            print("  " + "-" * 70)


def main():
    """主函数"""
    print("🚀 AI订阅管家 - 存储方案测试")
    print("=" * 80)

    try:
        # 显示存储方案对比
        show_storage_comparison()

        # 演示存储功能
        demo_storage_features()

        # 性能测试
        test_storage_performance()

        print("\n✅ 所有测试完成！")
        print("\n💡 建议:")
        print("  - 开发阶段：使用JSON存储，简单易用")
        print("  - 测试阶段：使用SQLite，性能更好")
        print("  - 生产环境：使用PostgreSQL，功能完整")

    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()