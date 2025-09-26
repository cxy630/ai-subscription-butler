# AI订阅管家 - 技术架构文档

## 文档信息
- **版本**: 1.0
- **日期**: 2025-01-XX
- **作者**: AI订阅管家技术团队
- **状态**: 草稿

## 1. 架构概述

### 1.1 架构愿景
构建一个可扩展、高性能、安全可靠的AI驱动订阅管理系统，采用现代化技术栈和云原生架构模式，支持快速迭代和持续交付。

### 1.2 架构原则
- **简单性**: 选择成熟稳定的技术栈，避免过度工程化
- **可扩展性**: 支持水平扩展，处理用户增长
- **可维护性**: 清晰的代码结构，完善的文档
- **性能优先**: 响应时间和用户体验是核心指标
- **安全第一**: 数据保护和隐私合规是基础要求

### 1.3 技术选型依据

| 技术组件 | 选择 | 理由 |
|---------|------|-----|
| 后端语言 | Python 3.9+ | AI生态丰富，开发效率高 |
| Web框架 | Streamlit | 快速原型开发，内置组件丰富 |
| API框架 | FastAPI | 高性能，自动文档生成 |
| 数据库 | PostgreSQL | 可靠性高，JSON支持好 |
| AI平台 | OpenAI GPT | 能力最强，API稳定 |
| 缓存 | Redis | 性能优秀，数据结构丰富 |
| 部署 | Docker | 环境一致性，易于部署 |

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户界面层     │    │     业务逻辑层    │    │     数据存储层    │
│                │    │                │    │                │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │ Streamlit │  │    │  │   AI引擎   │  │    │  │PostgreSQL │  │
│  │    UI     │  │    │  │  (OpenAI)  │  │    │  │   主数据库  │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
│                │    │                │    │                │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │   移动端   │  │    │  │   OCR服务  │  │    │  │   Redis   │  │
│  │   PWA     │  │◀──▶│  │ (GPT Vision)│  │    │  │   缓存     │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
│                │    │                │    │                │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │   REST    │  │    │  │  订阅管理   │  │    │  │  文件存储   │  │
│  │   API     │  │    │  │   服务     │  │    │  │  (Local/S3) │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                │
                    ┌─────────────────┐
                    │   外部服务集成    │
                    │                │
                    │ • OpenAI API   │
                    │ • 邮件服务      │
                    │ • 短信服务      │
                    │ • 支付服务      │
                    └─────────────────┘
```

### 2.2 架构分层

#### 2.2.1 表现层 (Presentation Layer)
- **Streamlit Web应用**: 主要用户界面
- **REST API**: 移动端和第三方集成
- **PWA**: 渐进式Web应用，提供类原生体验

#### 2.2.2 业务逻辑层 (Business Logic Layer)
- **AI对话引擎**: 自然语言处理和响应生成
- **订阅管理服务**: 核心业务逻辑
- **OCR处理服务**: 账单图像识别
- **分析引擎**: 数据分析和洞察生成
- **通知服务**: 提醒和通知管理

#### 2.2.3 数据访问层 (Data Access Layer)
- **ORM映射**: SQLAlchemy数据模型
- **缓存管理**: Redis缓存策略
- **文件存储**: 图片和文档存储
- **外部API**: 第三方服务集成

#### 2.2.4 基础设施层 (Infrastructure Layer)
- **容器化**: Docker容器部署
- **负载均衡**: 流量分发和高可用
- **监控告警**: 系统健康监控
- **日志管理**: 集中化日志收集

## 3. 详细架构设计

### 3.1 应用架构

```
app/
├── main.py                 # Streamlit应用入口
├── config.py              # 配置管理
└── constants.py           # 应用常量

core/
├── ai/                    # AI相关模块
│   ├── agent.py           # AI代理主逻辑
│   ├── prompts.py         # 提示词模板
│   ├── intents.py         # 意图识别
│   └── cost_optimizer.py  # 成本优化
├── database/              # 数据库模块
│   ├── models.py          # 数据模型
│   ├── crud.py            # CRUD操作
│   ├── session.py         # 会话管理
│   └── migrations/        # 数据库迁移
├── services/              # 业务服务
│   ├── subscription.py    # 订阅服务
│   ├── analytics.py       # 分析服务
│   ├── ocr.py            # OCR服务
│   ├── reminder.py       # 提醒服务
│   ├── auth.py           # 认证服务
│   └── payment.py        # 支付服务
└── utils/                # 工具模块
    ├── validators.py     # 验证器
    ├── helpers.py        # 辅助函数
    ├── decorators.py     # 装饰器
    └── exceptions.py     # 异常定义

