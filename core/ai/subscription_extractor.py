"""
订阅信息提取器 - 从用户对话中提取订阅信息
"""

import re
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


class SubscriptionExtractor:
    """从用户消息中提取订阅信息"""

    def __init__(self):
        # 服务名称模式
        self.service_patterns = {
            # 流媒体
            'Netflix': ['netflix', '奈飞', 'n飞'],
            'ChatGPT': ['chatgpt', 'chat gpt', 'gpt'],
            'Claude': ['claude', 'claude pro', 'anthropic'],
            '爱奇艺': ['爱奇艺', 'iqiyi'],
            '腾讯视频': ['腾讯视频', 'tencent video'],
            'Spotify': ['spotify', 'spotify premium'],
            'YouTube': ['youtube', 'youtube premium', 'yt'],
            'Apple Music': ['apple music', '苹果音乐'],
            'QQ音乐': ['qq音乐', 'qq music'],
            '网易云音乐': ['网易云', '网易云音乐'],

            # 生产力
            'Office 365': ['office', 'office 365', 'microsoft 365', 'o365'],
            'Adobe': ['adobe', 'creative cloud', 'photoshop'],
            'Notion': ['notion'],
            'GitHub': ['github', 'github pro', 'github copilot'],

            # 云存储
            '百度网盘': ['百度网盘', '百度云'],
            '阿里云盘': ['阿里云盘', 'aliyun drive'],
            'iCloud': ['icloud', 'icloud+'],
            'Dropbox': ['dropbox'],
            '夸克网盘': ['夸克', '夸克网盘'],
        }

        # 分类映射
        self.category_keywords = {
            'entertainment': ['视频', '音乐', '娱乐', '电影', '电视'],
            'productivity': ['办公', '生产力', '工作', '效率', 'ai'],
            'storage': ['网盘', '存储', '云盘', 'cloud'],
            'education': ['教育', '学习', '课程'],
            'health_fitness': ['健身', '健康', '运动'],
        }

    def extract_subscription_info(self, user_message: str, ai_response: str = "") -> Optional[Dict[str, Any]]:
        """
        从用户消息和AI响应中提取订阅信息

        Args:
            user_message: 用户输入的消息
            ai_response: AI的响应（可能包含结构化数据）

        Returns:
            提取的订阅信息字典，如果未识别到订阅添加意图则返回None
        """
        # 检查是否是添加订阅意图
        if not self._is_add_subscription_intent(user_message):
            return None

        # 尝试从AI响应中提取结构化数据
        extracted_from_ai = self._extract_from_ai_response(ai_response)
        if extracted_from_ai:
            return extracted_from_ai

        # 从用户消息中提取
        return self._extract_from_user_message(user_message)

    def _is_add_subscription_intent(self, message: str) -> bool:
        """检查是否是添加订阅的意图"""
        add_keywords = [
            '添加', '新增', '订阅', '加个', '帮我加', '我要订',
            '买了', '购买', '入手', '剁手', '开通', '办了',
            '续费', '充值', '付费', '订了', '下单', '入了'
        ]
        message_lower = message.lower()

        return any(keyword in message_lower for keyword in add_keywords)

    def _extract_from_ai_response(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """从AI响应中提取结构化数据"""
        try:
            # 查找JSON代码块
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            match = re.search(json_pattern, ai_response, re.DOTALL)

            if match:
                json_str = match.group(1)
                data = json.loads(json_str)

                # 验证必需字段
                if 'service_name' in data and 'price' in data:
                    return self._normalize_subscription_data(data)

            # 尝试直接查找JSON对象
            if '{' in ai_response and '}' in ai_response:
                start = ai_response.find('{')
                end = ai_response.rfind('}') + 1
                json_str = ai_response[start:end]

                data = json.loads(json_str)
                if 'service_name' in data and 'price' in data:
                    return self._normalize_subscription_data(data)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            pass

        return None

    def _extract_from_user_message(self, message: str) -> Dict[str, Any]:
        """从用户消息中提取订阅信息"""
        result = {
            'service_name': '',
            'price': 0.0,
            'currency': 'CNY',
            'billing_cycle': 'monthly',
            'category': 'other',
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'payment_method': '未知',
            'notes': f'通过AI助手添加于{datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'status': 'active'
        }

        # 提取服务名
        result['service_name'] = self._extract_service_name(message)

        # 提取价格
        result['price'] = self._extract_price(message)

        # 提取币种
        result['currency'] = self._extract_currency(message)

        # 提取周期
        result['billing_cycle'] = self._extract_billing_cycle(message)

        # 提取订阅日期
        result['start_date'] = self._extract_start_date(message)

        # 推断分类
        result['category'] = self._infer_category(result['service_name'], message)

        return result

    def _extract_service_name(self, message: str) -> str:
        """提取服务名称"""
        # 尝试匹配已知服务
        message_lower = message.lower()

        for service_name, patterns in self.service_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return service_name

        # 使用正则提取可能的服务名
        # 匹配引号中的内容
        quoted = re.findall(r'["""\'](.*?)["""\']', message)
        if quoted:
            return quoted[0]

        # 匹配"添加XX订阅"模式
        add_pattern = r'添加\s*([^\s，。,]+)\s*订阅'
        match = re.search(add_pattern, message)
        if match:
            return match.group(1)

        # 匹配"XX每月"模式
        monthly_pattern = r'([^\s，。,]+)\s*每[月年周]'
        match = re.search(monthly_pattern, message)
        if match:
            return match.group(1)

        return '未知服务'

    def _extract_price(self, message: str) -> float:
        """提取价格"""
        # 多种价格模式
        patterns = [
            r'(\d+\.?\d*)\s*元',
            r'¥\s*(\d+\.?\d*)',
            r'\$\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*块',
            r'(\d+\.?\d*)\s*CNY',
            r'(\d+\.?\d*)\s*USD',
            r'每[月年周]\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*每[月年周]',
        ]

        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue

        return 0.0

    def _extract_currency(self, message: str) -> str:
        """提取币种"""
        if any(keyword in message for keyword in ['美元', '$', 'USD', 'usd']):
            return 'USD'
        elif any(keyword in message for keyword in ['欧元', '€', 'EUR', 'eur']):
            return 'EUR'
        else:
            return 'CNY'  # 默认人民币

    def _extract_billing_cycle(self, message: str) -> str:
        """提取计费周期"""
        if any(keyword in message for keyword in ['每年', '年付', '年费', '年订', '每年', '/年', '一年']):
            return 'yearly'
        elif any(keyword in message for keyword in ['每周', '周付', '每周', '/周']):
            return 'weekly'
        elif any(keyword in message for keyword in ['每天', '日付', '每日', '/天']):
            return 'daily'
        else:
            return 'monthly'  # 默认每月

    def _extract_start_date(self, message: str) -> str:
        """
        从用户消息中提取订阅开始日期
        支持多种自然语言表达方式

        Returns:
            日期字符串 (YYYY-MM-DD格式)，如果未提及则返回今天
        """
        from datetime import timedelta
        import calendar

        today = datetime.now()
        message_lower = message.lower()

        # 1. 识别具体日期格式
        # YYYY-MM-DD 或 YYYY/MM/DD
        date_patterns = [
            r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})',  # 2024-01-15, 2024年1月15日
            r'(\d{1,2})[-/月](\d{1,2})[-/日]',         # 1-15, 1月15日 (当年)
        ]

        for pattern in date_patterns:
            match = re.search(pattern, message)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 3:  # 包含年份
                        year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                    else:  # 只有月日
                        year = today.year
                        month, day = int(groups[0]), int(groups[1])

                    # 验证日期有效性
                    parsed_date = datetime(year, month, day)
                    return parsed_date.strftime('%Y-%m-%d')
                except (ValueError, IndexError):
                    pass

        # 2. 相对日期表达
        # "今天"、"今日"
        if any(keyword in message_lower for keyword in ['今天', '今日', '现在']):
            return today.strftime('%Y-%m-%d')

        # "昨天"
        if '昨天' in message_lower:
            yesterday = today - timedelta(days=1)
            return yesterday.strftime('%Y-%m-%d')

        # "前天"
        if '前天' in message_lower:
            day_before = today - timedelta(days=2)
            return day_before.strftime('%Y-%m-%d')

        # "明天"
        if '明天' in message_lower:
            tomorrow = today + timedelta(days=1)
            return tomorrow.strftime('%Y-%m-%d')

        # "X天前" 或 "X天后"
        days_ago_pattern = r'(\d+)\s*天前'
        match = re.search(days_ago_pattern, message_lower)
        if match:
            days = int(match.group(1))
            past_date = today - timedelta(days=days)
            return past_date.strftime('%Y-%m-%d')

        days_later_pattern = r'(\d+)\s*天后'
        match = re.search(days_later_pattern, message_lower)
        if match:
            days = int(match.group(1))
            future_date = today + timedelta(days=days)
            return future_date.strftime('%Y-%m-%d')

        # "上周"、"上星期"
        if any(keyword in message_lower for keyword in ['上周', '上星期', '上个星期']):
            last_week = today - timedelta(weeks=1)
            return last_week.strftime('%Y-%m-%d')

        # "上个月"、"上月"
        if any(keyword in message_lower for keyword in ['上个月', '上月']):
            if today.month == 1:
                last_month_date = datetime(today.year - 1, 12, today.day)
            else:
                # 处理月末日期（如1月31日变成2月28/29日）
                last_month = today.month - 1
                last_month_year = today.year
                last_day_of_last_month = calendar.monthrange(last_month_year, last_month)[1]
                day = min(today.day, last_day_of_last_month)
                last_month_date = datetime(last_month_year, last_month, day)
            return last_month_date.strftime('%Y-%m-%d')

        # "本月X号"、"这个月X号"
        this_month_pattern = r'[本这]个?月\s*(\d{1,2})\s*[号日]'
        match = re.search(this_month_pattern, message)
        if match:
            try:
                day = int(match.group(1))
                date = datetime(today.year, today.month, day)
                return date.strftime('%Y-%m-%d')
            except ValueError:
                pass

        # "X月X号"、"X月X日" (当年)
        month_day_pattern = r'(\d{1,2})\s*月\s*(\d{1,2})\s*[号日]'
        match = re.search(month_day_pattern, message)
        if match:
            try:
                month = int(match.group(1))
                day = int(match.group(2))
                date = datetime(today.year, month, day)
                return date.strftime('%Y-%m-%d')
            except ValueError:
                pass

        # "周一"到"周日"、"星期一"到"星期日" (本周)
        weekday_map = {
            '周一': 0, '星期一': 0, '礼拜一': 0,
            '周二': 1, '星期二': 1, '礼拜二': 1,
            '周三': 2, '星期三': 2, '礼拜三': 2,
            '周四': 3, '星期四': 3, '礼拜四': 3,
            '周五': 4, '星期五': 4, '礼拜五': 4,
            '周六': 5, '星期六': 5, '礼拜六': 5,
            '周日': 6, '星期日': 6, '礼拜日': 6, '周天': 6, '星期天': 6
        }

        for weekday_name, weekday_num in weekday_map.items():
            if weekday_name in message:
                # 计算本周该天的日期
                days_diff = weekday_num - today.weekday()
                if days_diff > 0:  # 如果是本周未来的日子，取上周
                    days_diff -= 7
                target_date = today + timedelta(days=days_diff)
                return target_date.strftime('%Y-%m-%d')

        # 3. 默认返回今天
        return today.strftime('%Y-%m-%d')

    def _infer_category(self, service_name: str, message: str) -> str:
        """推断服务分类"""
        combined_text = (service_name + ' ' + message).lower()

        # 基于关键词推断
        for category, keywords in self.category_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                return category

        # 基于服务名推断
        category_mappings = {
            'entertainment': ['netflix', '爱奇艺', 'spotify', 'youtube', 'music', '音乐', '视频'],
            'productivity': ['chatgpt', 'claude', 'office', 'adobe', 'notion', 'github'],
            'storage': ['网盘', 'cloud', 'dropbox', 'icloud', '云'],
            'education': ['课程', '学习', '教育'],
        }

        for category, keywords in category_mappings.items():
            if any(keyword in combined_text for keyword in keywords):
                return category

        return 'other'

    def _normalize_subscription_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """标准化订阅数据"""
        # 处理 billing_cycle 的多种表达方式
        billing_cycle = data.get('billing_cycle') or data.get('period', 'monthly')

        # 处理特殊的周期格式（如 "3 years" → "yearly"）
        if isinstance(billing_cycle, str):
            billing_cycle_lower = billing_cycle.lower()
            if 'year' in billing_cycle_lower:
                billing_cycle = 'yearly'
            elif 'month' in billing_cycle_lower:
                billing_cycle = 'monthly'
            elif 'week' in billing_cycle_lower:
                billing_cycle = 'weekly'
            elif 'day' in billing_cycle_lower:
                billing_cycle = 'daily'

        normalized = {
            'service_name': str(data.get('service_name', '未知服务')),
            'price': float(data.get('price', 0.0)),
            'currency': str(data.get('currency', 'CNY')),
            'billing_cycle': str(billing_cycle),
            'category': str(data.get('category', 'other')),
            'start_date': data.get('start_date', datetime.now().strftime('%Y-%m-%d')),
            'payment_method': data.get('payment_method', '未知'),
            'notes': data.get('notes', f'通过AI助手添加于{datetime.now().strftime("%Y-%m-%d %H:%M")}'),
            'status': data.get('status', 'active')
        }

        # 验证枚举值
        valid_cycles = ['monthly', 'yearly', 'weekly', 'daily']
        if normalized['billing_cycle'] not in valid_cycles:
            normalized['billing_cycle'] = 'monthly'

        valid_categories = ['entertainment', 'productivity', 'storage', 'education', 'health_fitness', 'business', 'other', 'health']
        if normalized['category'] not in valid_categories:
            normalized['category'] = 'other'

        return normalized


def check_duplicate_subscription(service_name: str, existing_subscriptions: list) -> Tuple[bool, Optional[Dict]]:
    """
    检查是否有重复订阅

    Args:
        service_name: 服务名称
        existing_subscriptions: 现有订阅列表

    Returns:
        (is_duplicate, existing_subscription) 元组
    """
    service_name_lower = service_name.lower().strip()

    for sub in existing_subscriptions:
        existing_name = sub.get('service_name', '').lower().strip()

        # 完全匹配
        if service_name_lower == existing_name:
            return True, sub

        # 模糊匹配（包含关系）
        if service_name_lower in existing_name or existing_name in service_name_lower:
            # 确保不是误匹配（长度差距不能太大）
            len_diff = abs(len(service_name_lower) - len(existing_name))
            if len_diff <= 3:
                return True, sub

    return False, None
