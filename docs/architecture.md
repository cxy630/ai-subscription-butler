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
- **AI对话引擎**: 基于Gemini 2.5 Flash Lite的自然语言处理和响应生成
- **订阅管理服务**: 核心业务逻辑(CRUD、分类管理、状态跟踪)
- **OCR处理服务**: 账单图像识别(三步工作流程)
- **分析引擎**: 数据分析和洞察生成(支出趋势、分类洞察)
- **提醒服务**: 智能提醒系统(日期计算、优先级评估、通知生成)
- **数据导出服务**: 多格式数据导出(CSV、JSON)

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
│   ├── settings_page.py # 设置页
│   ├── add_subscription_page.py  # 添加订阅独立页面 (2025-10-01新增)
│   ├── template_page.py          # 模板选择独立页面 (2025-10-01新增)
│   └── scan_bill_page.py         # 扫描账单独立页面 (2025-10-01新增)
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

## 8. 最新功能架构 (2025-09-30)

### 8.1 智能提醒系统 (core/services/reminder_system.py)

#### 8.1.1 系统架构
```python
class ReminderSystem:
    """智能提醒系统核心类"""

    def calculate_next_billing_date(self, start_date, billing_cycle):
        """
        智能计算下次续费日期
        - 处理月末边界情况(Jan 31 → Feb 28)
        - 支持闰年计算
        - 多种计费周期(daily/weekly/monthly/yearly)
        """

    def generate_reminders(self, subscriptions, reminder_days=[7, 3, 1, 0]):
        """
        生成优先级提醒列表
        Priority Logic:
        - urgent:  days < 0 (已逾期)
        - high:    days == 0 (今天)
        - medium:  0 < days <= 3 (3天内)
        - low:     days > 3 (3天后)
        """

    def get_upcoming_renewals(self, subscriptions, days_ahead=30):
        """获取未来N天内即将续费的订阅"""

    def get_reminder_statistics(self, subscriptions):
        """生成提醒统计数据"""
```

#### 8.1.2 关键算法
**月末日期处理:**
```python
# 示例: 订阅开始日期为1月31日
start_date = datetime(2025, 1, 31)
# monthly cycle后自动调整为2月28日
next_date = datetime(2025, 2, 28)  # 非闰年
next_date = datetime(2024, 2, 29)  # 闰年
```

### 8.2 数据分析与导出

#### 8.2.1 支出趋势分析 (ui/components/dashboard.py:337-391)
```python
def render_spending_trends():
    """
    展示未来6个月支出趋势
    - 基于当前订阅数据模拟
    - Plotly折线图交互展示
    - 支持多货币汇总
    """
```

#### 8.2.2 分类洞察 (ui/components/dashboard.py:393-422)
```python
def render_category_insights():
    """
    分类详细分析
    - 饼图展示占比
    - 可展开查看服务列表
    - 统计每个分类的订阅数和总成本
    """
```

#### 8.2.3 数据导出 (ui/components/dashboard.py:658-749)
```python
def export_data(format='csv'):
    """
    多格式数据导出
    Supported Formats:
    - CSV: 表格数据,适合Excel分析
    - JSON: 结构化数据,适合程序处理
    - PDF: 详细报告(计划中)

    Export Fields:
    - 基本信息: 服务名、价格、周期
    - 日期信息: 订阅日期、续费日期
    - 分类信息: category, status
    - 备注: notes
    """
```

### 8.3 内联编辑功能

#### 8.3.1 手风琴式UI (ui/components/dashboard.py:197-205)
```python
# 订阅列表渲染逻辑
for subscription in subscriptions:
    render_subscription_card(subscription)  # 卡片显示

    # 如果编辑状态为True,在卡片下方展开编辑表单
    if st.session_state.get(f"edit_subscription_{sub['id']}", False):
        render_inline_edit_form(subscription)  # 内联编辑表单
```

#### 8.3.2 状态管理
```python
# Button-based toggle with st.rerun()
if editing:
    if st.button("❌ 取消"):
        st.session_state[edit_key] = False
        st.rerun()  # 触发页面重渲染
else:
    if st.button("✏️ 编辑"):
        st.session_state[edit_key] = True
        st.rerun()  # 立即展开编辑表单
```