ui/
├── components/           # UI组件
│   ├── chat.py          # 聊天界面
│   ├── dashboard.py     # 仪表板
│   ├── subscription_card.py # 订阅卡片
│   └── charts.py        # 图表组件
├── pages/               # 页面组件
│   ├── home.py         # 首页
│   ├── chat_page.py    # AI聊天页
│   ├── analytics_page.py # 分析页
│   └── settings_page.py # 设置页
└── styles/
    └── custom.css      # 自定义样式
```

### 3.2 数据库设计

#### 3.2.1 核心数据模型

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    subscription_tier VARCHAR(20) DEFAULT 'free'
);

-- 订阅表
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    service_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    billing_cycle VARCHAR(20) NOT NULL, -- daily, weekly, monthly, yearly, lifetime
    category VARCHAR(50),
    next_billing_date DATE,
    status VARCHAR(20) DEFAULT 'active', -- active, cancelled, paused, expired, trial
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB -- 存储额外的灵活数据
);

-- AI对话历史表
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL,
    message TEXT NOT NULL,
    response TEXT,
    intent VARCHAR(100),
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- OCR处理记录表
CREATE TABLE ocr_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    extracted_data JSONB,
    confidence_score FLOAT,
    status VARCHAR(20) DEFAULT 'processing', -- processing, completed, failed
    created_at TIMESTAMP DEFAULT NOW()
);

-- 提醒表
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- renewal_reminder, price_change, unused_service
    scheduled_at TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' -- pending, sent, cancelled
);

-- 用户设置表
CREATE TABLE user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    notification_email BOOLEAN DEFAULT TRUE,
    notification_push BOOLEAN DEFAULT TRUE,
    reminder_days INTEGER DEFAULT 3,
    currency VARCHAR(3) DEFAULT 'CNY',
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
    settings JSONB -- 存储其他设置
);
```

#### 3.2.2 索引策略

```sql
-- 性能优化索引
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_next_billing ON subscriptions(next_billing_date);
CREATE INDEX idx_conversations_user_session ON conversations(user_id, session_id);
CREATE INDEX idx_reminders_scheduled ON reminders(scheduled_at) WHERE status = 'pending';
```

### 3.3 AI架构设计

#### 3.3.1 AI服务架构

```python
class AIAgent:
    """AI代理核心类"""

    def __init__(self):
        self.llm_client = OpenAIClient()
        self.intent_classifier = IntentClassifier()
        self.context_manager = ContextManager()
        self.response_generator = ResponseGenerator()

    def process_query(self, user_message: str, context: dict) -> AIResponse:
        """处理用户查询的主要流程"""
        # 1. 意图识别
        intent = self.intent_classifier.classify(user_message)

        # 2. 上下文更新
        enhanced_context = self.context_manager.update_context(
            user_message, intent, context
        )

        # 3. 路由到特定处理器
        if intent.type == "query_spending":
            return self._handle_spending_query(enhanced_context)
        elif intent.type == "add_subscription":
            return self._handle_add_subscription(enhanced_context)
        elif intent.type == "optimization_advice":
            return self._handle_optimization_query(enhanced_context)
        else:
            return self._handle_general_query(enhanced_context)
```

#### 3.3.2 提示词工程

```python
PROMPT_TEMPLATES = {
    "spending_analysis": """
你是一个专业的订阅管理助手。基于以下用户数据分析支出情况：

用户订阅数据：
{subscription_data}

用户问题：{user_question}

请提供：
1. 直接回答用户问题
2. 具体的数字统计
3. 有用的节省建议（如果适用）

保持回答简洁明了，使用友好的语调。
""",

    "optimization_suggestions": """
基于用户的订阅使用模式，提供优化建议：

订阅列表：{subscriptions}
使用模式：{usage_patterns}

请分析并建议：
1. 可能未充分利用的服务
2. 重复功能的服务
3. 更经济的替代方案
4. 具体的行动建议

重点关注实用性和节省潜力。
"""
}
```

