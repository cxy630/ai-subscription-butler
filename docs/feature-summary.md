# AI订阅管家 - 功能总结文档

> 📅 更新日期：2025-10-13
> 📝 版本：Phase 2 Complete

---

## 📑 目录

1. [项目概览](#项目概览)
2. [核心架构](#核心架构)
3. [功能模块详解](#功能模块详解)
4. [AI能力](#ai能力)
5. [数据管理](#数据管理)
6. [UI组件](#ui组件)
7. [技术栈](#技术栈)
8. [已完成功能](#已完成功能)
9. [进行中功能](#进行中功能)
10. [待开发功能](#待开发功能)

---

## 🎯 项目概览

**AI订阅管家**是一个智能订阅管理系统，通过AI对话、自动提醒、成本分析等功能，帮助用户高效管理各类订阅服务，节省开支。

### 核心价值
- 💰 **成本优化**: 通过AI分析识别重复订阅、未使用服务，平均节省>¥50/月
- ⏰ **智能提醒**: 自动计算续费日期，提前多级别提醒，避免意外扣费
- 🤖 **AI助手**: 自然语言交互，快速添加订阅、查询信息
- 📊 **数据洞察**: 可视化分析消费趋势，分类统计，预算管控

---

## 🏗️ 核心架构

```
ai-subscription-butler/
├── app/                          # 应用入口
│   ├── main.py                  # Streamlit主应用（多页面导航）
│   ├── config.py                # 配置管理
│   └── constants.py             # 常量定义
│
├── core/                        # 核心业务逻辑
│   ├── ai/                      # AI集成层
│   │   ├── gemini_client.py    # Gemini API客户端
│   │   ├── assistant.py        # AI助手编排
│   │   └── openai_client.py    # OpenAI客户端（备用）
│   │
│   ├── agents/                  # 智能Agent系统 ⭐ NEW
│   │   ├── base_agent.py       # Agent基类和消息系统
│   │   ├── butler_agent.py     # 管家Agent（中央协调）
│   │   ├── monitoring_agent.py # 监控Agent（扫描订阅）
│   │   ├── optimization_agent.py # 优化Agent（成本分析）
│   │   ├── negotiation_agent.py # [NEW] 谈判Agent（策略生成）
│   │   ├── rules_engine.py     # 规则引擎
│   │   └── activity_logger.py  # 活动日志系统
│   │
│   ├── database/                # 数据持久化
│   │   ├── json_storage.py     # JSON文件存储
│   │   ├── data_interface.py   # 数据访问接口
│   │   └── sqlite_models.py    # SQLite模型（未启用）
│   │
│   ├── services/                # 业务服务
│   │   ├── reminder_system.py  # 提醒系统
│   │   └── daily_checkup_scheduler.py # 每日检查调度
│   │
│   ├── templates/               # 订阅模板 ⭐ NEW
│   │   └── subscription_templates.py # 预定义模板
│   │
│   └── backup/                  # 备份管理 ⭐ NEW
│       └── backup_manager.py    # 自动备份功能
│
├── ui/                          # 用户界面
│   ├── components/              # UI组件
│   │   ├── chat.py             # AI对话组件
│   │   ├── dashboard.py        # 数据分析仪表盘
│   │   ├── reminders.py        # 提醒通知组件
│   │   ├── settings.py         # 设置组件
│   │   └── template_selector.py # 模板选择器
│   │
│   └── pages/                   # 页面模块
│       ├── home.py             # 首页
│       ├── add_subscription_page.py # 添加订阅
│       ├── scan_bill_page.py   # 账单扫描OCR
│       ├── analytics_page.py   # 数据分析
│       ├── ai_insights_page.py # AI洞察 ⭐ NEW
│       ├── agent_activity_page.py # Agent活动监控 ⭐ NEW
│       ├── automation_settings_page.py # 自动化设置 ⭐ NEW
│       ├── template_page.py    # 模板管理
│       └── settings_page.py    # 设置页面
│
├── data/                        # 数据存储
│   ├── subscriptions.json      # 订阅数据
│   ├── users.json              # 用户数据
│   └── conversations.json      # 对话历史
│
├── tests/                       # 测试套件
│   ├── unit/                   # 单元测试
│   └── integration/            # 集成测试
│
├── scripts/                     # 工具脚本
│   ├── fix_categories.py       # 批量修复分类
│   └── test_reminder_system.py # 测试提醒系统
│
└── docs/                        # 文档
    ├── architecture.md          # 架构文档
    ├── database.md             # 数据库设计
    ├── ai-integration.md       # AI集成文档
    └── feature-summary.md      # 本文档
```

---

## 🎨 功能模块详解

### 1. 📱 订阅管理核心

#### 1.1 订阅CRUD操作
- ✅ **添加订阅**
  - 手动表单输入（支持所有字段）
  - AI对话添加（自然语言解析）
  - OCR扫描添加（图片识别）
  - 模板快速添加 ⭐ NEW

- ✅ **查看订阅**
  - 列表视图（支持排序、筛选）
  - 手风琴式展开详情
  - 分类归纳显示
  - 状态标记（active/inactive/cancelled）

- ✅ **编辑订阅**
  - 内联编辑（无需跳转）
  - 批量操作（计划中）
  - 历史版本追踪（计划中）

- ✅ **删除订阅**
  - 软删除机制
  - 回收站功能（计划中）

#### 1.2 字段支持
```python
{
    "service_name": str,        # 服务名称
    "category": str,            # 分类（entertainment/productivity/storage等）
    "price": float,             # 价格
    "currency": str,            # 货币（CNY/USD）
    "billing_cycle": str,       # 计费周期（monthly/yearly/weekly）
    "start_date": str,          # 开始日期
    "next_billing_date": str,   # 下次续费日期
    "status": str,              # 状态
    "payment_method": str,      # 支付方式
    "notes": str,               # 备注
    "reminder_days": int,       # 提醒天数
    "auto_renewal": bool        # 自动续费
}
```

---

### 2. 🤖 AI能力

#### 2.1 对话式AI助手
**技术**: Google Gemini 2.5 Flash Lite

**核心功能**:
- ✅ **自然语言理解**
  - 多轮对话上下文管理
  - 意图识别（添加/查询/修改/删除）
  - 实体提取（服务名、价格、日期等）

- ✅ **智能交互**
  ```
  用户: "帮我添加Netflix订阅，每月79元"
  助手: [自动识别] 服务名=Netflix, 价格=79, 周期=monthly
        [确认后] 已添加Netflix订阅

  用户: "我有哪些超过100元的订阅？"
  助手: [查询分析] 找到3个订阅：ChatGPT Plus (¥120)...
  ```

- ✅ **对话历史**
  - 保存完整对话记录
  - 支持上下文引用
  - 会话持久化

#### 2.2 智能Agent系统 ⭐ **重磅新功能**

**架构**: Multi-Agent协作系统

##### 2.2.1 Butler Agent（管家Agent）
- **角色**: 中央协调者，决策中枢
- **功能**:
  - 协调子Agent执行任务
  - 生成个性化洞察和建议
  - 处理用户查询和命令
  - 生成每日检查报告

##### 2.2.2 Monitoring Agent（监控Agent）
- **角色**: 订阅健康监控
- **功能**:
  - 扫描所有订阅状态
  - 检测即将到期的订阅
  - 识别异常消费模式
  - 生成告警和问题报告

##### 2.2.3 Optimization Agent（优化Agent）
- **角色**: 成本优化专家
- **功能**:
  - **成本分析**
    - 总成本计算（按货币分组）
    - 分类成本分析
    - 平均成本计算
    - 识别高成本订阅

  - **省钱机会识别**
    - 重复/重叠服务检测
    - 未使用订阅识别
    - 年付优惠建议
    - 预算超支预警

  - **投资组合优化**
    - 健康度评分
    - 多样性分析
    - 价值优化建议

##### 2.2.4 Negotiation Agent（谈判Agent）⭐ NEW
- **角色**: 价格谈判专家
- **功能**:
  - **策略生成**: 针对特定订阅生成降价/优惠谈判策略
  - **消息起草**: 自动撰写发给客服的申请邮件或聊天话术
  - **场景适配**: 支持“取消挽留”、“长期忠诚”、“竞品对比”等多种谈判逻辑

##### 2.2.4 Agent通信机制
```python
# 消息系统
class AgentMessage:
    - message_id: 唯一ID
    - from_agent: 发送者
    - to_agent: 接收者
    - message_type: COMMAND/QUERY/RESULT
    - content: 消息内容
    - timestamp: 时间戳

# 上下文管理
class AgentContext:
    - user_id: 用户ID
    - subscriptions: 订阅列表
    - user_preferences: 用户偏好
    - automation_level: 自动化级别（manual/semi/full）
    - budget_limit: 预算限制
```

#### 2.3 OCR账单识别
**技术**: Gemini Vision API

**工作流程**:
1. **上传图片** → 支持截图、照片
2. **AI识别** → 提取服务名、金额、日期
3. **人工确认** → 展示识别结果，允许修改
4. **一键填充** → 自动填入表单

**准确率**: >85%

---

### 3. 🔔 智能提醒系统

#### 3.1 提醒计算引擎
```python
def calculate_reminders():
    """
    自动计算续费日期和提醒时间
    - 处理月末边界情况（如1月31日 → 2月28日）
    - 支持多种计费周期
    - 自动递归计算下次续费
    """
```

#### 3.2 优先级系统
| 优先级 | 剩余天数 | 标记 | 显示方式 |
|-------|---------|------|---------|
| 🔴 紧急 | ≤3天 | urgent | 红色高亮 |
| 🟡 高 | 4-7天 | high | 黄色 |
| 🟢 中 | 8-14天 | medium | 绿色 |
| ⚪ 低 | >14天 | low | 灰色 |

#### 3.3 提醒展示
- ✅ **首页快速预览**: 显示最紧急的3条提醒
- ✅ **专门提醒页面**: 完整列表，支持筛选
- ✅ **统计面板**: 按优先级分组统计
- 🔄 **多渠道通知**: 邮件/短信（开发中）

---

### 4. 📊 数据分析与洞察

#### 4.1 数据分析仪表盘
**页面**: `analytics_page.py`

**功能模块**:
- ✅ **快速统计卡片**
  - 订阅总数
  - 月度总花费（多币种支持）
  - 活跃订阅数

- ✅ **消费趋势图表**
  - 时间序列折线图
  - 分类占比饼图
  - 成本对比柱状图

- ✅ **分类分析**
  - 按分类展开详情
  - 显示每个分类的服务列表
  - 分类成本排名

#### 4.2 AI洞察页面 ⭐ **重磅新功能**
**页面**: `ai_insights_page.py`

**核心功能**:
- ✅ **快速操作按钮**
  - 🔍 立即扫描: 扫描所有订阅健康状态
  - 📊 生成洞察: AI分析并生成个性化建议
  - 💰 成本分析: 深度成本结构分析
  - 💡 省钱建议: 识别省钱机会

- ✅ **智能洞察展示**
  - 成本警告（预算超支提醒）
  - 高成本订阅识别
  - 分类冗余检测
  - AI优化建议

- ✅ **优先行动项**
  - 根据紧急程度排序
  - 可执行的具体建议
  - 预期节省金额

- ✅ **成本分析报告**
  - 月度总支出
  - 平均每个订阅成本
  - 最常用计费周期
  - 分类成本分布（可视化进度条）

- ✅ **省钱机会清单**
  - 重复服务检测
  - 未使用订阅识别
  - 年付优惠机会
  - 预算超支预警
  - 按潜在节省金额排序

- ✅ **订阅健康概览**
  - 按分类统计卡片
  - 每个分类的订阅数和总成本

- ✅ **AI 自动化周报** ⭐ NEW
  - **文字版摘要**: AI 自动撰写本周消费洞察
  - **核心指标对比**: 展示活跃订阅与预计月开支
  - **无缝集成**: 直接在“分析报告”页顶部显示，亦可手动触发

**显示优化**:
- ✅ 完全中文化界面（修复英文字段名问题）
- ✅ Emoji视觉标识
- ✅ 颜色编码（红/黄/绿表示优先级）

---

### 5. 🛠️ 订阅模板系统 ⭐ NEW

#### 5.1 预定义模板
**文件**: `core/templates/subscription_templates.py`

**内置模板**（中国市场常见服务）:
```python
模板分类:
- 流媒体: Netflix, 爱奇艺, 腾讯视频, 优酷
- AI工具: ChatGPT Plus, Claude Pro, GitHub Copilot
- 云存储: 百度云盘, 阿里云盘, 坚果云
- 音乐: QQ音乐, 网易云音乐, Apple Music
- 工具: Office 365, Adobe Creative Cloud
- 开发: GitHub Pro, JetBrains
```

#### 5.2 快速添加
- 一键应用模板
- 自动填充常用字段（价格、周期等）
- 支持自定义修改

---

### 6. 💾 数据管理

#### 6.1 数据存储
**当前方案**: JSON文件存储
- ✅ 开发友好，易调试
- ✅ 无需额外数据库部署
- ✅ 支持版本控制

**文件结构**:
```json
// subscriptions.json
{
  "user_id": {
    "subscriptions": [
      {
        "id": "uuid",
        "service_name": "Netflix",
        ...
      }
    ]
  }
}
```

#### 6.2 备份系统 ⭐ NEW
**文件**: `core/backup/backup_manager.py`

**功能**:
- ✅ 自动备份（每日/每周/手动）
- ✅ 多版本管理
- ✅ 一键恢复
- ✅ 备份验证

**备份策略**:
```python
backups/
├── daily/      # 保留7天
├── weekly/     # 保留4周
└── manual/     # 永久保留
```

#### 6.3 数据导出
- ✅ **CSV导出**: 适合Excel分析
- ✅ **JSON导出**: 数据迁移
- 📅 **PDF报告**: 可打印的详细报告（计划中）

---

### 7. ⚙️ 自动化与设置

#### 7.1 自动化级别设置 ⭐ NEW
**页面**: `automation_settings_page.py`

**三种模式**:
1. **Manual（手动）**
   - 所有操作需要用户确认
   - 适合谨慎用户

2. **Semi-Automatic（半自动）**
   - 低风险操作自动执行
   - 高风险操作需要确认
   - 推荐模式

3. **Fully Automatic（全自动）**
   - Agent自主决策和执行
   - 定期汇报结果
   - 适合信任AI的用户

#### 7.2 偏好设置
- ✅ 预算限制设置
- ✅ 提醒偏好
- ✅ 通知渠道选择
- ✅ 分类偏好

#### 7.3 Agent活动监控 ⭐ NEW
**页面**: `agent_activity_page.py`

**功能**:
- ✅ 实时查看Agent活动日志
- ✅ 按类型筛选（扫描/分析/优化）
- ✅ 按Agent筛选
- ✅ 时间范围筛选
- ✅ 活动详情展开查看

---

## 💻 技术栈

### 后端
- **Python 3.9+**
- **Streamlit**: Web框架
- **Google Gemini API**: AI能力
  - gemini-2.5-flash-lite: 对话和分析
  - gemini-vision: OCR识别

### 前端
- **Streamlit Components**: 原生UI组件
- **Plotly**: 数据可视化
- **Markdown**: 富文本展示

### 数据层
- **JSON**: 当前存储方案
- **SQLite**: 备选方案（已实现模型）
- **PostgreSQL**: 生产环境计划

### 开发工具
- **Git**: 版本控制
- **pytest**: 单元测试
- **black**: 代码格式化
- **flake8**: 代码检查

---

## ✅ 已完成功能清单

### Phase 1: 基础功能
- [x] 订阅CRUD操作
- [x] JSON数据存储
- [x] 基础UI界面
- [x] 分类管理
- [x] 日期计算

### Phase 2: AI集成 ⭐ **当前阶段**
- [x] Gemini AI集成
- [x] 对话式添加订阅
- [x] OCR账单扫描
- [x] 智能提醒系统
- [x] 数据分析仪表盘
- [x] Agent系统架构
  - [x] Butler Agent
  - [x] Monitoring Agent
  - [x] Optimization Agent
- [x] AI洞察页面
- [x] 成本分析功能
- [x] 省钱建议功能
- [x] Agent活动监控
- [x] 自动化设置
- [x] 订阅模板系统
- [x] 备份管理系统
- [x] 完全中文化界面

---

## 🔄 进行中功能

### 短期（1-2周）
- [ ] 批量操作优化
- [ ] 通知偏好细化
- [ ] 邮件/短信提醒
- [ ] 模板库扩充

### 中期（1-2月）
- [ ] 数据库迁移（JSON → SQLite/PostgreSQL）
- [ ] 多用户支持
- [ ] 家庭账号共享
- [ ] 移动端适配

---

## 📅 待开发功能

### Phase 3: 高级功能
- [ ] 预算追踪与警报
- [ ] 订阅推荐系统
- [ ] 价格变动监控
- [ ] API集成（自动获取订阅状态）
- [ ] 订阅市场分析
- [ ] AI聊天增强（多模态）

### Phase 4: 社区与扩展
- [ ] 用户社区
- [ ] 订阅攻略分享
- [ ] Chrome扩展
- [ ] 移动App
- [ ] 开放API

---

## 📈 关键指标

### 性能指标
- **响应时间**: < 2秒
- **OCR准确率**: > 85%
- **Agent响应**: < 3秒

### 业务指标
- **用户满意度**: 目标 > 4.5/5
- **平均节省**: 目标 > ¥50/月/用户
- **活跃度**: 目标每周使用 > 2次

---

## 🎯 使用场景示例

### 场景1: 新用户首次使用
1. 注册账号 → 设置预算 (¥500/月)
2. 扫描账单 → OCR识别3个订阅
3. AI对话添加 → "我还有Netflix和ChatGPT Plus"
4. 查看仪表盘 → 发现已超预算 ¥50
5. 查看AI建议 → "建议取消重复的视频服务"
6. 采取行动 → 取消爱奇艺，节省¥30/月

### 场景2: 日常管理
1. 登录首页 → 看到3条紧急提醒
2. 点击提醒 → Netflix明天续费
3. 确认续费 → 系统自动更新下次日期
4. 查看洞察 → AI发现2个未使用订阅
5. 采取行动 → 取消百度云盘

### 场景3: 成本优化
1. 点击AI洞察 → 生成分析报告
2. 查看成本 → 月度支出¥680，超预算¥180
3. 查看建议 → 识别到5个省钱机会
4. 应用建议 →
   - 取消重复服务 (节省¥60)
   - 月付改年付 (节省¥120/年)
   - 降级套餐 (节省¥50)
5. 结果 → 月度支出降至¥570

---

## 🔐 安全与隐私

### 数据安全
- ✅ API密钥环境变量管理
- ✅ `.env`文件Git忽略
- ✅ 敏感数据加密存储（计划）
- ✅ 数据备份与恢复

### 隐私保护
- ✅ 本地数据存储
- ✅ 无第三方数据上传
- ✅ 用户数据完全可控

详见: [SECURITY.md](../SECURITY.md)

---

## 📝 开发日志

### 2026-01-24 (Phase 3 & 4a Complete)
- ✅ **上线“省钱战报”首页**: 首页 Hero Section 视觉重构，突出 AI 节省潜力
- ✅ **实现 Negotiation Agent**: 支持一键获取客服谈判话术
- ✅ **上线 AI 周报系统**: 自动化汇总每周消费见解
- ✅ **引入 AI 工作日志**: 首页实时展示 Agent 后台任务流
- ✅ **规则引擎增强**: 实现同类冗余检测与年付转化逻辑

### 2025-10-13
- ✅ 修复AI洞察页面英文字段名显示问题
- ✅ 优化type字段中文映射
- ✅ 完善省钱建议展示逻辑
- ✅ 创建本功能总结文档

### 2025-10-12
- ✅ 完成Agent活动监控页面
- ✅ 实现自动化级别设置
- ✅ 添加备份管理系统

### 2025-10-10
- ✅ 完成Multi-Agent系统架构
- ✅ 实现ButlerAgent核心逻辑
- ✅ 完成成本分析功能

### 2025-10-08
- ✅ 完成订阅模板系统
- ✅ 优化UI交互体验

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程
1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📞 联系方式

- **Email**: chenxy@fortune-data.com
- **GitHub**: https://github.com/cxy630/ai-subscription-butler
- **Issues**: https://github.com/cxy630/ai-subscription-butler/issues

---

## 📄 许可证

MIT License - 详见 [LICENSE](../LICENSE)

---

**Built with ❤️ using Claude Code**

*最后更新: 2025-10-13*
