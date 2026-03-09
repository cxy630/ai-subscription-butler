"""
订阅模板模块
"""

from .subscription_templates import (
    get_all_templates,
    get_templates_by_category,
    get_template,
    search_templates,
    get_template_categories,
    create_subscription_from_template,
    SUBSCRIPTION_TEMPLATES
)

__all__ = [
    'get_all_templates',
    'get_templates_by_category',
    'get_template',
    'search_templates',
    'get_template_categories',
    'create_subscription_from_template',
    'SUBSCRIPTION_TEMPLATES'
]