#### 8.3.3 UI设计特性
- 绿色左边框突出编辑区域
- 完整表单字段(与添加订阅一致)
- 三个操作按钮: 💾 保存 | ❌ 取消 | 🗑️ 删除
- 编辑状态下按钮切换为"取消"

### 8.4 技术栈更新

#### 8.4.1 AI模型切换
```
OpenAI GPT → Google Gemini 2.5 Flash Lite
Reasons:
- 更低的API成本
- 更快的响应速度
- 多模态能力(文本+图像)
- 免费配额充足
```

#### 8.4.2 数据存储
```
PostgreSQL (计划) → JSON File Storage (当前)
Reasons for JSON:
- 快速原型开发
- 无需数据库配置
- 易于版本控制
- 足够支撑MVP阶段

Migration Path:
Phase 1: JSON files (current)
Phase 2: SQLite (growth)
Phase 3: PostgreSQL (scale)
```

## 9. 架构演进

随着项目发展，本文档将持续更新：
- 每月架构评审
- 重大变更时更新
- 性能瓶颈分析后优化

---

## 10. 独立页面架构 (2025-10-01新增)

### 10.1 页面导航架构升级

从**模态窗口模式**升级为**独立页面模式**,改善用户体验和代码可维护性。

#### 10.1.1 架构对比

**改进前 (模态窗口)**:
```python
# 在侧边栏按钮点击后设置session state标志
if st.button("添加订阅"):
    st.session_state.show_add_modal = True

# 在当前页面底部条件渲染模态窗口
if st.session_state.get("show_add_modal"):
    render_add_subscription_modal()  # 内联显示
```

**改进后 (独立页面)**:
```python
# 在侧边栏按钮点击后切换页面
if st.button("添加订阅"):
    st.session_state.current_page = "添加订阅"
    st.rerun()

# 在主路由器中处理页面渲染
def render_main_content():
    if current_page == "添加订阅":
        render_add_subscription_page()  # 完整页面渲染
```

#### 10.1.2 页面路由实现 (app/main.py)

```python
def render_main_content():
    """主内容渲染路由"""
    render_reminder_banner()  # 全局提醒横幅
    current_page = st.session_state.current_page

    # 核心页面路由
    if current_page == "首页":
        render_home_page()
    elif current_page == "数据概览":
        render_dashboard()
    elif current_page == "AI助手":
        render_chat_page()
    elif current_page == "数据分析":
        render_analytics_page()
    elif current_page == "系统设置":
        render_settings_page()

    # 独立功能页面路由 (2025-10-01新增)
    elif current_page == "添加订阅":
        render_add_subscription_page()
    elif current_page == "从模板添加":
        render_template_page()
    elif current_page == "扫描账单":
        render_scan_bill_page()
```

### 10.2 独立页面实现

#### 10.2.1 添加订阅页面 (ui/pages/add_subscription_page.py)

**文件结构:**
```python
"""添加订阅页面 - 独立页面用于添加新订阅"""

def render_add_subscription_page():
    """渲染添加订阅页面"""
    st.title("➕ 添加新订阅")
    st.markdown("填写以下信息以添加新的订阅服务")

    with st.form("add_subscription_form_page"):
        # 表单字段定义
        col1, col2 = st.columns(2)
        with col1:
            service_name = st.text_input("服务名称*")
            price = st.number_input("价格*")
        with col2:
            currency = st.selectbox("币种", ["CNY", "USD", ...])
            billing_cycle = st.selectbox("付费周期*", [...])

        # 表单提交按钮(只能用form_submit_button)
        submitted = st.form_submit_button("✅ 添加订阅")

        if submitted:
            # 数据验证和保存
            result = data_manager.create_subscription(user_id, data)
            if result:
                st.success("✅ 成功添加订阅")
                st.info("💡 可以继续添加或通过左侧菜单查看数据概览")
```

**关键设计点:**
- 独立的页面文件,不依赖其他组件
- 使用 `st.form()` 统一表单提交
- 成功后不使用按钮导航,引导用户使用菜单
- 避免 Streamlit 表单约束问题

#### 10.2.2 模板选择页面 (ui/pages/template_page.py)