### 3.4 OCR处理架构

#### 3.4.1 OCR处理流程

```python
class OCRService:
    """OCR服务处理账单图像"""

    def __init__(self):
        self.vision_client = OpenAIVisionClient()
        self.preprocessor = ImagePreprocessor()
        self.validator = DataValidator()

    async def process_bill_image(self, image_path: str, user_id: str) -> OCRResult:
        """处理账单图像的完整流程"""

        # 1. 图像预处理
        processed_image = await self.preprocessor.enhance_image(image_path)

        # 2. GPT Vision API调用
        extraction_prompt = self._build_extraction_prompt()
        raw_result = await self.vision_client.analyze_image(
            processed_image, extraction_prompt
        )

        # 3. 结果解析和验证
        parsed_data = self._parse_extraction_result(raw_result)
        validated_data = self.validator.validate_subscription_data(parsed_data)

        # 4. 置信度评分
        confidence_score = self._calculate_confidence(validated_data)

        # 5. 保存处理记录
        await self._save_ocr_record(user_id, image_path, validated_data, confidence_score)

        return OCRResult(
            data=validated_data,
            confidence=confidence_score,
            needs_review=confidence_score < 0.85
        )

    def _build_extraction_prompt(self) -> str:
        """构建OCR提取提示词"""
        return """
请从这张账单图片中提取订阅相关信息，返回JSON格式：

{
    "subscriptions": [
        {
            "service_name": "服务名称",
            "amount": 金额（数字）,
            "currency": "货币代码",
            "billing_date": "账单日期",
            "category": "推测的服务类别"
        }
    ],
    "total_amount": 总金额,
    "bill_date": "账单日期",
    "confidence": "提取信心度（0-1）"
}

如果无法识别某些信息，请标记为null。
"""
```

### 3.5 缓存策略

#### 3.5.1 Redis缓存架构

```python
class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self.redis_client = Redis(host='localhost', port=6379, db=0)

    # 用户订阅数据缓存
    async def get_user_subscriptions(self, user_id: str):
        cache_key = f"user:subscriptions:{user_id}"
        cached = await self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        return None

    async def cache_user_subscriptions(self, user_id: str, data: dict, ttl: int = 3600):
        cache_key = f"user:subscriptions:{user_id}"
        await self.redis_client.setex(cache_key, ttl, json.dumps(data))

    # AI响应缓存（针对常见问题）
    async def get_ai_response_cache(self, query_hash: str):
        cache_key = f"ai:response:{query_hash}"
        return await self.redis_client.get(cache_key)

    async def cache_ai_response(self, query_hash: str, response: str, ttl: int = 1800):
        cache_key = f"ai:response:{query_hash}"
        await self.redis_client.setex(cache_key, ttl, response)
```

#### 3.5.2 缓存策略配置

| 数据类型 | TTL | 缓存策略 | 失效条件 |
|---------|-----|----------|----------|
| 用户订阅列表 | 1小时 | Write-through | 订阅数据更新 |
| AI常见响应 | 30分钟 | Cache-aside | 相关数据变更 |
| 用户分析报告 | 6小时 | Lazy loading | 新订阅添加 |
| OCR处理结果 | 24小时 | Write-behind | 手动刷新 |

## 4. 安全架构

### 4.1 认证与授权

#### 4.1.1 JWT认证流程

```python
class AuthService:
    """认证服务"""

    def __init__(self):
        self.jwt_secret = settings.SECRET_KEY
        self.hash_algorithm = "HS256"
        self.token_expire_hours = 24

    def generate_token(self, user_id: str) -> str:
        """生成JWT令牌"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expire_hours),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.hash_algorithm)

    def verify_token(self, token: str) -> Optional[str]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.hash_algorithm])
            return payload.get("user_id")
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("令牌已过期")
        except jwt.InvalidTokenError:
            raise AuthenticationError("无效令牌")
```

### 4.2 数据加密

#### 4.2.1 敏感数据加密

```python
class EncryptionService:
    """加密服务"""

    def __init__(self):
        self.cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())

    def encrypt_sensitive_data(self, data: str) -> str:
        """加密敏感数据"""
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """解密敏感数据"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
```

