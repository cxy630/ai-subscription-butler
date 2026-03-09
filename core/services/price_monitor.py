import json
import os
from datetime import datetime
from typing import Dict, Any, List

# A simple JSON based file for storing historical prices
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "price_history.json")

class PriceMonitor:
    """价格监控服务 - 记录订阅价格历史并检测涨价"""
    
    def __init__(self):
        self._ensure_history_file()

    def _ensure_history_file(self):
        """确保历史数据文件存在"""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load_history(self) -> Dict[str, Any]:
        """加载价格历史数据"""
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_history(self, data: Dict[str, Any]):
        """保存历史数据"""
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def record_prices(self, user_id: str, subscriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        记录当前订阅价格并返回所有发生涨价的订阅
        """
        history = self._load_history()
        user_history = history.get(user_id, {})
        
        price_increases = []
        today = datetime.now().date().isoformat()
        
        for sub in subscriptions:
            if sub.get("status") != "active":
                continue
                
            service_name = sub.get("service_name")
            current_price = sub.get("price", 0)
            sub_id = sub.get("id")
            
            if not service_name or current_price <= 0:
                continue
                
            # 获取该服务历史记录
            service_records = user_history.get(sub_id, [])
            
            if not service_records:
                service_records.append({
                    "date": today,
                    "price": current_price
                })
            else:
                last_record = service_records[-1]
                last_price = last_record["price"]
                
                # 若价格上涨
                if current_price > last_price:
                    price_increases.append({
                        "subscription_id": sub_id,
                        "service_name": service_name,
                        "old_price": last_price,
                        "new_price": current_price,
                        "increase_amount": current_price - last_price,
                        "increase_percentage": (current_price - last_price) / last_price
                    })
                    
                    # 避免同一天重复记录
                    if last_record["date"] == today:
                        last_record["price"] = current_price
                    else:
                        service_records.append({
                            "date": today,
                            "price": current_price
                        })
            
            user_history[sub_id] = service_records
        
        history[user_id] = user_history
        self._save_history(history)
        
        return price_increases

price_monitor = PriceMonitor()
