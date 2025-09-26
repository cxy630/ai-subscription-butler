# AI订阅管家 - 数据库设计文档

## 文档信息
- **版本**: 1.0
- **日期**: 2025-01-XX
- **作者**: AI订阅管家数据库团队
- **状态**: 草稿

## 1. 数据库概述

### 1.1 设计目标
- **数据完整性**: 确保财务数据的准确性和一致性
- **高性能**: 支持快速查询和分析操作
- **可扩展性**: 支持用户增长和数据量增加
- **灵活性**: 使用JSONB字段支持动态数据结构
- **安全性**: 敏感数据加密和访问控制

### 1.2 技术选择
- **主数据库**: PostgreSQL 15+
- **缓存层**: Redis 7+
- **开发环境**: SQLite 3 (快速开发和测试)
- **ORM**: SQLAlchemy 2.0+ (异步支持)
- **迁移工具**: Alembic

### 1.3 数据库架构原则
- **范式化设计**: 避免数据冗余，确保数据一致性
- **适度反范式**: 为性能优化适当冗余
- **JSONB灵活性**: 使用JSONB存储非结构化数据
- **索引策略**: 基于查询模式设计索引
- **分区准备**: 为大数据量增长预留分区策略

## 2. 数据库实体关系图 (ERD)

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │  subscriptions  │       │   reminders     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │◀─────┐│ id (PK)         │◀─────┐│ id (PK)         │
│ email (UK)      │      ││ user_id (FK)    │      ││ user_id (FK)    │
│ password_hash   │      ││ service_name    │      ││ subscription_id │
│ name            │      ││ price           │      ││ type            │
│ created_at      │      ││ currency        │      ││ scheduled_at    │
│ updated_at      │      ││ billing_cycle   │      ││ sent_at         │
│ is_active       │      ││ category        │      ││ status          │
│ subscription_tier│      ││ next_billing_date│     │└─────────────────┘
└─────────────────┘      ││ status          │      │
        │                ││ notes           │      │
        │                ││ created_at      │      │
        │                ││ updated_at      │      │
        │                ││ metadata        │      │
        │                │└─────────────────┘      │
        │                │                         │
        │                └─────────────────────────┘
        │
        │   ┌─────────────────┐       ┌─────────────────┐
        │   │ conversations   │       │   ocr_records   │
        │   ├─────────────────┤       ├─────────────────┤
        └──▶│ id (PK)         │       │ id (PK)         │◀───┘
            │ user_id (FK)    │       │ user_id (FK)    │
            │ session_id      │       │ file_path       │
            │ message         │       │ extracted_data  │
            │ response        │       │ confidence_score│
            │ intent          │       │ status          │
            │ confidence      │       │ created_at      │
            │ created_at      │       └─────────────────┘
            └─────────────────┘

        │   ┌─────────────────┐       ┌─────────────────┐
        │   │ user_settings   │       │ audit_logs      │
        │   ├─────────────────┤       ├─────────────────┤
        └──▶│ id (PK)         │       │ id (PK)         │◀───┘
            │ user_id (FK)    │       │ user_id (FK)    │
            │ notification_email│     │ table_name      │
            │ notification_push│      │ record_id       │
            │ reminder_days   │       │ action          │
            │ currency        │       │ old_values      │
            │ timezone        │       │ new_values      │
            │ settings        │       │ created_at      │
            └─────────────────┘       └─────────────────┘
