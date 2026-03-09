# AI 订阅管家 (AI Subscription Butler)

一款由 AI 驱动的智能订阅管理助手，帮助用户通过自然对话发现、管理和优化订阅服务。

## 🚀 功能特性

### 核心功能
- **🤖 对话式 AI 助手**：基于 Google Gemini 2.5 Flash Lite 的自然语言交互
  - 多轮对话上下文感知
  - 智能订阅发现与管理
  - 自然语言查询与指令

- **📱 智能账单识别 (OCR)**：三步式智能工作流
  - 自动从账单截图识别文本
  - 交互式确认和修正
  - 一键填充已识别数据
  - 支持中英文账单

- **📊 数据分析仪表板**：全方位消费洞察
  - 消费趋势可视化图表
  - 分类统计与深度分析
  - 快速统计卡片（总订阅数、月度费用、活跃服务数）
  - 支持展开查看分类详情

- **🔔 智能提醒系统**：续费不再遗忘
  - 自动计算续费日期（处理月末等边界日期）
  - 优先级通知（紧急/高/中/低）
  - 可自定义提醒时间线（提前7/14/21/28+天）
  - 颜色编码倒计时指示器
  - 提醒统计面板

- **✏️ 智能订阅管理**：
  - 手风琴式内联编辑
  - 订阅与续费日期追踪
  - 按分类组织管理
  - 灵活的筛选与排序
  - 批量操作支持

- **💾 数据导出**：多格式支持
  - CSV 导出（可用于表格分析）
  - JSON 导出（便于数据迁移）

- **🧠 高级 AI Agent 系统 (v1.4)**：主动式订阅管理
  - **优化 Agent**：自动检测重复服务和年付省钱机会
  - **智能规则引擎**：可配置自动化规则，支持一键启用/禁用
    - 续费提醒、闲置订阅检测
    - 涨价警报、预算预警
    - 分类冗余检测、年付转化建议
  - **价格监控**：实时历史价格追踪与涨价检测
  - **省钱战报**：价值导向型首页，实时 AI 活动日志
  - **每周 AI 报告**：自动化周度消费洞察与总结
  - **月度优化建议**：AI 生成的月度消费健康报告

## 🛠️ 技术栈

- **后端**：Python 3.9+
- **前端**：Streamlit
- **AI/ML**：
  - Google Gemini 2.5 Flash Lite（对话与 OCR）
  - 多模态 AI 文本与图像处理
- **数据库**：JSON 文件存储（开发）、SQLite（已就绪）、PostgreSQL（生产计划）
- **部署**：Streamlit Cloud / Docker

## 📦 安装指南

### 前置条件

- Python 3.9 或更高版本
- Git
- Google Gemini API 密钥（可在 https://aistudio.google.com/ 免费获取）

### 快速开始

1. **克隆仓库**
   ```bash
   git clone https://github.com/cxy630/ai-subscription-butler.git
   cd ai-subscription-butler
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量** 🔑
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，添加你的 Google Gemini API 密钥
   # GEMINI_API_KEY=your-api-key-here
   ```

   ⚠️ **安全提醒**：
   - **绝不要**将包含真实 API 密钥的 `.env` 文件提交到 Git
   - 项目已正确配置 `.gitignore` 保护敏感文件
   - 查看 [SECURITY.md](SECURITY.md) 了解完整安全指南

5. **运行应用**
   ```bash
   streamlit run app/main.py --server.port=8501
   ```

访问 `http://localhost:8501` 即可使用。

## 🏗️ 项目结构

