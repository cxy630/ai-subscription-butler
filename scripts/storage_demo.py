"""
Storage Solutions Demo - English Version
Demonstrates JSON storage functionality without dependencies
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

def create_demo_data():
    """Create demo data to test storage"""

    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    print("AI Subscription Butler - Storage Demo")
    print("=" * 50)

    # Test user data
    user_data = {
        "id": str(uuid.uuid4()),
        "email": "demo@example.com",
        "name": "Demo User",
        "created_at": datetime.now().isoformat(),
        "subscription_tier": "free"
    }

    # Test subscriptions
    subscriptions = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_data["id"],
            "service_name": "Netflix",
            "price": 15.99,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "entertainment",
            "status": "active"
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_data["id"],
            "service_name": "ChatGPT Plus",
            "price": 140.0,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "productivity",
            "status": "active"
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_data["id"],
            "service_name": "Spotify",
            "price": 9.99,
            "currency": "CNY",
            "billing_cycle": "monthly",
            "category": "entertainment",
            "status": "active"
        }
    ]

    # Save to JSON files
    print("\n1. Creating user data...")
    with open(data_dir / "users.json", "w", encoding="utf-8") as f:
        json.dump([user_data], f, indent=2, ensure_ascii=False)
    print(f"   User created: {user_data['name']} ({user_data['email']})")

    print("\n2. Creating subscriptions...")
    with open(data_dir / "subscriptions.json", "w", encoding="utf-8") as f:
        json.dump(subscriptions, f, indent=2, ensure_ascii=False)

    for sub in subscriptions:
        print(f"   + {sub['service_name']}: CNY{sub['price']}/{sub['billing_cycle']}")

    # Calculate analytics
    print("\n3. Analytics:")
    total_subscriptions = len(subscriptions)
    monthly_spending = sum(sub["price"] for sub in subscriptions)

    # Category breakdown
    categories = {}
    for sub in subscriptions:
        cat = sub["category"]
        if cat not in categories:
            categories[cat] = {"count": 0, "spending": 0}
        categories[cat]["count"] += 1
        categories[cat]["spending"] += sub["price"]

    print(f"   Total subscriptions: {total_subscriptions}")
    print(f"   Monthly spending: CNY{monthly_spending}")
    print(f"   Categories:")
    for cat, stats in categories.items():
        print(f"     {cat}: {stats['count']} services, CNY{stats['spending']}")

    return {
        "user": user_data,
        "subscriptions": subscriptions,
        "total_spending": monthly_spending,
        "categories": len(categories)
    }

def show_storage_options():
    """Show different storage options available"""

    print("\n" + "=" * 50)
    print("STORAGE OPTIONS COMPARISON")
    print("=" * 50)

    options = [
        {
            "name": "JSON Files",
            "pros": [
                "No database server required",
                "Human readable format",
                "Easy to backup and move",
                "Perfect for development"
            ],
            "cons": [
                "Limited query capabilities",
                "No concurrent access control",
                "Performance issues with large data"
            ],
            "use_case": "Development & Prototyping"
        },
        {
            "name": "SQLite",
            "pros": [
                "SQL query support",
                "ACID transactions",
                "Better performance",
                "Single file database"
            ],
            "cons": [
                "Limited concurrent writes",
                "Not suitable for large scale",
                "Requires SQLite knowledge"
            ],
            "use_case": "Small to Medium Applications"
        },
        {
            "name": "PostgreSQL",
            "pros": [
                "Full featured database",
                "Excellent concurrency",
                "Rich data types",
                "Production ready"
            ],
            "cons": [
                "Requires server installation",
                "More complex deployment",
                "Higher resource usage"
            ],
            "use_case": "Production Applications"
        }
    ]

    for option in options:
        print(f"\n{option['name']}:")
        print(f"  Use Case: {option['use_case']}")
        print("  Pros:")
        for pro in option['pros']:
            print(f"    + {pro}")
        print("  Cons:")
        for con in option['cons']:
            print(f"    - {con}")

def main():
    """Main demo function"""
    try:
        # Create demo data
        results = create_demo_data()

        # Show storage options
        show_storage_options()

        print(f"\n" + "=" * 50)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Created demo with:")
        print(f"  User: {results['user']['name']}")
        print(f"  Subscriptions: {len(results['subscriptions'])}")
        print(f"  Monthly cost: CNY{results['total_spending']}")
        print(f"  Categories: {results['categories']}")
        print(f"\nData files saved in: ./data/")
        print(f"  - users.json")
        print(f"  - subscriptions.json")

        print(f"\nRecommendation: Start with JSON storage for development!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()