### 4.3 API安全

#### 4.3.1 速率限制

```python
class RateLimiter:
    """API速率限制器"""

    def __init__(self):
        self.redis_client = Redis()

    async def check_rate_limit(self, user_id: str, endpoint: str) -> bool:
        """检查速率限制"""
        key = f"rate_limit:{user_id}:{endpoint}"
        current_requests = await self.redis_client.incr(key)

        if current_requests == 1:
            await self.redis_client.expire(key, 60)  # 1分钟窗口

        limit = self._get_rate_limit(endpoint)
        return current_requests <= limit

    def _get_rate_limit(self, endpoint: str) -> int:
        """获取端点速率限制"""
        limits = {
            "ai_query": 60,      # AI查询：每分钟60次
            "ocr_process": 10,   # OCR处理：每分钟10次
            "subscription_crud": 100  # 订阅CRUD：每分钟100次
        }
        return limits.get(endpoint, 30)
```

## 5. 部署架构

### 5.1 容器化架构

#### 5.1.1 Docker配置

```dockerfile
# 生产环境Dockerfile
FROM python:3.9-slim as builder

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行时镜像
FROM python:3.9-slim

WORKDIR /app

# 复制Python依赖
COPY --from=builder /root/.local /root/.local

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# 环境变量
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python scripts/health_check.py || exit 1

# 启动命令
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 5.1.2 Docker Compose配置

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/subscriptions
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: subscriptions
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 5.2 CI/CD流水线

#### 5.2.1 GitHub Actions配置

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        pytest tests/ --cov=core --cov=app --cov-report=xml

    - name: Code quality checks
      run: |
        black --check .
        flake8 .
        mypy .

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to production
      run: |
        # 部署脚本
        echo "部署到生产环境"
```

## 6. 监控与运维

### 6.1 监控架构

#### 6.1.1 应用监控

```python
import logging
import sentry_sdk
from prometheus_client import Counter, Histogram, Gauge

# Sentry错误监控
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
)

# Prometheus指标
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_USERS = Gauge('active_users_total', 'Number of active users')
AI_QUERY_COUNT = Counter('ai_queries_total', 'Total AI queries', ['intent'])
OCR_PROCESSING_TIME = Histogram('ocr_processing_seconds', 'OCR processing duration')

class MonitoringMiddleware:
    """监控中间件"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def log_request(self, request, response):
        """记录请求日志"""
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path
        ).inc()

        self.logger.info(
            f"{request.method} {request.url.path} - {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "user_id": getattr(request, "user_id", None)
            }
        )
```

### 6.2 日志管理

#### 6.2.1 结构化日志

```python
import structlog

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# 业务日志示例
async def process_subscription(user_id: str, subscription_data: dict):
    logger.info(
        "处理订阅创建",
        user_id=user_id,
        service_name=subscription_data.get("service_name"),
        price=subscription_data.get("price")
    )
```

## 7. 性能优化

### 7.1 数据库优化

#### 7.1.1 查询优化策略

```python
class OptimizedSubscriptionService:
    """优化的订阅服务"""

    def __init__(self, db: Session):
        self.db = db

    async def get_user_subscriptions_optimized(self, user_id: str):
        """优化的用户订阅查询"""
        # 使用索引和预加载
        query = (
            select(Subscription)
            .options(selectinload(Subscription.reminders))
            .where(Subscription.user_id == user_id)
            .where(Subscription.status == 'active')
            .order_by(Subscription.next_billing_date)
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_spending_analytics_optimized(self, user_id: str, months: int = 6):
        """优化的支出分析查询"""
        # 使用聚合查询减少数据传输
        query = text("""
            SELECT
                category,
                DATE_TRUNC('month', created_at) as month,
                SUM(price) as total_amount,
                COUNT(*) as subscription_count
            FROM subscriptions
            WHERE user_id = :user_id
            AND created_at >= NOW() - INTERVAL ':months months'
            AND status = 'active'
            GROUP BY category, DATE_TRUNC('month', created_at)
            ORDER BY month DESC, total_amount DESC
        """)

        result = await self.db.execute(
            query,
            {"user_id": user_id, "months": months}
        )
        return result.fetchall()
```

### 7.2 AI性能优化