```

## 3. 详细表结构设计

### 3.1 用户相关表

#### 3.1.1 users 表
用户基本信息表，存储用户账户核心数据。

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    avatar_url VARCHAR(500),
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'premium', 'enterprise')),
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 索引
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription_tier ON users(subscription_tier);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_metadata_gin ON users USING GIN(metadata);

-- 触发器：自动更新updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

**字段说明**:
- `id`: UUID主键，使用PostgreSQL内置函数生成
- `email`: 用户邮箱，唯一约束
- `password_hash`: BCrypt加密的密码哈希
- `subscription_tier`: 用户订阅级别，影响功能限制
- `metadata`: JSONB字段存储额外用户属性

#### 3.1.2 user_settings 表
用户个人设置表，存储用户偏好配置。

```sql
CREATE TABLE user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_email BOOLEAN DEFAULT TRUE,
    notification_push BOOLEAN DEFAULT TRUE,
    notification_sms BOOLEAN DEFAULT FALSE,
    reminder_days INTEGER DEFAULT 3 CHECK (reminder_days >= 1 AND reminder_days <= 30),
    currency VARCHAR(3) DEFAULT 'CNY' CHECK (currency IN ('CNY', 'USD', 'EUR', 'GBP', 'JPY')),
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
    language VARCHAR(10) DEFAULT 'zh-CN',
    theme VARCHAR(20) DEFAULT 'light' CHECK (theme IN ('light', 'dark', 'auto')),
    budget_alert_threshold DECIMAL(10,2),
    auto_categorization BOOLEAN DEFAULT TRUE,
    data_export_format VARCHAR(10) DEFAULT 'json' CHECK (data_export_format IN ('json', 'csv', 'excel')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settings JSONB DEFAULT '{}'::jsonb,
    UNIQUE(user_id)
);

-- 索引
CREATE UNIQUE INDEX idx_user_settings_user_id ON user_settings(user_id);
CREATE TRIGGER trigger_user_settings_updated_at
    BEFORE UPDATE ON user_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

### 3.2 订阅相关表

#### 3.2.1 subscriptions 表
核心业务表，存储用户的所有订阅信息。

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_name VARCHAR(100) NOT NULL,
    service_logo_url VARCHAR(500),
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    currency VARCHAR(3) DEFAULT 'CNY' CHECK (currency IN ('CNY', 'USD', 'EUR', 'GBP', 'JPY')),
    billing_cycle VARCHAR(20) NOT NULL CHECK (billing_cycle IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'lifetime')),
    category VARCHAR(50) CHECK (category IN (
        'entertainment', 'productivity', 'health_fitness', 'education',
        'business', 'gaming', 'news_media', 'shopping', 'travel',
        'utilities', 'finance', 'social', 'development', 'other'
    )),
    next_billing_date DATE,
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'paused', 'expired', 'trial')),
    payment_method VARCHAR(50),
    notes TEXT,
    usage_tracking JSONB DEFAULT '{}'::jsonb, -- 使用情况跟踪
    price_history JSONB DEFAULT '[]'::jsonb, -- 价格历史记录
    tags VARCHAR(255)[], -- 用户自定义标签
    is_shared BOOLEAN DEFAULT FALSE, -- 是否为共享订阅
    shared_with UUID[], -- 共享用户ID数组
    auto_renewal BOOLEAN DEFAULT TRUE,
    trial_end_date DATE,
    cancellation_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 索引
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_category ON subscriptions(category);
CREATE INDEX idx_subscriptions_next_billing_date ON subscriptions(next_billing_date)
    WHERE status = 'active';
CREATE INDEX idx_subscriptions_service_name ON subscriptions(service_name);
CREATE INDEX idx_subscriptions_billing_cycle ON subscriptions(billing_cycle);
CREATE INDEX idx_subscriptions_created_at ON subscriptions(created_at);
CREATE INDEX idx_subscriptions_tags_gin ON subscriptions USING GIN(tags);
CREATE INDEX idx_subscriptions_metadata_gin ON subscriptions USING GIN(metadata);
CREATE INDEX idx_subscriptions_usage_tracking_gin ON subscriptions USING GIN(usage_tracking);

-- 复合索引
CREATE INDEX idx_subscriptions_user_status_billing ON subscriptions(user_id, status, next_billing_date);

-- 触发器
CREATE TRIGGER trigger_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

**字段说明**:
- `price_history`: 存储价格变更历史，格式 `[{"price": 15.99, "date": "2024-01-01", "reason": "price_increase"}]`
- `usage_tracking`: 存储使用情况数据，由外部API或用户手动更新
- `tags`: 用户自定义标签数组
- `shared_with`: 家庭共享功能的用户ID数组

#### 3.2.2 subscription_categories 表
订阅类别配置表，用于标准化分类管理。

