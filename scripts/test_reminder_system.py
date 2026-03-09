"""
测试提醒系统功能
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.services.reminder_system import reminder_system


def test_billing_date_calculation():
    """测试账单日期计算"""
    print("=" * 60)
    print("测试账单日期计算")
    print("=" * 60)

    start_date = datetime(2025, 1, 31, 0, 0, 0)
    print(f"\n开始日期: {start_date.strftime('%Y-%m-%d')}\n")

    # 测试月付
    print("月付测试:")
    for i in range(1, 6):
        next_date = reminder_system.calculate_next_billing_date(start_date, "monthly", i)
        print(f"  第{i}次续费: {next_date.strftime('%Y-%m-%d')}")

    # 测试年付
    print("\n年付测试:")
    for i in range(1, 4):
        next_date = reminder_system.calculate_next_billing_date(start_date, "yearly", i)
        print(f"  第{i}次续费: {next_date.strftime('%Y-%m-%d')}")

    # 测试周付
    print("\n周付测试:")
    start_date = datetime(2025, 1, 1, 0, 0, 0)
    for i in range(1, 5):
        next_date = reminder_system.calculate_next_billing_date(start_date, "weekly", i)
        print(f"  第{i}次续费: {next_date.strftime('%Y-%m-%d')}")


def test_days_until_renewal():
    """测试剩余天数计算"""
    print("\n" + "=" * 60)
    print("测试剩余天数计算")
    print("=" * 60 + "\n")

    now = datetime.now()

    test_dates = [
        ("过期7天", now - timedelta(days=7)),
        ("过期1天", now - timedelta(days=1)),
        ("今天到期", now),
        ("明天到期", now + timedelta(days=1)),
        ("3天后到期", now + timedelta(days=3)),
        ("7天后到期", now + timedelta(days=7)),
        ("30天后到期", now + timedelta(days=30))
    ]

    for desc, date in test_dates:
        days = reminder_system.calculate_days_until_renewal(date)
        print(f"{desc}: {days}天 ({date.strftime('%Y-%m-%d')})")


def test_reminder_generation():
    """测试提醒生成"""
    print("\n" + "=" * 60)
    print("测试提醒生成")
    print("=" * 60 + "\n")

    now = datetime.now()

    # 创建测试订阅数据
    test_subscriptions = [
        {
            "id": "test1",
            "service_name": "Netflix",
            "price": 15.99,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "status": "active",
            "start_date": (now - timedelta(days=30)).isoformat(),
            "created_at": (now - timedelta(days=30)).isoformat()
        },
        {
            "id": "test2",
            "service_name": "Spotify",
            "price": 9.99,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "status": "active",
            "start_date": (now - timedelta(days=27)).isoformat(),
            "created_at": (now - timedelta(days=27)).isoformat()
        },
        {
            "id": "test3",
            "service_name": "ChatGPT Plus",
            "price": 140.0,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "status": "active",
            "start_date": (now - timedelta(days=29)).isoformat(),
            "created_at": (now - timedelta(days=29)).isoformat()
        }
    ]

    # 生成提醒
    reminders = reminder_system.generate_reminders(test_subscriptions, [7, 3, 1, 0])

    print(f"生成了 {len(reminders)} 个提醒:\n")

    for reminder in reminders:
        print(f"服务: {reminder['service_name']}")
        print(f"  优先级: {reminder['priority']}")
        print(f"  剩余天数: {reminder['days_until_renewal']}")
        print(f"  金额: {reminder['currency']}{reminder['amount']:.2f}")
        print(f"  消息: {reminder['message']}")
        print()


def test_upcoming_renewals():
    """测试即将续费的订阅"""
    print("=" * 60)
    print("测试即将续费的订阅列表")
    print("=" * 60 + "\n")

    now = datetime.now()

    test_subscriptions = [
        {
            "id": "test1",
            "service_name": "服务A",
            "price": 10.0,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "status": "active",
            "start_date": (now - timedelta(days=25)).isoformat()
        },
        {
            "id": "test2",
            "service_name": "服务B",
            "price": 20.0,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "status": "active",
            "start_date": (now - timedelta(days=15)).isoformat()
        },
        {
            "id": "test3",
            "service_name": "服务C",
            "price": 30.0,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "status": "active",
            "start_date": (now - timedelta(days=60)).isoformat()
        }
    ]

    upcoming = reminder_system.get_upcoming_renewals(test_subscriptions, days_ahead=30)

    print(f"未来30天内将续费 {len(upcoming)} 个订阅:\n")

    for sub in upcoming:
        print(f"{sub['service_name']}:")
        print(f"  剩余天数: {sub['days_until_renewal']}")
        print(f"  下次续费: {sub['next_billing_date']}")
        print(f"  金额: {sub['currency']}{sub['price']:.2f}")
        print()


def test_statistics():
    """测试统计功能"""
    print("=" * 60)
    print("测试提醒统计")
    print("=" * 60 + "\n")

    now = datetime.now()

    test_subscriptions = [
        {
            "id": f"test{i}",
            "service_name": f"服务{i}",
            "price": 10.0 + i * 5,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "status": "active",
            "start_date": (now - timedelta(days=30 - i)).isoformat()
        }
        for i in range(10)
    ]

    stats = reminder_system.get_reminder_statistics(test_subscriptions)

    print("统计结果:")
    print(f"  总提醒数: {stats['total_reminders']}")
    print(f"  今日到期: {stats['due_today']}")
    print(f"  3天内: {stats['upcoming_3days']}")
    print(f"  7天内: {stats['upcoming_7days']}")
    print(f"  已逾期: {stats['overdue']}")
    print(f"  预计支出: ¥{stats['total_amount_due']:.2f}")
    print("\n按优先级分布:")
    for priority, count in stats['by_priority'].items():
        print(f"  {priority}: {count}")


if __name__ == "__main__":
    print("\n[Reminder System Test]\n")

    try:
        test_billing_date_calculation()
        test_days_until_renewal()
        test_reminder_generation()
        test_upcoming_renewals()
        test_statistics()

        print("\n" + "=" * 60)
        print("[SUCCESS] All tests completed!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()