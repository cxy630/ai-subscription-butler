# AI助手添加订阅功能 - 实现文档

## 功能概述

用户可以通过自然语言对话，让AI助手自动识别并添加订阅。

### 用户体验流程

```
用户: "帮我添加Netflix订阅，每月79元"
  ↓
AI助手: [识别] 服务名=Netflix, 价格=79, 周期=monthly
  ↓
系统: [检查重复] 是否已有Netflix订阅？
  ├─ 无重复 → 显示确认卡片
  └─ 有重复 → 提示用户修改名称或取消
  ↓
用户: [点击"确认添加"]
  ↓
系统: ✅ 已添加Netflix订阅
```

## 已完成实现

### 1. 订阅信息提取器 ✅

**文件**: `core/ai/subscription_extractor.py`

**功能**:
- 从用户消息中提取订阅信息
- 支持多种表达方式识别
- 智能推断服务分类
- 检查重复订阅

**示例用法**:
```python
from core.ai.subscription_extractor import SubscriptionExtractor, check_duplicate_subscription

extractor = SubscriptionExtractor()

# 提取订阅信息
info = extractor.extract_subscription_info(
    user_message="帮我添加Netflix订阅，每月79元",
    ai_response=ai_response_text
)

# 检查重复
is_dup, existing = check_duplicate_subscription(
    service_name="Netflix",
    existing_subscriptions=user_subscriptions
)
```

### 2. Gemini Prompt 增强 ✅

**文件**: `core/ai/gemini_client.py` (line 289-346)

**更新内容**:
- 添加订阅添加意图识别指令
- 要求AI返回结构化JSON数据
- 包含字段：intent, service_name, price, currency, billing_cycle, category, confidence

### 3. 待集成到Chat组件

**文件**: `ui/components/chat.py`

需要在 `render_chat_interface()` 函数中添加以下逻辑：

```python
# 在处理AI响应后，检查是否是添加订阅intent
if (send_button or auto_send or enter_pressed) and user_input.strip():
    with st.spinner("🤖 AI助手正在思考..."):
        # 获取AI响应
        ai_response_data = get_ai_response_smart(user_input, user_context)

        # 提取订阅信息
        from core.ai.subscription_extractor import SubscriptionExtractor, check_duplicate_subscription
        extractor = SubscriptionExtractor()

        subscription_info = extractor.extract_subscription_info(
            user_message=user_input,
            ai_response=ai_response_data.get("response", "")
        )

        if subscription_info:
            # 检查重复
            subscriptions = data_manager.get_active_subscriptions(st.session_state.current_user_id)
            is_duplicate, existing_sub = check_duplicate_subscription(
                subscription_info['service_name'],
                subscriptions
            )

            if is_duplicate:
                # 显示重复警告
                st.session_state.pending_subscription = subscription_info
                st.session_state.duplicate_subscription = existing_sub
                st.session_state.show_duplicate_warning = True
            else:
                # 显示确认卡片
                st.session_state.pending_subscription = subscription_info
                st.session_state.show_subscription_confirmation = True

        # 保存对话历史...
```

## UI组件设计

### 1. 确认卡片 (无重复)

```python
if st.session_state.get("show_subscription_confirmation"):
    st.success("✅ AI已识别到订阅信息")

    pending_sub = st.session_state.pending_subscription

    with st.container():
        st.markdown("### ➕ 确认添加订阅")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("服务名称", pending_sub['service_name'])
            st.metric("计费周期", {
                'monthly': '每月',
                'yearly': '每年',
                'weekly': '每周'
            }[pending_sub['billing_cycle']])

        with col2:
            st.metric("价格", f"{pending_sub['currency']} {pending_sub['price']}")
            st.metric("分类", {
                'entertainment': '娱乐',
                'productivity': '生产力',
                'storage': '存储',
                'other': '其他'
            }.get(pending_sub['category'], '其他'))

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("✅ 确认添加", type="primary", use_container_width=True):
                # 添加到数据库
                subscription_id = data_manager.add_subscription(
                    user_id=st.session_state.current_user_id,
                    **pending_sub
                )

                if subscription_id:
                    st.success(f"✅ 已成功添加 {pending_sub['service_name']} 订阅！")
                    del st.session_state.show_subscription_confirmation
                    del st.session_state.pending_subscription
                    st.rerun()
                else:
                    st.error("添加失败，请重试")

        with col_b:
            if st.button("✏️ 修改信息", use_container_width=True):
                st.session_state.editing_subscription = True

        with col_c:
            if st.button("❌ 取消", use_container_width=True):
                del st.session_state.show_subscription_confirmation
                del st.session_state.pending_subscription
                st.rerun()

        # 编辑表单
        if st.session_state.get("editing_subscription"):
            with st.form("edit_subscription_form"):
                pending_sub['service_name'] = st.text_input("服务名称", pending_sub['service_name'])
                pending_sub['price'] = st.number_input("价格", value=pending_sub['price'], min_value=0.0)
                pending_sub['currency'] = st.selectbox("币种", ['CNY', 'USD', 'EUR'],
                                                       index=['CNY', 'USD', 'EUR'].index(pending_sub['currency']))
                pending_sub['billing_cycle'] = st.selectbox("计费周期",
                                                            ['monthly', 'yearly', 'weekly'],
                                                            index=['monthly', 'yearly', 'weekly'].index(pending_sub['billing_cycle']),
                                                            format_func=lambda x: {'monthly': '每月', 'yearly': '每年', 'weekly': '每周'}[x])

                if st.form_submit_button("保存修改"):
                    st.session_state.editing_subscription = False
                    st.rerun()
```