**两阶段状态机:**
```python
def render_template_page():
    """模板选择主页面"""
    # 状态1: 显示模板表单
    if st.session_state.get("show_template_form_page", False):
        render_template_form_page()
        return

    # 状态2: 显示模板列表
    # 搜索和筛选
    search_query = st.text_input("🔍 搜索服务", key="template_search_page")
    selected_category = st.selectbox("分类筛选", [...], key="category_select_page")

    # 3列卡片布局
    cols_per_row = 3
    for i in range(0, len(templates), cols_per_row):
        cols = st.columns(cols_per_row)
        for col, (name, template) in zip(cols, templates):
            with col:
                st.markdown(f"### {template['icon']} {name}")
                if st.button("➕ 选择", key=f"select_template_page_{name}"):
                    st.session_state.selected_template_page = name
                    st.session_state.show_template_form_page = True
                    st.rerun()

def render_template_form_page():
    """模板确认表单页面"""
    template = get_template(st.session_state.selected_template_page)
    # 预填充模板数据的表单...
```

**关键特性:**
- 两阶段工作流: 选择 → 确认
- 独立的widget key命名(`_page`后缀)
- 状态管理使用session_state

#### 10.2.3 扫描账单页面 (ui/pages/scan_bill_page.py)

**三步OCR流程:**
```python
def render_scan_bill_page():
    """扫描账单主页面"""
    st.title("📱 扫描账单")

    # 步骤1: 文件上传
    uploaded_file = st.file_uploader("上传账单图片", type=['png', 'jpg', 'jpeg', 'pdf'])

    if uploaded_file:
        # 步骤2: OCR识别
        if st.button("🔍 开始识别"):
            gemini_client = get_gemini_client()
            ocr_result = gemini_client.analyze_bill_image(file_bytes, file_type)
            st.session_state.ocr_result = ocr_result
            st.session_state.ocr_step = "confirm"

        # 步骤2.5: 确认识别结果
        if st.session_state.get("ocr_step") == "confirm":
            st.subheader("📋 识别结果确认")
            st.info(f"识别描述: {ocr_result['description']}")
            if st.button("✅ 确认识别结果"):
                st.session_state.ocr_step = "form"
                st.rerun()

        # 步骤3: 填入表单
        if st.session_state.get("ocr_step") == "form":
            with st.form("ocr_result_form"):
                service_name = st.text_input("服务名称", value=recognized_data.get("service_name"))
                # ... 其他表单字段
                submitted = st.form_submit_button("✅ 添加订阅")
                if submitted:
                    data_manager.create_subscription(user_id, subscription_data)
```

**技术亮点:**
- 使用Gemini 2.5 Flash Lite多模态能力
- 三步状态机: upload → confirm → form
- 支持置信度显示和手动调整
- 错误处理和降级方案

### 10.3 Widget Key 冲突解决

**问题:** 新建独立页面与原有模态组件使用相同的widget key导致冲突

**解决方案:** 统一命名规范
```python
# 原有模态组件 (components/*)
key="template_search"
key="category_select"
key=f"add_template_{service_name}"

# 新建独立页面 (pages/*_page.py)
key="template_search_page"
key="category_select_page"
key=f"select_template_page_{service_name}"
```

### 10.4 Streamlit 表单约束处理

**约束:**
- `st.form()` 内部只能使用 `st.form_submit_button()`
- 不能使用普通 `st.button()` 或其他交互组件

**典型错误:**
```python
with st.form("my_form"):
    submitted = st.form_submit_button("提交")
    if submitted and result:
        # ❌ 错误: 不能在表单内使用button
        if st.button("继续添加"):
            st.rerun()
```

**修复方案:**
```python
with st.form("my_form"):
    submitted = st.form_submit_button("提交")
    if submitted:
        if result:
            st.success("✅ 成功!")
            st.info("💡 可以继续添加订阅,或通过左侧菜单查看数据概览")
            # ✅ 不使用按钮,引导用户使用菜单导航
```

### 10.5 架构优势

**相比模态窗口的改进:**

| 维度 | 模态窗口 | 独立页面 |
|-----|---------|---------|
| 用户体验 | 内容在当前页面下方,不够清晰 | 完整页面切换,边界清晰 |
| 代码组织 | 组件耦合,状态管理复杂 | 页面独立,状态隔离 |
| Widget Key | 易冲突,需要全局唯一 | 页面级隔离,_page后缀 |
| 测试性 | 依赖父组件状态 | 可独立测试 |
| 扩展性 | 难以添加新功能 | 易于扩展和修改 |
| URL路由 | 不支持 | 易于实现深度链接 |