```sql
CREATE TABLE subscription_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name_zh VARCHAR(100) NOT NULL,
    display_name_en VARCHAR(100) NOT NULL,
    icon VARCHAR(100),
    color VARCHAR(7), -- HEX颜色代码
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 预填充数据
INSERT INTO subscription_categories (name, display_name_zh, display_name_en, icon, color) VALUES
('entertainment', '娱乐', 'Entertainment', '🎬', '#FF6B6B'),
('productivity', '生产力', 'Productivity', '⚡', '#4ECDC4'),
('health_fitness', '健康健身', 'Health & Fitness', '💪', '#45B7D1'),
('education', '教育', 'Education', '📚', '#96CEB4'),
('business', '商务', 'Business', '💼', '#FECA57'),
('gaming', '游戏', 'Gaming', '🎮', '#FF9FF3'),
('news_media', '新闻媒体', 'News & Media', '📰', '#54A0FF'),
('shopping', '购物', 'Shopping', '🛒', '#5F27CD'),
('travel', '旅行', 'Travel', '✈️', '#00D2D3'),
('utilities', '工具', 'Utilities', '🔧', '#FF9F43'),
('other', '其他', 'Other', '📦', '#C8D6E5');
```

### 3.3 AI和分析相关表

#### 3.3.1 conversations 表
存储用户与AI助手的对话记录。

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL,
    message TEXT NOT NULL,
    response TEXT,
    intent VARCHAR(100),
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    processing_time_ms INTEGER,
    model_used VARCHAR(50),
    token_usage JSONB, -- {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
    context_data JSONB,
    feedback_rating INTEGER CHECK (feedback_rating >= 1 AND feedback_rating <= 5),
    feedback_comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_user_session ON conversations(user_id, session_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_conversations_intent ON conversations(intent);

-- 分区表 (按月分区，为未来大数据量准备)
-- CREATE TABLE conversations_y2024m01 PARTITION OF conversations
--     FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

#### 3.3.2 user_insights 表
存储为用户生成的分析洞察。

```sql
CREATE TABLE user_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL CHECK (insight_type IN (
        'spending_trend', 'unused_subscription', 'price_increase',
        'saving_opportunity', 'usage_pattern', 'budget_alert'
    )),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    importance VARCHAR(20) DEFAULT 'medium' CHECK (importance IN ('low', 'medium', 'high', 'critical')),
    action_required BOOLEAN DEFAULT FALSE,
    suggested_actions JSONB,
    data_snapshot JSONB, -- 生成洞察时的数据快照
    is_read BOOLEAN DEFAULT FALSE,
    is_dismissed BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_user_insights_user_id ON user_insights(user_id);
CREATE INDEX idx_user_insights_type ON user_insights(insight_type);
CREATE INDEX idx_user_insights_importance ON user_insights(importance);
CREATE INDEX idx_user_insights_unread ON user_insights(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_user_insights_created_at ON user_insights(created_at);
```

### 3.4 OCR和文件处理表

#### 3.4.1 ocr_records 表
OCR处理记录表。

```sql
CREATE TABLE ocr_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_filename VARCHAR(255),
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(50),
    extracted_data JSONB,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    processing_time_ms INTEGER,
    model_used VARCHAR(50),
    status VARCHAR(20) DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed', 'requires_review')),
    error_message TEXT,
    manual_corrections JSONB, -- 用户手动修正的数据
    subscriptions_created UUID[], -- 基于此OCR创建的订阅ID数组
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_ocr_records_user_id ON ocr_records(user_id);
CREATE INDEX idx_ocr_records_status ON ocr_records(status);
CREATE INDEX idx_ocr_records_created_at ON ocr_records(created_at);
CREATE INDEX idx_ocr_records_confidence ON ocr_records(confidence_score);
```

### 3.5 通知和提醒表

#### 3.5.1 reminders 表
提醒和通知表。

```sql
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN (
        'renewal_reminder', 'price_change', 'unused_service',
        'trial_expiring', 'optimization_tip', 'budget_alert', 'custom'
    )),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivery_method VARCHAR(20)[] DEFAULT '{"email"}' CHECK (
        delivery_method <@ '{"email", "push", "sms", "in_app"}'
    ),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'cancelled', 'failed')),
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    priority VARCHAR(10) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    external_id VARCHAR(255), -- 外部通知服务的ID
    response_data JSONB, -- 通知服务的响应数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_reminders_user_id ON reminders(user_id);
CREATE INDEX idx_reminders_subscription_id ON reminders(subscription_id);
CREATE INDEX idx_reminders_scheduled_at ON reminders(scheduled_at);
CREATE INDEX idx_reminders_status_scheduled ON reminders(status, scheduled_at)
    WHERE status = 'pending';
CREATE INDEX idx_reminders_type ON reminders(type);
```

#### 3.5.2 notification_templates 表
通知模板表。

```sql
CREATE TABLE notification_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,
    subject_template TEXT,
    body_template TEXT NOT NULL,
    variables JSONB, -- 模板可用变量说明
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 预填充通知模板
INSERT INTO notification_templates (name, type, subject_template, body_template, variables) VALUES
(
    'renewal_reminder',
    'renewal_reminder',
    '提醒：{{service_name}} 将在 {{days}} 天后续费',
    '您的 {{service_name}} 订阅将在 {{renewal_date}} 续费 ￥{{price}}。如需取消，请及时处理。',
    '{"service_name": "服务名称", "days": "天数", "renewal_date": "续费日期", "price": "价格"}'
);
```

### 3.6 系统和审计表

#### 3.6.1 audit_logs 表
审计日志表，记录所有重要数据变更。

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id UUID,
    action VARCHAR(20) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_table_record ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- 分区表 (按月分区)
-- 示例分区创建
-- CREATE TABLE audit_logs_y2024m01 PARTITION OF audit_logs
--     FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

#### 3.6.2 system_settings 表
系统配置表。

```sql
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    data_type VARCHAR(20) DEFAULT 'string' CHECK (data_type IN ('string', 'number', 'boolean', 'json')),
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE, -- 是否可被前端访问
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 预填充系统设置
INSERT INTO system_settings (key, value, data_type, description, is_public, category) VALUES
('max_subscriptions_free', '5', 'number', '免费用户最大订阅数', TRUE, 'limits'),
('max_subscriptions_premium', '100', 'number', '高级用户最大订阅数', TRUE, 'limits'),
('ai_query_limit_free', '100', 'number', '免费用户每日AI查询限制', TRUE, 'limits'),
('ocr_monthly_limit_free', '30', 'number', '免费用户每月OCR处理限制', TRUE, 'limits'),
('default_reminder_days', '3', 'number', '默认提醒天数', TRUE, 'defaults'),
('supported_currencies', '["CNY", "USD", "EUR", "GBP", "JPY"]', 'json', '支持的货币列表', TRUE, 'config');
```

## 4. 视图和函数

### 4.1 常用业务视图

#### 4.1.1 用户订阅概览视图

```sql
CREATE VIEW user_subscription_overview AS
SELECT
    u.id as user_id,
    u.email,
    u.subscription_tier,
    COUNT(s.id) as total_subscriptions,
    COUNT(CASE WHEN s.status = 'active' THEN 1 END) as active_subscriptions,
    COUNT(CASE WHEN s.status = 'trial' THEN 1 END) as trial_subscriptions,
    SUM(CASE WHEN s.status = 'active' THEN s.price ELSE 0 END) as monthly_spending,
    SUM(CASE WHEN s.status = 'active' AND s.billing_cycle = 'yearly' THEN s.price/12
             WHEN s.status = 'active' AND s.billing_cycle = 'monthly' THEN s.price
             ELSE 0 END) as normalized_monthly_spending,
    MAX(s.created_at) as last_subscription_added,
    COUNT(CASE WHEN s.next_billing_date <= CURRENT_DATE + INTERVAL '7 days'
               AND s.status = 'active' THEN 1 END) as upcoming_renewals
FROM users u
LEFT JOIN subscriptions s ON u.id = s.user_id
GROUP BY u.id, u.email, u.subscription_tier;
```

#### 4.1.2 支出分析视图

```sql
CREATE VIEW monthly_spending_analysis AS
SELECT
    user_id,
    DATE_TRUNC('month', created_at) as month,
    category,
    COUNT(*) as subscription_count,
    SUM(price) as total_amount,
    AVG(price) as avg_price,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM subscriptions
WHERE status = 'active'
GROUP BY user_id, DATE_TRUNC('month', created_at), category
ORDER BY user_id, month DESC, total_amount DESC;
```

### 4.2 存储函数

#### 4.2.1 计算用户月度支出

```sql
CREATE OR REPLACE FUNCTION calculate_monthly_spending(
    p_user_id UUID,
    p_target_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    category VARCHAR(50),
    subscription_count BIGINT,
    total_monthly_amount DECIMAL(10,2),
    avg_amount DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.category,
        COUNT(*)::BIGINT as subscription_count,
        SUM(
            CASE
                WHEN s.billing_cycle = 'monthly' THEN s.price
                WHEN s.billing_cycle = 'yearly' THEN s.price / 12
                WHEN s.billing_cycle = 'quarterly' THEN s.price / 3
                WHEN s.billing_cycle = 'weekly' THEN s.price * 4.33
                WHEN s.billing_cycle = 'daily' THEN s.price * 30
                ELSE s.price
            END
        )::DECIMAL(10,2) as total_monthly_amount,
        AVG(s.price)::DECIMAL(10,2) as avg_amount
    FROM subscriptions s
    WHERE s.user_id = p_user_id
      AND s.status = 'active'
      AND (s.end_date IS NULL OR s.end_date >= p_target_date)
    GROUP BY s.category
    ORDER BY total_monthly_amount DESC;
END;
$$ LANGUAGE plpgsql;
```

#### 4.2.2 获取即将到期的订阅

```sql
CREATE OR REPLACE FUNCTION get_upcoming_renewals(
    p_user_id UUID,
    p_days_ahead INTEGER DEFAULT 7
)
RETURNS TABLE (
    subscription_id UUID,
    service_name VARCHAR(100),
    price DECIMAL(10,2),
    currency VARCHAR(3),
    next_billing_date DATE,
    days_until_renewal INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id as subscription_id,
        s.service_name,
        s.price,
        s.currency,
        s.next_billing_date,
        (s.next_billing_date - CURRENT_DATE)::INTEGER as days_until_renewal
    FROM subscriptions s
    WHERE s.user_id = p_user_id
      AND s.status = 'active'
      AND s.next_billing_date BETWEEN CURRENT_DATE AND CURRENT_DATE + p_days_ahead
    ORDER BY s.next_billing_date ASC;
END;
$$ LANGUAGE plpgsql;
```

## 5. 数据迁移策略

### 5.1 版本控制

使用Alembic进行数据库版本控制：

```python
# migrations/versions/001_initial_schema.py
"""初始数据库架构

Revision ID: 001
Revises:
Create Date: 2025-01-XX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 创建用户表
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        # ... 其他字段
    )

    # 创建索引
    op.create_unique_index('idx_users_email', 'users', ['email'])

def downgrade() -> None:
    op.drop_table('users')
```

### 5.2 数据库迁移最佳实践

1. **向后兼容**: 新字段使用默认值
2. **分步骤迁移**: 大的更改分多个版本进行
3. **数据验证**: 迁移后验证数据完整性
4. **回滚计划**: 每个迁移都有对应的回滚脚本

## 6. 性能优化

### 6.1 查询优化

#### 6.1.1 常见查询模式索引

```sql
-- 用户订阅查询优化
CREATE INDEX CONCURRENTLY idx_subscriptions_user_active_billing
ON subscriptions(user_id, status, next_billing_date)
WHERE status = 'active';

-- 支出分析查询优化
CREATE INDEX CONCURRENTLY idx_subscriptions_category_created
ON subscriptions(category, created_at, price)
WHERE status = 'active';

-- AI对话查询优化
CREATE INDEX CONCURRENTLY idx_conversations_session_time
ON conversations(session_id, created_at);
```

#### 6.1.2 分区表策略

```sql
-- conversations 表按月分区
CREATE TABLE conversations_partitioned (
    LIKE conversations INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- 创建分区
CREATE TABLE conversations_2024_01 PARTITION OF conversations_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE conversations_2024_02 PARTITION OF conversations_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### 6.2 缓存策略

#### 6.2.1 Redis缓存键设计

```python
# 缓存键命名规范
CACHE_KEYS = {
    'user_subscriptions': 'user:subs:{user_id}',
    'monthly_spending': 'user:spending:{user_id}:{month}',
    'ai_response': 'ai:resp:{hash}',
    'user_insights': 'insights:{user_id}',
    'popular_services': 'services:popular',
}

# TTL设置
CACHE_TTL = {
    'user_subscriptions': 3600,      # 1小时
    'monthly_spending': 3600 * 6,    # 6小时
    'ai_response': 1800,             # 30分钟
    'user_insights': 3600 * 12,      # 12小时
    'popular_services': 3600 * 24,   # 24小时
}
```

## 7. 安全性

### 7.1 数据加密

#### 7.1.1 字段级加密

```sql
-- 敏感数据加密函数
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(data TEXT)
RETURNS TEXT AS $$
BEGIN
    -- 使用pgcrypto扩展进行加密
    RETURN encode(encrypt(data::bytea, 'encryption_key', 'aes'), 'base64');
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION decrypt_sensitive_data(encrypted_data TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN convert_from(decrypt(decode(encrypted_data, 'base64'), 'encryption_key', 'aes'), 'UTF8');
END;
$$ LANGUAGE plpgsql;
```

### 7.2 访问控制

#### 7.2.1 行级安全策略

```sql
-- 启用行级安全
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- 创建策略：用户只能访问自己的订阅
CREATE POLICY user_subscriptions_policy ON subscriptions
    FOR ALL TO application_user
    USING (user_id = current_setting('app.current_user_id')::UUID);

-- 创建应用用户角色
CREATE ROLE application_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON subscriptions TO application_user;
```

### 7.3 审计触发器

```sql
-- 创建审计触发器函数
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        user_id,
        table_name,
        record_id,
        action,
        old_values,
        new_values,
        created_at
    ) VALUES (
        COALESCE(NEW.user_id, OLD.user_id),
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END,
        NOW()
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 为重要表添加审计触发器
CREATE TRIGGER subscriptions_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();

CREATE TRIGGER users_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

## 8. 监控和维护

### 8.1 性能监控查询

```sql
-- 查看表大小和索引使用情况
CREATE VIEW table_stats AS
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation,
    most_common_vals,
    most_common_freqs
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY schemaname, tablename, attname;

-- 查看慢查询
SELECT
    query,
    calls,
    total_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

### 8.2 数据备份策略

```bash
#!/bin/bash
# 数据库备份脚本

# 配置
DB_NAME="subscriptions"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份
pg_dump -h localhost -U postgres -d $DB_NAME \
  --format=custom \
  --compress=9 \
  --file="$BACKUP_DIR/backup_$DATE.dump"

# 清理老备份（保留30天）
find $BACKUP_DIR -name "backup_*.dump" -mtime +30 -delete

# 验证备份
pg_restore --list "$BACKUP_DIR/backup_$DATE.dump" > /dev/null
if [ $? -eq 0 ]; then
    echo "Backup successful: backup_$DATE.dump"
else
    echo "Backup failed!"
    exit 1
fi
```

## 9. 测试数据

### 9.1 测试数据生成脚本

```sql
-- 生成测试用户
INSERT INTO users (email, password_hash, name, subscription_tier) VALUES
('test1@example.com', '$2b$12$hashed_password', '测试用户1', 'free'),
('test2@example.com', '$2b$12$hashed_password', '测试用户2', 'premium');

-- 生成测试订阅数据
WITH test_user AS (
    SELECT id FROM users WHERE email = 'test1@example.com'
)
INSERT INTO subscriptions (user_id, service_name, price, currency, billing_cycle, category, next_billing_date, status)
SELECT
    test_user.id,
    services.name,
    services.price,
    'CNY',
    'monthly',
    services.category,
    CURRENT_DATE + INTERVAL '30 days',
    'active'
FROM test_user,
(VALUES
    ('Netflix', 15.99, 'entertainment'),
    ('Spotify', 9.99, 'entertainment'),
    ('ChatGPT Plus', 20.00, 'productivity'),
    ('Adobe Creative Cloud', 52.99, 'productivity'),
    ('Microsoft 365', 6.99, 'productivity')
) AS services(name, price, category);
```

## 10. 文档维护

### 10.1 数据字典

维护完整的数据字典，包括：
- 表结构说明
- 字段含义和约束
- 索引策略说明
- 业务规则映射

### 10.2 变更日志

记录所有数据库结构变更：
- 变更日期和版本
- 变更原因和影响
- 迁移脚本和回滚方案
- 性能影响评估

---

**文档状态**: 草稿
**下次审核**: [待安排]
**版本历史**:
- v1.0 - 初始数据库设计 - [日期]

---

*此文档是AI订阅管家数据库设计的权威参考，所有数据库相关开发都应遵循此设计。*