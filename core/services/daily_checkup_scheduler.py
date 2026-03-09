"""
每日检查调度器 - 定期运行AI管家的每日检查任务
"""

import asyncio
import schedule
import time
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from core.agents.butler_agent import ButlerAgent
from core.agents.base_agent import AgentContext
from core.database.data_interface import data_manager

logger = logging.getLogger(__name__)


class DailyCheckupScheduler:
    """每日检查调度器"""

    def __init__(self):
        self.butler_agent = ButlerAgent()
        self.is_running = False
        self.last_run_time: Optional[datetime] = None
        self.last_weekly_run_time: Optional[datetime] = None
        self.last_results: Dict[str, Any] = {}
        self.last_weekly_results: Dict[str, Any] = {}

    async def run_daily_checkup_for_user(self, user_id: str) -> Dict[str, Any]:
        """为指定用户运行每日检查"""
        try:
            # 获取用户数据
            user = data_manager.get_user_by_id(user_id)
            if not user:
                return {
                    "status": "error",
                    "error": f"User {user_id} not found"
                }

            # 获取用户的活跃订阅
            subscriptions = data_manager.get_active_subscriptions(user_id)

            # 创建Agent上下文
            automation_prefs = user.get("automation_preferences", {})
            logger.info(f"--- [DEBUG] AgentContext fields: {AgentContext.__dataclass_fields__.keys() if hasattr(AgentContext, '__dataclass_fields__') else 'Not a dataclass'}")
            context = AgentContext(
                user_id=user_id,
                user_preferences=automation_prefs,
                subscriptions=subscriptions,
                current_time=datetime.now()
            )

            # 执行每日检查任务
            task = {
                "type": "daily_checkup",
                "user_id": user_id
            }

            result = await self.butler_agent.execute_task(task, context)

            # 记录结果
            self.last_run_time = datetime.now()
            self.last_results[user_id] = {
                "timestamp": self.last_run_time.isoformat(),
                "result": result
            }

            logger.info(f"Daily checkup completed for user {user_id}: {result.get('status')}")
            return result

        except Exception as e:
            logger.error(f"Error running daily checkup for user {user_id}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def run_daily_checkup_for_all_users(self):
        """为所有用户运行每日检查"""
        try:
            # 获取所有用户
            users = data_manager.get_all_users()

            logger.info(f"Running daily checkup for {len(users)} users")

            results = {}
            for user in users:
                user_id = user.get("id")
                if user_id:
                    # 检查用户是否启用了自动检查
                    automation_prefs = user.get("automation_preferences", {})
                    if automation_prefs.get("enable_auto_checkup", True):
                        result = await self.run_daily_checkup_for_user(user_id)
                        results[user_id] = result
                    else:
                        logger.info(f"User {user_id} has disabled auto checkup")

            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "users_processed": len(results),
                "results": results
            }

        except Exception as e:
            logger.error(f"Error running daily checkup for all users: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def run_weekly_report_for_user(self, user_id: str) -> Dict[str, Any]:
        """为指定用户运行周报生成"""
        try:
            user = data_manager.get_user_by_id(user_id)
            if not user: return {"status": "error", "error": f"User {user_id} not found"}
            
            subscriptions = data_manager.get_active_subscriptions(user_id)
            automation_prefs = user.get("automation_preferences", {})
            context = AgentContext(
                user_id=user_id,
                subscriptions=subscriptions,
                user_preferences=user.get("notification_preferences", {}),
                automation_level=automation_prefs.get("automation_level", "manual")
            )

            task = {"type": "generate_weekly_report", "user_id": user_id}
            result = await self.butler_agent.execute_task(task, context)

            self.last_weekly_run_time = datetime.now()
            self.last_weekly_results[user_id] = {
                "timestamp": self.last_weekly_run_time.isoformat(),
                "result": result
            }
            return result
        except Exception as e:
            logger.error(f"Error running weekly report for user {user_id}: {e}")
            return {"status": "error", "error": str(e)}

    async def run_weekly_report_for_all_users(self):
        """为所有开启自动检查的用户运行周报"""
        try:
            users = data_manager.get_all_users()
            results = {}
            for user in users:
                user_id = user.get("id")
                if user_id and user.get("automation_preferences", {}).get("enable_auto_checkup", True):
                    results[user_id] = await self.run_weekly_report_for_user(user_id)
            return {"status": "success", "users_processed": len(results), "results": results}
        except Exception as e:
            logger.error(f"Error running weekly reports: {e}")
            return {"status": "error", "error": str(e)}

    def schedule_daily_checkup(self, time_str: str = "09:00"):
        """
        调度每日检查任务

        Args:
            time_str: 执行时间，格式为 "HH:MM" (24小时制)
        """
        def job():
            """调度任务的包装函数"""
            logger.info(f"Starting scheduled daily checkup at {datetime.now()}")
            asyncio.run(self.run_daily_checkup_for_all_users())

        def weekly_job():
            """周报展示任务的包装函数"""
            logger.info(f"Starting scheduled weekly report at {datetime.now()}")
            asyncio.run(self.run_weekly_report_for_all_users())

        # 清除现有调度
        schedule.clear()

        # 添加新的调度
        schedule.every().day.at(time_str).do(job)
        # 固定每周一运行周报
        schedule.every().monday.at(time_str).do(weekly_job)

        logger.info(f"Daily checkup and Weekly report scheduled at {time_str}")

    def start_scheduler(self, time_str: str = "09:00"):
        """
        启动调度器

        Args:
            time_str: 执行时间，格式为 "HH:MM"
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        self.schedule_daily_checkup(time_str)
        self.is_running = True

        logger.info("Scheduler started")

        # 运行调度循环
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

    def stop_scheduler(self):
        """停止调度器"""
        self.is_running = False
        schedule.clear()
        logger.info("Scheduler stopped")

    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        next_run = schedule.next_run()

        return {
            "is_running": self.is_running,
            "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
            "last_weekly_run_time": self.last_weekly_run_time.isoformat() if self.last_weekly_run_time else None,
            "next_run_time": next_run.isoformat() if next_run else None,
            "scheduled_jobs": len(schedule.jobs),
            "last_results_count": len(self.last_results)
        }

    def get_last_results(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取最近的检查结果

        Args:
            user_id: 用户ID，如果为None则返回所有用户的结果
        """
        if user_id:
            return self.last_results.get(user_id, {})
        return self.last_results


# 全局调度器实例
daily_checkup_scheduler = DailyCheckupScheduler()