**文档状态**: 活跃更新中
**最后更新**: 2025-10-01
**版本历史**:
- v1.0 - 初始架构设计 - 2025-01
- v1.1 - 添加提醒系统、数据导出、内联编辑架构 - 2025-09-30
- v1.2 - 独立页面架构升级 - 2025-10-01
- v1.3 - AI Agent架构增强 (Phase 2) - 2025-10-01

---

## 11. AI Agent架构增强 (Phase 2 - 2025-10-01)

### 11.1 多Agent系统架构

#### 11.1.1 Agent层次结构

```
ButlerAgent (管家Agent - 中央协调者)
    ├── MonitoringAgent (监控Agent)
    │   ├── 订阅扫描
    │   ├── 异常检测
    │   └── 续费提醒
    │
    ├── OptimizationAgent (优化Agent) ✨ 新增
    │   ├── 成本分析
    │   ├── 省钱机会检测
    │   └── 订阅组合优化
    │
    └── Future Agents
        ├── NegotiationAgent (谈判Agent - 规划中)
        └── RecommendationAgent (推荐Agent - 规划中)
```

#### 11.1.2 OptimizationAgent 架构

**文件**: `core/agents/optimization_agent.py`

```python
class OptimizationAgent(BaseAgent):
    """优化Agent - 分析和优化订阅组合"""

    async def analyze_costs(self, context: AgentContext) -> Dict[str, Any]:
        """
        成本分析功能
        - 总月度支出计算
        - 分类成本分布
        - 付费周期分析
        - 平均订阅成本
        """
        pass

    async def find_savings_opportunities(self, context: AgentContext) -> Dict[str, Any]:
        """
        省钱机会检测
        - 重复服务检测
        - 未使用订阅识别
        - 年付优惠分析 (月付→年付转换)
        - 预算超支警告
        - 高成本订阅标记
        """
        pass

    async def optimize_subscription_portfolio(self, context: AgentContext) -> Dict[str, Any]:
        """
        订阅组合优化
        - 基于使用模式的优化建议
        - 替代方案推荐
        - 成本效益分析
        """
        pass
```

**关键设计点**:
- 独立的分析引擎，不依赖外部AI服务
- 基于规则和算法的优化逻辑
- 可扩展的优化策略框架

### 11.2 Agent活动日志系统

#### 11.2.1 活动日志架构

**文件**: `core/agents/activity_logger.py`

```python
class ActivityType(Enum):
    """活动类型枚举"""
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    DECISION_MADE = "decision_made"
    ACTION_TAKEN = "action_taken"
    ERROR_OCCURRED = "error_occurred"

class AgentActivityLogger:
    """全局活动日志记录器"""

    def log_activity(
        self,
        agent_id: str,
        agent_type: str,
        activity_type: ActivityType,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        status: str = "success"
    ) -> str:
        """记录Agent活动"""
        pass

    def get_activities(
        self,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        activity_type: Optional[ActivityType] = None,
        start_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AgentActivity]:
        """查询活动记录"""
        pass

    def get_activity_stats(
        self,
        user_id: Optional[str] = None,
        time_window: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """获取活动统计"""
        pass
```

#### 11.2.2 BaseAgent集成

**文件**: `core/agents/base_agent.py`

```python
class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self._current_user_id: Optional[str] = None  # 用于活动日志记录

    def log_action(self, action: str, details: Dict[str, Any], status: str = "success"):
        """
        记录Agent动作
        - 同时记录到Python logger
        - 同时记录到活动日志系统
        """
        # Python日志
        self.logger.info(f"Action: {action}", extra=details)

        # 活动日志系统
        activity_logger.log_activity(
            agent_id=self.agent_id,
            agent_type=self.agent_type.value,
            activity_type=ActivityType.ACTION_TAKEN,
            description=action,
            details=details,
            user_id=self._current_user_id,
            status=status
        )
```

### 11.3 每日检查调度系统

#### 11.3.1 调度器架构

**文件**: `core/services/daily_checkup_scheduler.py`

