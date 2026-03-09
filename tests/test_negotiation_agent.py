"""
NegotiationAgent 验证测试脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.agents.negotiation_agent import NegotiationAgent
from core.agents.base_agent import AgentContext

async def verify_negotiation_agent():
    print("开始验证 NegotiationAgent...")
    
    # 模拟上下文
    context = AgentContext(
        user_id="test_user",
        subscriptions=[{
            "id": "sub_1",
            "service_name": "Netflix",
            "price": 100.0,
            "currency": "CNY",
            "status": "active"
        }],
        user_preferences={},
        automation_level="manual"
    )
    
    agent = NegotiationAgent()
    
    # 1. 测试策略生成
    print("\n--- 测试 1: 生成谈判策略 ---")
    strategy_result = await agent.execute_task({
        "type": "generate_strategy",
        "subscription_id": "sub_1"
    }, context)
    
    if strategy_result.get("status") == "success":
        print("✅ 策略生成成功!")
        print(f"策略内容预览: {strategy_result.get('strategy_text')[:100]}...")
    else:
        print(f"❌ 策略生成失败: {strategy_result.get('message')}")
        return

    # 2. 测试消息起草
    print("\n--- 测试 2: 起草联系消息 ---")
    draft_result = await agent.execute_task({
        "type": "draft_message",
        "strategy": strategy_result.get("strategy_text")
    }, context)
    
    if draft_result.get("status") == "success":
        print("✅ 消息起草成功!")
        print(f"初稿预览: {draft_result.get('draft_text')[:100]}...")
    else:
        print(f"❌ 消息起草失败: {draft_result.get('message')}")

if __name__ == "__main__":
    asyncio.run(verify_negotiation_agent())