### 2. 重复警告卡片

```python
if st.session_state.get("show_duplicate_warning"):
    st.warning("⚠️ 发现重复订阅")

    pending_sub = st.session_state.pending_subscription
    existing_sub = st.session_state.duplicate_subscription

    with st.container():
        st.markdown("### 🔄 已存在相同订阅")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**要添加的订阅：**")
            st.info(f"""
            - 服务名称: {pending_sub['service_name']}
            - 价格: {pending_sub['currency']} {pending_sub['price']}
            - 周期: {pending_sub['billing_cycle']}
            """)

        with col2:
            st.markdown("**现有订阅：**")
            st.warning(f"""
            - 服务名称: {existing_sub.get('service_name')}
            - 价格: {existing_sub.get('currency')} {existing_sub.get('price')}
            - 周期: {existing_sub.get('billing_cycle')}
            - 状态: {existing_sub.get('status')}
            """)

        st.markdown("---")
        st.markdown("**建议操作：**")
        st.markdown("1. 修改新订阅的名称（例如：Netflix 个人版 / Netflix 家庭版）")
        st.markdown("2. 取消添加，保留现有订阅")
        st.markdown("3. 添加为新订阅（如果确实是不同的账号）")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("✏️ 修改名称", type="primary", use_container_width=True):
                st.session_state.editing_duplicate = True
                del st.session_state.show_duplicate_warning
                st.session_state.show_subscription_confirmation = True
                st.rerun()

        with col_b:
            if st.button("➕ 仍然添加", use_container_width=True):
                del st.session_state.show_duplicate_warning
                st.session_state.show_subscription_confirmation = True
                st.rerun()

        with col_c:
            if st.button("❌ 取消添加", use_container_width=True):
                del st.session_state.show_duplicate_warning
                del st.session_state.pending_subscription
                del st.session_state.duplicate_subscription
                st.rerun()
```

## 测试用例

### 基本添加测试

```python
测试输入：
1. "帮我添加Netflix订阅，每月79元"
2. "我要订阅ChatGPT Plus，每月20美元"
3. "添加百度网盘会员，年费298"
4. "新增爱奇艺，12元/月"

预期结果：
- 正确识别服务名
- 正确提取价格和币种
- 正确识别计费周期
- 正确推断分类
```

### 重复检测测试

```python
场景：用户已有Netflix订阅

测试输入：
"添加Netflix订阅，每月79元"

预期结果：
- 检测到重复
- 显示警告卡片
- 展示现有订阅信息
- 提供修改/取消/继续添加选项
```

### 边界情况测试

```python
测试输入：
1. "添加Netflix"  # 缺少价格
2. "每月79元"  # 缺少服务名
3. "添加一个视频服务，79元"  # 模糊的服务名

预期结果：
- 提取尽可能多的信息
- 缺失字段使用默认值
- 允许用户在确认时修改
```

## 集成步骤

### Step 1: 测试提取器

```bash
cd core/ai
python
>>> from subscription_extractor import SubscriptionExtractor
>>> extractor = SubscriptionExtractor()
>>> info = extractor.extract_subscription_info("帮我添加Netflix，每月79元")
>>> print(info)
```

### Step 2: 更新chat.py

将上述UI组件代码集成到 `ui/components/chat.py` 的适当位置。

### Step 3: 测试完整流程

1. 启动应用
2. 打开AI助手页面
3. 输入 "帮我添加Netflix订阅，每月79元"
4. 验证识别结果
5. 测试确认添加功能
6. 验证订阅已添加到数据库

### Step 4: 测试重复检测

1. 先手动添加一个Netflix订阅
2. 再通过AI添加同名订阅
3. 验证重复警告显示
4. 测试各种操作选项

## 后续优化

1. **支持批量添加**: "帮我添加Netflix和ChatGPT"
2. **支持更新订阅**: "把Netflix的价格改成89元"
3. **支持删除订阅**: "帮我取消爱奇艺"
4. **自然语言时间**: "我上个月订阅的Netflix"
5. **智能建议**: 根据已有订阅推荐相关服务

## 注意事项

1. **隐私保护**: 不要记录敏感支付信息
2. **错误处理**: 优雅处理AI识别失败的情况
3. **用户确认**: 必须经过用户确认才能添加订阅
4. **数据验证**: 后端必须验证所有输入数据
5. **撤销功能**: 提供"撤销上次添加"功能

---

**创建时间**: 2025-10-13
**作者**: Claude Code
**状态**: 🚧 开发中 - 核心逻辑已完成，待UI集成
