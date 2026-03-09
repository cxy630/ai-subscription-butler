"""
订阅模板 - 常见订阅服务的预设模板
"""

from typing import Dict, List, Any

# 订阅服务模板
SUBSCRIPTION_TEMPLATES = {
    # 娱乐类
    "Netflix": {
        "service_name": "Netflix",
        "category": "entertainment",
        "price": 15.99,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "全球领先的流媒体平台",
        "icon": "🎬"
    },
    "Disney+": {
        "service_name": "Disney+",
        "category": "entertainment",
        "price": 28.0,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "迪士尼流媒体服务",
        "icon": "🏰"
    },
    "Spotify": {
        "service_name": "Spotify",
        "category": "entertainment",
        "price": 9.99,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "音乐流媒体服务",
        "icon": "🎵"
    },
    "Apple Music": {
        "service_name": "Apple Music",
        "category": "entertainment",
        "price": 10.0,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "苹果音乐服务",
        "icon": "🎧"
    },
    "YouTube Premium": {
        "service_name": "YouTube Premium",
        "category": "entertainment",
        "price": 11.99,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "YouTube无广告会员",
        "icon": "📺"
    },
    "腾讯视频": {
        "service_name": "腾讯视频",
        "category": "entertainment",
        "price": 30.0,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "腾讯视频VIP会员",
        "icon": "📺"
    },
    "爱奇艺": {
        "service_name": "爱奇艺",
        "category": "entertainment",
        "price": 25.0,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "爱奇艺VIP会员",
        "icon": "🎬"
    },
    "优酷": {
        "service_name": "优酷",
        "category": "entertainment",
        "price": 25.0,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "优酷VIP会员",
        "icon": "📺"
    },
    "哔哩哔哩": {
        "service_name": "哔哩哔哩",
        "category": "entertainment",
        "price": 25.0,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "B站大会员",
        "icon": "📺"
    },
    "网易云音乐": {
        "service_name": "网易云音乐",
        "category": "entertainment",
        "price": 8.0,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "网易云音乐黑胶VIP",
        "icon": "🎵"
    },
    "QQ音乐": {
        "service_name": "QQ音乐",
        "category": "entertainment",
        "price": 8.0,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "QQ音乐绿钻会员",
        "icon": "🎵"
    },

    # 生产力工具
    "ChatGPT Plus": {
        "service_name": "ChatGPT Plus",
        "category": "productivity",
        "price": 140.0,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "OpenAI聊天机器人高级版",
        "icon": "🤖"
    },
    "Claude Pro": {
        "service_name": "Claude Pro",
        "category": "productivity",
        "price": 20.0,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "Anthropic AI助手专业版",
        "icon": "🤖"
    },
    "GitHub Copilot": {
        "service_name": "GitHub Copilot",
        "category": "productivity",
        "price": 10.0,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "AI代码助手",
        "icon": "💻"
    },
    "Microsoft 365": {
        "service_name": "Microsoft 365",
        "category": "productivity",
        "price": 398.0,
        "currency": "CNY",
        "billing_cycle": "yearly",
        "description": "微软办公套件",
        "icon": "📝"
    },
    "Notion": {
        "service_name": "Notion",
        "category": "productivity",
        "price": 8.0,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "协作笔记和知识管理",
        "icon": "📔"
    },
    "Evernote": {
        "service_name": "Evernote",
        "category": "productivity",
        "price": 7.99,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "笔记软件",
        "icon": "📝"
    },
    "Grammarly": {
        "service_name": "Grammarly",
        "category": "productivity",
        "price": 12.0,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "英文写作助手",
        "icon": "✍️"
    },
    "Canva Pro": {
        "service_name": "Canva Pro",
        "category": "productivity",
        "price": 9.99,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "在线设计工具",
        "icon": "🎨"
    },

    # 存储服务
    "iCloud+": {
        "service_name": "iCloud+",
        "category": "storage",
        "price": 21.0,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "苹果云存储服务",
        "icon": "☁️"
    },
    "Google One": {
        "service_name": "Google One",
        "category": "storage",
        "price": 1.99,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "Google云存储",
        "icon": "☁️"
    },
    "Dropbox": {
        "service_name": "Dropbox",
        "category": "storage",
        "price": 11.99,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "云存储服务",
        "icon": "📦"
    },
    "百度网盘": {
        "service_name": "百度网盘",
        "category": "storage",
        "price": 8.8,
        "currency": "CNY",
        "billing_cycle": "yearly",
        "description": "百度云存储",
        "icon": "☁️"
    },
    "阿里云盘": {
        "service_name": "阿里云盘",
        "category": "storage",
        "price": 9.0,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "阿里云存储服务",
        "icon": "☁️"
    },
    "夸克网盘": {
        "service_name": "夸克网盘",
        "category": "storage",
        "price": 19.9,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "夸克云存储",
        "icon": "☁️"
    },

    # 教育类
    "Coursera Plus": {
        "service_name": "Coursera Plus",
        "category": "education",
        "price": 399.0,
        "currency": "CNY",
        "billing_cycle": "yearly",
        "description": "在线课程平台",
        "icon": "📚"
    },
    "Udemy Pro": {
        "service_name": "Udemy Pro",
        "category": "education",
        "price": 16.99,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "在线学习平台",
        "icon": "📚"
    },
    "Duolingo Plus": {
        "service_name": "Duolingo Plus",
        "category": "education",
        "price": 6.99,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "语言学习应用",
        "icon": "🦉"
    },
    "得到": {
        "service_name": "得到",
        "category": "education",
        "price": 365.0,
        "currency": "CNY",
        "billing_cycle": "yearly",
        "description": "知识服务应用",
        "icon": "📚"
    },

    # 健康健身
    "Peloton": {
        "service_name": "Peloton",
        "category": "health_fitness",
        "price": 12.99,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "健身课程平台",
        "icon": "🚴"
    },
    "Keep": {
        "service_name": "Keep",
        "category": "health_fitness",
        "price": 15.0,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "description": "运动健身应用",
        "icon": "💪"
    },
    "MyFitnessPal": {
        "service_name": "MyFitnessPal",
        "category": "health_fitness",
        "price": 9.99,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "健康追踪应用",
        "icon": "🏃"
    },

    # 商务工具
    "LinkedIn Premium": {
        "service_name": "LinkedIn Premium",
        "category": "business",
        "price": 29.99,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "职场社交网络高级版",
        "icon": "💼"
    },
    "Zoom Pro": {
        "service_name": "Zoom Pro",
        "category": "business",
        "price": 14.99,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "视频会议服务",
        "icon": "📹"
    },
    "Slack": {
        "service_name": "Slack",
        "category": "business",
        "price": 6.67,
        "currency": "USD",
        "billing_cycle": "monthly",
        "description": "团队协作工具",
        "icon": "💬"
    },
}


