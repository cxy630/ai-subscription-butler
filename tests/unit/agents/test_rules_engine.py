import pytest
from datetime import datetime, timedelta
from core.agents.rules_engine import (
    RuleCondition, RuleConditionType, RuleAction, RuleActionType,
    AutomationRule, RuleExecutionMode, RulesEngine
)

def test_price_change_condition():
    condition = RuleCondition(RuleConditionType.PRICE_CHANGE, {"threshold": 0.05})
    
    # Needs historical_price in context
    sub = {"price": 105}
    ctx = {"historical_price": 100}
    assert condition.evaluate(sub, ctx) is False  # Exactly 5% change, threshold > 0.05
    
    sub_high = {"price": 110}
    assert condition.evaluate(sub_high, ctx) is True  # 10% change > 5%

def test_unused_period_condition():
    condition = RuleCondition(RuleConditionType.UNUSED_PERIOD, {"days": 30})
    
    sub = {}
    last_used = (datetime.now() - timedelta(days=35)).isoformat()
    ctx = {"last_used_date": last_used}
    assert condition.evaluate(sub, ctx) is True
    
    last_used_recent = (datetime.now() - timedelta(days=10)).isoformat()
    ctx_recent = {"last_used_date": last_used_recent}
    assert condition.evaluate(sub, ctx_recent) is False

def test_redundant_feature_condition():
    condition = RuleCondition(RuleConditionType.REDUNDANT_FEATURE, {})
    
    sub = {"category": "Entertainment"}
    ctx = {"category_Entertainment_active_count": 2}
    assert condition.evaluate(sub, ctx) is True
    
    ctx_single = {"category_Entertainment_active_count": 1}
    assert condition.evaluate(sub, ctx_single) is False

def test_annual_potential_condition():
    condition = RuleCondition(RuleConditionType.ANNUAL_POTENTIAL, {"months_threshold": 3})
    
    sub_monthly = {"billing_cycle": "monthly"}
    ctx = {"months_active": 4}
    assert condition.evaluate(sub_monthly, ctx) is True
    
    ctx_short = {"months_active": 2}
    assert condition.evaluate(sub_monthly, ctx_short) is False
    
    # Ignore yearly plans
    sub_yearly = {"billing_cycle": "yearly"}
    assert condition.evaluate(sub_yearly, ctx) is False

def test_rules_engine_evaluation():
    engine = RulesEngine()
    # Mock subscription that hasn't been used in 40 days
    sub = {
        "id": "sub_1",
        "service_name": "Netflix",
        "category": "Entertainment",
        "billing_cycle": "monthly",
        "price": 15
    }
    ctx = {
        "last_used_date": (datetime.now() - timedelta(days=40)).isoformat(),
        "historical_price": 15,
        "months_active": 1,
        "category_Entertainment_active_count": 1
    }
    
    triggered = engine.evaluate_subscription(sub, ctx)
    # Should trigger pause_unused rule
    triggered_ids = [r.rule_id for r in triggered]
    assert "pause_unused" in triggered_ids
    assert "price_increase_alert" not in triggered_ids