```python
class DailyCheckupScheduler:
    """每日检查调度器 - 基于schedule库"""

    def __init__(self):
        self.butler_agent = ButlerAgent()
        self.is_running = False
        self.last_run_time: Optional[datetime] = None
        self.last_results: Dict[str, Any] = {}

    async def run_daily_checkup_for_user(self, user_id: str) -> Dict[str, Any]:
        """为指定用户运行每日检查"""
        # 获取用户订阅
        # 创建Agent上下文
        # 调用ButlerAgent执行daily_checkup任务
        pass

    def schedule_daily_checkup(self, time_str: str = "09:00"):
        """调度每日检查任务"""
        schedule.every().day.at(time_str).do(job)

    def start_scheduler(self, time_str: str = "09:00"):
        """启动调度器 (后台线程)"""
        self.is_running = True
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)
```

#### 11.3.2 UI集成

**文件**: `ui/pages/automation_settings_page.py`

**配置界面**:
```python
# 每日检查设置
enable_auto_checkup = st.checkbox("启用每日自动检查")
checkup_time = st.time_input("检查时间", value="09:00")

# 调度器状态显示
scheduler_status = daily_checkup_scheduler.get_status()
st.metric("调度器状态", "运行中" if scheduler_status["is_running"] else "已停止")
st.metric("上次检查", last_run_time)
st.metric("下次检查", next_run_time)

# 手动触发
if st.button("▶️ 立即执行检查"):
    result = asyncio.run(
        daily_checkup_scheduler.run_daily_checkup_for_user(user_id)
    )
    st.session_state.daily_checkup_result = result
```

### 11.4 AI洞察仪表板

#### 11.4.1 页面架构

**文件**: `ui/pages/ai_insights_page.py`

**功能模块**:
1. **监控扫描** - MonitoringAgent
   - 扫描所有订阅
   - 检测异常和问题
   - 生成问题列表

2. **成本分析** - OptimizationAgent ✨ 新增
   - 月度总支出
   - 分类成本分布
   - 付费周期分析
   - 成本趋势

3. **省钱建议** - OptimizationAgent ✨ 新增
   - 重复服务检测
   - 年付优惠机会
   - 未使用订阅识别
   - 按优先级排序

4. **每日检查结果**
   - 显示调度器执行的检查结果
   - 行动项建议

**数据流**:
```
用户点击按钮
    ↓
创建AgentContext
    ↓
调用Agent异步方法
    ↓
结果存入session_state
    ↓
UI重新渲染显示结果
```

### 11.5 Agent活动日志页面

**文件**: `ui/pages/agent_activity_page.py`

**功能**:
- 时间范围筛选 (1小时/24小时/7天/30天/全部)
- Agent类型筛选
- 活动类型筛选
- 状态筛选 (success/failed/pending)
- 活动统计概览
- Agent活动分布可视化
- 最近错误列表
- 日志导出 (JSON格式)
- 旧日志清理

### 11.6 架构优势

**Phase 2增强的价值**:

| 维度 | Phase 1 | Phase 2 |
|-----|---------|---------|
| Agent能力 | 监控+对话 | +优化分析 |
| 可观测性 | Python日志 | +活动日志系统+UI查看器 |
| 自动化 | 手动触发 | +定时调度+后台运行 |
| 成本洞察 | 基础统计 | +深度分析+省钱建议 |
| 用户价值 | 管理订阅 | +主动优化+智能建议 |

**技术创新点**:
1. **多Agent协作**: ButlerAgent协调多个专业Agent
2. **活动追踪**: 完整的Agent行为可观测性
3. **后台调度**: 异步任务定时执行
4. **智能优化**: 基于规则的成本优化引擎

### 11.7 编码问题修复

**Windows GBK编码兼容性**:

**问题**: Streamlit在Windows下使用GBK编码，¥符号导致`UnicodeEncodeError`

**解决方案**:
```bash
# 启动命令使用UTF-8环境变量
set PYTHONIOENCODING=utf-8 && streamlit run app/main.py --server.port=8501
```

**影响**:
- 所有包含Unicode字符的输出正常显示
- 支持中文、¥、€等多语言字符
- 跨平台兼容性提升

**文档更新**: 2025-10-01
**Phase**: Phase 2 完成
**版本**: v1.3

---

*此文档定义了AI订阅管家的技术架构基础，是所有技术决策的参考依据。*