# 后续任务清单

**更新日期**: 2025-10-01
**当前版本**: v1.3
**下一目标**: Phase 3 - 高级Agent和自动化

---

## 🎯 Phase 3 任务清单 (优先级顺序)

### 高优先级 - 立即开始

#### 1. NegotiationAgent (谈判Agent) ⭐⭐⭐
**业务价值**: 帮助用户争取优惠价格，实际节省成本
**工作量**: 中等 (3-5天)

**任务分解**:
- [ ] 创建`core/agents/negotiation_agent.py`
  - [ ] 实现`generate_negotiation_strategy()`方法
  - [ ] 实现`draft_contact_message()`方法
  - [ ] 实现`track_negotiation_result()`方法
- [ ] 集成到ButlerAgent
  - [ ] 添加任务路由
  - [ ] 注册到agents字典
- [ ] UI实现
  - [ ] 在订阅详情添加"价格谈判"按钮
  - [ ] 创建谈判策略显示页面
  - [ ] 添加结果追踪界面
- [ ] 活动日志集成
  - [ ] 记录谈判活动
  - [ ] 统计成功率

**技术细节**:
```python
class NegotiationAgent(BaseAgent):
    async def generate_negotiation_strategy(
        self,
        subscription_id: str,
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        生成谈判策略
        Returns: {
            "status": "success",
            "strategy": {
                "leverage_points": [...],  # 谈判筹码
                "talking_points": [...],   # 话术要点
                "target_discount": 0.15,   # 目标折扣
                "alternatives": [...]      # 替代方案
            },
            "draft_message": "..."
        }
        """
        pass
```

---

#### 2. 智能规则引擎增强 ⭐⭐⭐
**业务价值**: 自动化更多场景，减少手动操作
**工作量**: 低 (2-3天)

**任务分解**:
- [ ] 扩展预设规则
  - [ ] 长期未使用自动标记规则
  - [ ] 价格上涨通知规则
  - [ ] 重复功能警告规则
  - [ ] 年付提醒规则
- [ ] 规则执行历史
  - [ ] 创建`core/agents/rule_execution_log.py`
  - [ ] 记录规则触发和结果
  - [ ] 在Agent活动页面显示
- [ ] UI增强
  - [ ] 规则效果统计
  - [ ] 规则启用/禁用快捷开关

**文件**:
- `core/agents/rules_engine.py` (已存在，需扩展)
- `core/agents/rule_execution_log.py` (新建)
- `ui/pages/automation_settings_page.py` (修改)

---

#### 3. 自动化任务增强 ⭐⭐
**业务价值**: 提供更多主动洞察
**工作量**: 低 (1-2天)

**任务分解**:
- [ ] 周度成本报告
  - [ ] 在`DailyCheckupScheduler`添加周度任务
  - [ ] 实现`generate_weekly_report()`方法
  - [ ] 邮件/通知发送
- [ ] 月度优化建议
  - [ ] 实现`generate_monthly_insights()`方法
  - [ ] 年度趋势分析
- [ ] 价格监控
  - [ ] 添加价格历史记录表
  - [ ] 实现价格变化检测
  - [ ] 涨价自动通知

**文件**:
- `core/services/daily_checkup_scheduler.py` (修改)
- `core/services/price_monitor.py` (新建)

---

### 中优先级 - 3周内完成

#### 4. RecommendationAgent (推荐Agent) ⭐⭐
**业务价值**: 主动发现更优服务
**工作量**: 中等 (3-4天)

**任务分解**:
- [ ] 创建`core/agents/recommendation_agent.py`
  - [ ] 实现`recommend_alternatives()`
  - [ ] 实现`analyze_plan_fit()`
  - [ ] 实现`suggest_new_services()`
- [ ] 服务对比数据库
  - [ ] 创建服务对比表
  - [ ] 收集常见服务信息
- [ ] UI实现
  - [ ] 推荐页面
  - [ ] 对比视图

---

#### 5. 数据可视化增强 ⭐⭐
**业务价值**: 更直观的数据展示
**工作量**: 中等 (3-4天)

**任务分解**:
- [ ] Plotly图表集成
  - [ ] 支出趋势折线图
  - [ ] 分类分布饼图
  - [ ] 时间热力图
- [ ] 交互式仪表板
  - [ ] 自定义指标卡片
  - [ ] 图表导出功能
- [ ] 在分析页面集成

**依赖**:
```bash
pip install plotly
```

---

#### 6. 测试覆盖 ⭐⭐⭐
**业务价值**: 提高代码质量和稳定性
**工作量**: 高 (5-7天)

**任务分解**:
- [ ] 单元测试
  - [ ] Agent测试 (目标: 80%覆盖)
  - [ ] 数据层测试
  - [ ] 工具函数测试
- [ ] 集成测试
  - [ ] Agent交互测试
  - [ ] 数据流测试
- [ ] E2E测试
  - [ ] 关键用户流程测试

**工具**:
```bash
pip install pytest pytest-asyncio pytest-cov
```

**测试结构**:
```
tests/
├── unit/
│   ├── agents/
│   │   ├── test_butler_agent.py
│   │   ├── test_optimization_agent.py
│   │   └── test_negotiation_agent.py
│   └── services/
│       └── test_scheduler.py
├── integration/
│   └── test_agent_workflow.py
└── e2e/
    └── test_user_flows.py
```

---

## 🔧 技术债务修复

### 紧急修复
- [ ] 数据库迁移到SQLite/PostgreSQL
  - 当前JSON存储不适合生产
  - 添加事务支持
  - 提升查询性能

### 代码优化
- [ ] 类型注解完善
  - 所有函数添加类型提示
  - 使用mypy检查
- [ ] 错误处理统一
  - 自定义异常类
  - 统一错误响应格式
- [ ] 日志系统完善
  - 结构化日志
  - 日志级别管理
  - 日志轮转

### 文档补充
- [ ] API文档生成
  - 使用Sphinx或MkDocs
  - 自动从代码注释生成
- [ ] 用户手册
  - 功能使用指南
  - 常见问题FAQ
- [ ] 开发者指南
  - 架构说明
  - 贡献指南

---

## 📋 快速参考 - Phase 3核心任务

### Week 1-2: NegotiationAgent + 规则增强
1. Day 1-3: NegotiationAgent核心实现
2. Day 4-5: UI集成和测试
3. Day 6-7: 规则引擎增强

### Week 3: 自动化任务 + RecommendationAgent启动
1. Day 1-2: 周度/月度报告
2. Day 3-4: 价格监控
3. Day 5-7: RecommendationAgent基础

### Week 4: RecommendationAgent + 数据库迁移
1. Day 1-3: RecommendationAgent完成
2. Day 4-7: 数据库迁移准备

---

## ✅ 验收标准

### Phase 3完成标准
- [ ] NegotiationAgent可用，能生成谈判策略
- [ ] 至少5个新的智能规则
- [ ] 周度报告自动发送
- [ ] RecommendationAgent提供3种类型推荐
- [ ] 单元测试覆盖率 >60%
- [ ] 所有新功能有活动日志记录
- [ ] 文档已更新

---

## 📊 进度追踪

### 当前进度
- ✅ Phase 1: 100%
- ✅ Phase 2: 100%
- ⏳ Phase 3: 0%

### 下次检查点
**日期**: 2025-10-15
**目标**: NegotiationAgent完成, 规则增强50%

---

## 🔗 相关文档
- [产品路线图](./roadmap.md)
- [架构文档](./architecture.md)
- [Phase 2完成总结](./phase2-completion-summary.md)
- [需求文档](./requirement.md)

---

**维护者**: 开发团队
**更新频率**: 每周