```
ai-subscription-butler/
├── app/                    # 应用入口
│   ├── main.py            # Streamlit 主应用（多页面导航）
│   ├── config.py          # 配置管理
│   └── constants.py       # 常量定义
├── core/                  # 核心业务逻辑
│   ├── ai/               # AI 集成层
│   │   ├── assistant.py  # AI 助手编排
│   │   ├── gemini_client.py  # Gemini API 客户端
│   │   └── subscription_extractor.py  # 订阅信息提取
│   ├── agents/           # AI Agent 框架
│   │   ├── butler_agent.py   # 管家 Agent（日检/周报/月报）
│   │   ├── rules_engine.py   # 智能自动化规则引擎
│   │   ├── optimization_agent.py # 成本优化 Agent
│   │   ├── monitoring_agent.py   # 订阅监控 Agent
│   │   ├── negotiation_agent.py  # 谈判 Agent
│   │   └── activity_logger.py    # 活动审计日志
│   ├── database/         # 数据持久化
│   │   ├── json_storage.py    # JSON 文件存储
│   │   ├── sqlite_models.py   # SQLite ORM 模型
│   │   └── data_interface.py  # 统一数据访问层
│   ├── services/         # 业务服务
│   │   ├── reminder_system.py # 续费提醒逻辑
│   │   ├── price_monitor.py   # 历史价格追踪
│   │   └── daily_checkup_scheduler.py # 自动化任务调度
│   └── templates/        # 订阅模板
├── ui/                   # 用户界面
│   ├── pages/            # 页面组件
│   │   ├── home.py               # 省钱战报首页
│   │   ├── analytics_page.py     # 消费分析
│   │   ├── ai_insights_page.py   # AI 洞察面板
│   │   ├── automation_settings_page.py # 规则管理 UI
│   │   └── agent_activity_page.py     # Agent 活动日志
│   └── components/       # 可复用 UI 组件
│       ├── activity_stream.py # 实时 AI 活动流
│       ├── dashboard.py  # 数据分析仪表盘
│       ├── chat.py      # AI 聊天界面
│       ├── reminders.py # 提醒通知组件
│       └── settings.py  # 设置组件
├── tests/               # 测试套件（33 个测试）
│   ├── test_json_storage.py
│   ├── test_openai_client.py
│   └── unit/agents/test_rules_engine.py
├── scripts/             # 工具脚本
│   ├── fix_categories.py          # 批量分类修复
│   └── migrate_json_to_sqlite.py  # 数据库迁移工具
├── docs/               # 项目文档
└── data/               # 数据存储
    ├── subscriptions.json
    ├── users.json
    ├── conversations.json
    └── price_history.json
```

## 📚 文档目录

- [需求分析](docs/requirement.md)
- [技术架构](docs/architecture.md)
- [数据库设计](docs/database.md)
- [UI 设计](docs/ui-design.md)
- [功能总结](docs/feature-summary.md)
- [产品路线图](docs/roadmap.md)
- [安全指南](SECURITY.md)

## 🚀 开发指南

### 开发环境配置

1. **安装开发依赖**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **配置 pre-commit 钩子**
   ```bash
   pre-commit install
   ```

3. **运行测试**
   ```bash
   pytest
   ```

4. **代码格式化**
   ```bash
   black .
   isort .
   flake8
   ```

## 🔧 配置说明

`.env` 中的主要配置项：

```bash
# Google Gemini 配置
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash-lite

# 应用设置
APP_PORT=8501
DEBUG_MODE=false

# 功能开关（默认全部启用）
FEATURE_AI_CHAT=true
FEATURE_OCR=true
FEATURE_ANALYTICS=true
FEATURE_REMINDERS=true
```

## 🤝 参与贡献

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加新功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 📞 联系方式

- **邮箱**：chenxy@fortune-data.com
- **问题反馈**：[GitHub Issues](https://github.com/cxy630/ai-subscription-butler/issues)
- **项目文档**：[docs/](docs/)

## 🎯 路线图

### 已完成 ✅
- ✅ 订阅 CRUD 基础管理
- ✅ AI 对话界面（Gemini 2.5 Flash Lite）
- ✅ OCR 账单识别（三步工作流）
- ✅ 数据分析仪表板（消费趋势）
- ✅ 智能提醒系统（优先级通知）
- ✅ 数据导出（CSV、JSON）
- ✅ 内联编辑与手风琴 UI
- ✅ 分类管理与组织
- ✅ **规则引擎**：重复检测、年付优化、涨价警报、预算预警
- ✅ **省钱战报**：价值导向首页重构
- ✅ **智能规则引擎**：可配置规则 + UI 切换 + 执行日志
- ✅ **价格监控**：历史价格追踪与涨价检测
- ✅ **每周 AI 报告**：基于真实价格数据的自动化消费总结
- ✅ **月度优化洞察**：AI 生成月度消费健康报告
- ✅ **SQLite 后端**：完整 ORM 模型与迁移脚本就绪
- ✅ **33 个单元测试**：核心模块全面测试覆盖

### 进行中 🔄
- 🔄 数据库迁移（JSON → SQLite/PostgreSQL）
- 🔄 邮件/短信通知集成
- 🔄 批量操作优化

### 计划中 📅
- 📅 谈判 Agent 增强
- 📅 多渠道消息推送（Server酱 / 钉钉 / 邮件）
- 📅 数据备份与恢复
- 📅 多用户与家庭共享
- 📅 移动端响应式设计
- 📅 订阅推荐系统

## 🏆 成功指标

- **用户满意度**：> 4.5/5
- **成本节省**：> ¥50/用户/月
- **响应时间**：< 2 秒
- **OCR 准确率**：> 85%

---

**用 ❤️ 构建**

*最后更新：2026-03-09*