def get_all_templates() -> Dict[str, Dict[str, Any]]:
    """获取所有订阅模板"""
    return SUBSCRIPTION_TEMPLATES


def get_templates_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """根据分类获取模板"""
    return {
        name: template
        for name, template in SUBSCRIPTION_TEMPLATES.items()
        if template.get("category") == category
    }


def get_template(service_name: str) -> Dict[str, Any]:
    """获取指定服务的模板"""
    return SUBSCRIPTION_TEMPLATES.get(service_name, None)


def search_templates(query: str) -> Dict[str, Dict[str, Any]]:
    """搜索模板"""
    query_lower = query.lower()
    return {
        name: template
        for name, template in SUBSCRIPTION_TEMPLATES.items()
        if query_lower in name.lower() or query_lower in template.get("description", "").lower()
    }


def get_template_categories() -> List[str]:
    """获取所有模板分类"""
    categories = set()
    for template in SUBSCRIPTION_TEMPLATES.values():
        categories.add(template.get("category", "other"))
    return sorted(list(categories))


def create_subscription_from_template(template_name: str, custom_overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """从模板创建订阅数据"""
    template = get_template(template_name)
    if not template:
        return None

    # 复制模板数据（排除icon和description）
    subscription_data = {
        "service_name": template["service_name"],
        "price": template["price"],
        "currency": template["currency"],
        "billing_cycle": template["billing_cycle"],
        "category": template["category"],
        "status": "active"
    }

    # 应用自定义覆盖
    if custom_overrides:
        subscription_data.update(custom_overrides)

    return subscription_data


if __name__ == "__main__":
    # 测试模板功能
    print("订阅模板测试")
    print(f"总模板数: {len(SUBSCRIPTION_TEMPLATES)}")
    print(f"\n分类: {get_template_categories()}")

    print("\n娱乐类模板:")
    entertainment = get_templates_by_category("entertainment")
    for name, template in list(entertainment.items())[:3]:
        print(f"  {template['icon']} {name}: ¥{template['price']}/{template['billing_cycle']}")

    print("\n搜索'音乐':")
    music = search_templates("音乐")
    for name, template in music.items():
        print(f"  {template['icon']} {name}: {template['description']}")