"""
Application Constants
"""

from enum import Enum
from typing import Dict, List


class BillingCycle(Enum):
    """Subscription billing cycle options."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


class SubscriptionStatus(Enum):
    """Subscription status options."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    EXPIRED = "expired"
    TRIAL = "trial"


class ServiceCategory(Enum):
    """Subscription service categories."""
    ENTERTAINMENT = "entertainment"
    PRODUCTIVITY = "productivity"
    HEALTH_FITNESS = "health_fitness"
    EDUCATION = "education"
    BUSINESS = "business"
    GAMING = "gaming"
    NEWS_MEDIA = "news_media"
    SHOPPING = "shopping"
    TRAVEL = "travel"
    UTILITIES = "utilities"
    OTHER = "other"


class NotificationType(Enum):
    """Notification types."""
    RENEWAL_REMINDER = "renewal_reminder"
    PRICE_CHANGE = "price_change"
    UNUSED_SERVICE = "unused_service"
    TRIAL_EXPIRING = "trial_expiring"
    OPTIMIZATION_TIP = "optimization_tip"


class UserRole(Enum):
    """User role options."""
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


# Business Constants
MAX_SUBSCRIPTIONS_FREE = 5
MAX_SUBSCRIPTIONS_PRO = 100
RENEWAL_REMINDER_DAYS = 3
UNUSED_THRESHOLD_DAYS = 30
TRIAL_WARNING_DAYS = 3

# Currency and Pricing
DEFAULT_CURRENCY = "CNY"
SUPPORTED_CURRENCIES = ["CNY", "USD", "EUR", "GBP", "JPY"]

# Service Categories Mapping
CATEGORY_ICONS: Dict[str, str] = {
    ServiceCategory.ENTERTAINMENT.value: "🎬",
    ServiceCategory.PRODUCTIVITY.value: "⚡",
    ServiceCategory.HEALTH_FITNESS.value: "💪",
    ServiceCategory.EDUCATION.value: "📚",
    ServiceCategory.BUSINESS.value: "💼",
    ServiceCategory.GAMING.value: "🎮",
    ServiceCategory.NEWS_MEDIA.value: "📰",
    ServiceCategory.SHOPPING.value: "🛒",
    ServiceCategory.TRAVEL.value: "✈️",
    ServiceCategory.UTILITIES.value: "🔧",
    ServiceCategory.OTHER.value: "📦",
}

CATEGORY_COLORS: Dict[str, str] = {
    ServiceCategory.ENTERTAINMENT.value: "#FF6B6B",
    ServiceCategory.PRODUCTIVITY.value: "#4ECDC4",
    ServiceCategory.HEALTH_FITNESS.value: "#45B7D1",
    ServiceCategory.EDUCATION.value: "#96CEB4",
    ServiceCategory.BUSINESS.value: "#FECA57",
    ServiceCategory.GAMING.value: "#FF9FF3",
    ServiceCategory.NEWS_MEDIA.value: "#54A0FF",
    ServiceCategory.SHOPPING.value: "#5F27CD",
    ServiceCategory.TRAVEL.value: "#00D2D3",
    ServiceCategory.UTILITIES.value: "#FF9F43",
    ServiceCategory.OTHER.value: "#C8D6E5",
}

# Popular Services Database
POPULAR_SERVICES: Dict[str, Dict] = {
    "Netflix": {
        "category": ServiceCategory.ENTERTAINMENT.value,
        "typical_price": 15.99,
        "billing_cycle": BillingCycle.MONTHLY.value,
        "description": "Video streaming service",
    },
    "Spotify": {
        "category": ServiceCategory.ENTERTAINMENT.value,
        "typical_price": 9.99,
        "billing_cycle": BillingCycle.MONTHLY.value,
        "description": "Music streaming service",
    },
    "ChatGPT Plus": {
        "category": ServiceCategory.PRODUCTIVITY.value,
        "typical_price": 20.0,
        "billing_cycle": BillingCycle.MONTHLY.value,
        "description": "AI assistant service",
    },
    "Adobe Creative Cloud": {
        "category": ServiceCategory.PRODUCTIVITY.value,
        "typical_price": 52.99,
        "billing_cycle": BillingCycle.MONTHLY.value,
        "description": "Creative software suite",
    },
    "Microsoft 365": {
        "category": ServiceCategory.PRODUCTIVITY.value,
        "typical_price": 6.99,
        "billing_cycle": BillingCycle.MONTHLY.value,
        "description": "Office productivity suite",
    },
    "YouTube Premium": {
        "category": ServiceCategory.ENTERTAINMENT.value,
        "typical_price": 11.99,
        "billing_cycle": BillingCycle.MONTHLY.value,
        "description": "Ad-free YouTube with extras",
    },
}

# AI Configuration
AI_RESPONSE_MAX_LENGTH = 500
AI_CONTEXT_WINDOW = 4000
AI_TEMPERATURE_DEFAULT = 0.7
AI_TEMPERATURE_CREATIVE = 0.9
AI_TEMPERATURE_ANALYTICAL = 0.3

# File Upload
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
ALLOWED_DOCUMENT_TYPES = ["application/pdf", "text/plain"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# API Rate Limits
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000
RATE_LIMIT_PER_DAY = 10000

# Cache TTL (seconds)
CACHE_TTL_SHORT = 300      # 5 minutes
CACHE_TTL_MEDIUM = 1800    # 30 minutes
CACHE_TTL_LONG = 3600      # 1 hour
CACHE_TTL_DAILY = 86400    # 24 hours

# Error Messages
ERROR_MESSAGES: Dict[str, str] = {
    "SUBSCRIPTION_NOT_FOUND": "Subscription not found",
    "SUBSCRIPTION_LIMIT_EXCEEDED": "Subscription limit exceeded",
    "INVALID_BILLING_CYCLE": "Invalid billing cycle",
    "INVALID_PRICE": "Invalid price format",
    "AI_SERVICE_UNAVAILABLE": "AI service is currently unavailable",
    "OCR_PROCESSING_FAILED": "Failed to process image",
    "AUTHENTICATION_REQUIRED": "Authentication required",
    "INSUFFICIENT_PERMISSIONS": "Insufficient permissions",
}

# Success Messages
SUCCESS_MESSAGES: Dict[str, str] = {
    "SUBSCRIPTION_CREATED": "Subscription created successfully",
    "SUBSCRIPTION_UPDATED": "Subscription updated successfully",
    "SUBSCRIPTION_DELETED": "Subscription deleted successfully",
    "SETTINGS_SAVED": "Settings saved successfully",
    "EXPORT_COMPLETED": "Export completed successfully",
}

# Validation Rules
MIN_PASSWORD_LENGTH = 8
MAX_SERVICE_NAME_LENGTH = 100
MAX_NOTES_LENGTH = 500
MIN_PRICE_VALUE = 0.01
MAX_PRICE_VALUE = 999999.99