#### 7.2.1 模型路由和缓存

```python
class OptimizedAIService:
    """优化的AI服务"""

    def __init__(self):
        self.cache = CacheManager()
        self.cheap_model = "gpt-3.5-turbo"
        self.premium_model = "gpt-4"

    async def get_ai_response_optimized(self, query: str, context: dict):
        """优化的AI响应获取"""

        # 1. 检查缓存
        query_hash = hashlib.md5(f"{query}:{hash(str(context))}".encode()).hexdigest()
        cached_response = await self.cache.get_ai_response_cache(query_hash)
        if cached_response:
            return cached_response

        # 2. 智能模型选择
        model = self._select_model(query, context)

        # 3. 获取响应
        response = await self._call_ai_model(query, context, model)

        # 4. 缓存结果
        await self.cache.cache_ai_response(query_hash, response)

        return response

    def _select_model(self, query: str, context: dict) -> str:
        """智能选择AI模型"""
        # 简单查询使用便宜模型
        simple_patterns = ["多少钱", "总费用", "有几个订阅"]
        if any(pattern in query for pattern in simple_patterns):
            return self.cheap_model

        # 复杂分析使用高级模型
        return self.premium_model
```

## 8. 扩展性设计

### 8.1 微服务准备

虽然MVP阶段采用单体架构，但设计时考虑未来微服务拆分：

```python
# 服务接口定义，为未来微服务化准备
class SubscriptionServiceInterface:
    """订阅服务接口"""
    async def create_subscription(self, user_id: str, data: dict) -> dict
    async def get_user_subscriptions(self, user_id: str) -> List[dict]
    async def update_subscription(self, subscription_id: str, data: dict) -> dict
    async def delete_subscription(self, subscription_id: str) -> bool

class AIServiceInterface:
    """AI服务接口"""
    async def process_query(self, query: str, context: dict) -> dict
    async def generate_insights(self, user_data: dict) -> dict

class OCRServiceInterface:
    """OCR服务接口"""
    async def process_image(self, image_path: str) -> dict
    async def extract_subscriptions(self, ocr_data: dict) -> List[dict]
```

### 8.2 插件架构

```python
class PluginManager:
    """插件管理器"""

    def __init__(self):
        self.plugins = {}

    def register_plugin(self, name: str, plugin: 'Plugin'):
        """注册插件"""
        self.plugins[name] = plugin

    async def execute_hook(self, hook_name: str, *args, **kwargs):
        """执行钩子"""
        results = []
        for plugin in self.plugins.values():
            if hasattr(plugin, hook_name):
                result = await getattr(plugin, hook_name)(*args, **kwargs)
                results.append(result)
        return results

class NotificationPlugin:
    """通知插件示例"""

    async def before_subscription_expires(self, subscription: dict):
        """订阅到期前钩子"""
        # 发送自定义通知逻辑
        pass
```

## 9. 技术债务管理

### 9.1 已知技术债务

1. **单体架构限制**: MVP阶段的权衡，未来需要微服务化
2. **Streamlit性能限制**: 大量数据时可能性能不足
3. **同步数据库操作**: 部分操作未异步化
4. **有限的测试覆盖**: 需要增加集成测试和E2E测试

### 9.2 重构计划

| 优先级 | 项目 | 时间估算 | 影响 |
|--------|------|----------|------|
| P1 | 异步数据库操作 | 2周 | 性能提升50% |
| P2 | API响应缓存优化 | 1周 | 响应时间减少30% |
| P3 | 前端框架迁移(React) | 4周 | 用户体验显著提升 |
| P4 | 微服务拆分准备 | 6周 | 可扩展性大幅提升 |

## 10. 文档维护

### 10.1 架构决策记录 (ADR)

每个重要技术决策都需要记录ADR，包括：
- 决策背景
- 考虑的选项
- 决策结果
- 后果分析

### 10.2 架构演进

随着项目发展，本文档将持续更新：
- 每月架构评审
- 重大变更时更新
- 性能瓶颈分析后优化

---

**文档状态**: 草稿
**下次审核**: [待安排]
**版本历史**:
- v1.0 - 初始架构设计 - [日期]

---

*此文档定义了AI订阅管家的技术架构基础，是所有技术决策的参考依据。*