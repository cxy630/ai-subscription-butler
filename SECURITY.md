# 🔒 安全指南

## 重要安全提醒

⚠️ **绝不要将以下敏感信息提交到版本控制系统：**

### 🚫 禁止提交的文件类型
- `.env` - 环境变量文件
- `.env.local` - 本地环境配置
- `.env.production` - 生产环境配置
- `secrets/` - 任何密钥目录
- `*.key`, `*.pem` - 密钥文件
- 包含API密钥的任何文件

### 🔑 API密钥安全
```bash
# ✅ 正确做法：使用环境变量
OPENAI_API_KEY=sk-your-actual-key-here

# ❌ 错误做法：硬编码在代码中
openai.api_key = "sk-hardcoded-key"  # 绝对不要这样做！
```

## 🛡️ 保护措施

### 1. `.gitignore` 已配置
项目已正确配置 `.gitignore` 文件，包含所有敏感文件模式。

### 2. 环境变量使用
所有敏感配置都通过环境变量管理：
```python
import os
api_key = os.getenv("OPENAI_API_KEY")  # 安全方式
```

### 3. 配置模板
使用 `.env.example` 作为模板，**绝不包含真实密钥**。

## 📋 安全检查清单

在提交代码前，请确认：

- [ ] 没有硬编码的API密钥
- [ ] `.env` 文件未被添加到Git
- [ ] 代码中没有个人身份信息
- [ ] 没有数据库连接字符串
- [ ] 没有第三方服务凭据

## 🚨 意外泄露处理

如果意外提交了敏感信息：

### 立即措施
1. **撤销最新提交**（如果还未推送）：
```bash
git reset --hard HEAD~1
```

2. **从Git历史中移除**（如果已推送）：
```bash
git filter-branch --force --index-filter \
"git rm --cached --ignore-unmatch path/to/sensitive/file" \
--prune-empty --tag-name-filter cat -- --all
```

3. **重新生成密钥**：
- 立即在OpenAI平台撤销泄露的API密钥
- 生成新的API密钥
- 更新本地环境配置

### 报告流程
如果发现安全问题，请：
1. 不要在公共Issue中讨论安全问题
2. 通过私有方式联系项目维护者
3. 提供问题详细信息和复现步骤

## 🔧 开发最佳实践

### 环境隔离
```bash
# 开发环境
cp .env.example .env.development

# 生产环境
cp .env.example .env.production

# 测试环境
cp .env.example .env.test
```

### 密钥轮换
- 定期更换API密钥（建议每季度）
- 使用不同环境的不同密钥
- 监控API密钥使用情况

### 代码审查
- 每次提交前自检敏感信息
- 使用工具扫描潜在泄露
- 团队成员互相审查

## 📞 联系方式

如有安全相关问题，请通过以下方式联系：
- GitHub Issues（非敏感问题）
- 项目维护者（敏感问题）

---
**记住：安全是每个开发者的责任！** 🛡️