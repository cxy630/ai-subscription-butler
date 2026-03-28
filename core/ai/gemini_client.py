"""
Gemini AI客户端 - 使用Google Gemini 2.0 Flash进行AI对话和OCR
"""

import os
import re
import html
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json


class RateLimiter:
    """速率限制器"""

    def __init__(self, max_requests: int = 15, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    def is_allowed(self, user_id: str) -> bool:
        """检查是否允许请求"""
        now = time.time()
        window_start = now - self.window_seconds

        if user_id not in self.requests:
            self.requests[user_id] = []

        # 清理过期请求
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > window_start
        ]

        # 检查是否超过限制
        if len(self.requests[user_id]) >= self.max_requests:
            return False

        # 记录新请求
        self.requests[user_id].append(now)
        return True

    def get_reset_time(self, user_id: str) -> float:
        """获取重置时间"""
        if user_id not in self.requests or not self.requests[user_id]:
            return 0

        oldest_request = min(self.requests[user_id])
        reset_time = oldest_request + self.window_seconds - time.time()
        return max(0, reset_time)


class GeminiClient:
    """Gemini AI客户端"""

    def __init__(self, api_key: str = None, model_name: str = None):
        """初始化Gemini客户端"""
        # 获取API密钥
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到Gemini API密钥。请设置GEMINI_API_KEY环境变量或传入api_key参数。")

        # 初始化日志
        self.logger = logging.getLogger(__name__)

        # 配置Gemini
        genai.configure(api_key=self.api_key)

        # 模型配置
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.max_message_length = 2000
        self.max_context_length = 8000

        # 初始化模型
        self._init_model()

        # 速率限制器 (Gemini Free: 15 RPM)
        self.rate_limiter = RateLimiter(max_requests=15, window_seconds=60)

        # 日志记录
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # 线程池用于异步操作
        self.executor = ThreadPoolExecutor(max_workers=3)

    def _init_model(self):
        """初始化模型"""
        try:
            # 安全设置
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

            # 生成配置
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 1000,
            }

            # 创建模型
            try:
                self.model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                self.logger.info(f"Gemini模型 {self.model_name} 初始化成功")
            except Exception as model_error:
                # 如果模型不存在，尝试使用备用模型
                self.logger.warning(f"模型 {self.model_name} 初始化失败: {model_error}")
                # 尝试多个备用模型
                fallback_models = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro"]
                model_initialized = False
                
                for fallback_model in fallback_models:
                    try:
                        self.logger.info(f"尝试使用备用模型: {fallback_model}")
                        self.model = genai.GenerativeModel(
                            model_name=fallback_model,
                            generation_config=generation_config,
                            safety_settings=safety_settings
                        )
                        self.model_name = fallback_model
                        self.logger.info(f"备用模型 {fallback_model} 初始化成功")
                        model_initialized = True
                        break
                    except Exception as fallback_error:
                        self.logger.warning(f"备用模型 {fallback_model} 也失败: {fallback_error}")
                        continue
                
                if not model_initialized:
                    self.logger.error(f"所有模型初始化失败，将使用降级响应")
                    self.model = None

        except Exception as e:
            self.logger.error(f"Gemini模型初始化失败: {e}", exc_info=True)
            # 不抛出异常，允许使用降级响应
            self.model = None

    def _validate_user_input(self, user_message: str) -> bool:
        """验证用户输入"""
        if not user_message or not user_message.strip():
            return False

        # 长度检查
        if len(user_message) > self.max_message_length:
            self.logger.warning(f"消息过长: {len(user_message)} > {self.max_message_length}")
            return False

        # 检查恶意内容
        malicious_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS
            r'javascript:',  # JavaScript注入
            r'SELECT.*FROM.*',  # SQL注入
            r'DROP\s+TABLE',  # SQL删除
            r'INSERT\s+INTO',  # SQL插入
            r'eval\s*\(',  # 代码执行
        ]

        for pattern in malicious_patterns:
            if re.search(pattern, user_message, re.IGNORECASE):
                self.logger.warning(f"检测到可疑内容: {pattern}")
                return False

        # 检查过多重复字符
        if re.search(r'(.)\1{50,}', user_message):
            self.logger.warning("检测到过多重复字符")
            return False

        return True

    def _sanitize_input(self, user_message: str) -> str:
        """清理用户输入"""
        # HTML转义
        sanitized = html.escape(user_message)

        # 移除多余的空白字符
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()

        # 限制长度
        if len(sanitized) > self.max_message_length:
            sanitized = sanitized[:self.max_message_length] + "..."

        # 记录清理操作
        if sanitized != user_message:
            self.logger.info("用户输入已清理")

        return sanitized

    def _build_context_string(self, user_context: Dict[str, Any]) -> str:
        """构建上下文字符串"""
        context_parts = []

        # 用户基本信息
        monthly_spending = user_context.get("monthly_spending", 0)
        context_parts.append(f"月度支出: CNY {monthly_spending:.2f}")

        # 订阅信息
        total_subscriptions = user_context.get("total_subscriptions", 0)
        active_subscriptions = user_context.get("active_subscriptions", 0)

        if total_subscriptions > 0:
            context_parts.append(f"订阅总数: {total_subscriptions}")
            context_parts.append(f"活跃订阅: {active_subscriptions}")

            # 从数据库获取实际的订阅列表
            user_id = user_context.get("user", {}).get("id")
            if user_id:
                try:
                    from core.database.data_interface import data_manager
                    subscriptions = data_manager.get_active_subscriptions(user_id)
                    if subscriptions:
                        context_parts.append(f"订阅详情(共{len(subscriptions)}个):")
                        # 显示所有订阅,不限制数量
                        for sub in subscriptions:
                            service_name = sub.get("service_name", "未知服务")
                            price = sub.get("price", 0)
                            currency = sub.get("currency", "CNY")
                            billing_cycle = sub.get("billing_cycle", "monthly")
                            category = sub.get("category", "未分类")
                            context_parts.append(f"  - {service_name}: {currency} {price}/{billing_cycle} [{category}]")
                except Exception as e:
                    self.logger.warning(f"获取订阅详情失败: {e}")
                    context_parts.append("  - 无法获取详细订阅信息")

        # 分类统计
        categories = user_context.get("subscription_categories", {})
        if categories:
            context_parts.append("分类统计:")
            for category, stats in categories.items():
                count = stats.get("count", 0)
                spending = stats.get("spending", 0)
                context_parts.append(f"  - {category}: {count}个服务, CNY {spending:.2f}/月")

        context_str = "\n".join(context_parts)

        # 限制上下文长度
        if len(context_str) > self.max_context_length:
            context_str = context_str[:self.max_context_length] + "..."

        return context_str

    def _analyze_intent(self, user_message: str) -> str:
        """分析用户意图"""
        message_lower = user_message.lower()

        # 定义意图关键词（中英文）
        intent_keywords = {
            "spending_query": ["花费", "支出", "钱", "费用", "成本", "多少", "spend", "spending", "cost", "money", "much", "expense"],
            "subscription_count": ["多少", "几个", "数量", "订阅", "how many", "count", "number", "subscription"],
            "cancel_request": ["取消", "停止", "删除", "退订", "cancel", "stop", "delete", "unsubscribe"],
            "optimization_advice": ["节省", "省钱", "优化", "建议", "推荐", "save", "optimize", "advice", "recommend", "suggestion"],
            "add_subscription": ["添加", "新增", "订阅", "add", "new", "create", "subscription"],
            "category_analysis": ["分类", "类别", "分析", "category", "analyze", "analysis"],
            "trend_analysis": ["趋势", "变化", "预测", "trend", "change", "forecast", "predict"],
            "general_help": ["帮助", "怎么", "如何", "什么", "help", "how", "what", "guide"]
        }

        # 匹配意图
        for intent, keywords in intent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return "general_query"

    def get_ai_response_sync(self, user_message: str, user_context: Dict[str, Any] = None, user_id: str = "default") -> Dict[str, Any]:
        """同步获取AI响应"""
        start_time = time.time()

        try:
            # 输入验证
            if not self._validate_user_input(user_message):
                return {
                    "response": "抱歉，您的输入包含不当内容或格式有误，请重新输入。",
                    "intent": "validation_error",
                    "confidence": 0.0,
                    "tokens_used": 0,
                    "response_time": time.time() - start_time,
                    "model": "gemini-validation"
                }

            # 速率限制检查
            if not self.rate_limiter.is_allowed(user_id):
                reset_time = self.rate_limiter.get_reset_time(user_id)
                return {
                    "response": f"请求过于频繁，请等待 {reset_time:.0f} 秒后再试。",
                    "intent": "rate_limit",
                    "confidence": 0.0,
                    "tokens_used": 0,
                    "response_time": time.time() - start_time,
                    "reset_time": reset_time,
                    "model": "gemini-rate-limit"
                }

            # 清理输入
            sanitized_message = self._sanitize_input(user_message)

            # 构建上下文
            context_str = ""
            if user_context:
                context_str = self._build_context_string(user_context)

            # 构建提示词
            system_prompt = """你是一个专业的AI订阅管家助手，专门帮助用户管理和优化他们的订阅服务。

你的主要职责：
1. 帮助用户分析订阅支出
2. 提供订阅优化建议
3. 回答关于订阅管理的问题
4. **识别并提取订阅添加请求**
5. 提供友好、专业的建议

**重要交互原则**：
- **不要主动给出完整的订阅概览和优化建议**
- 只回答用户明确问到的问题
- 如果用户询问概览性问题，可以询问"需要我详细分析吗？"
- 保持简洁，针对性回答

**订阅添加处理**：
当用户说"添加XX订阅"、"帮我加XX"、"我要订阅XX"、"X月X日买的XX"等时：
1. 从用户消息中提取以下信息：
   - service_name: 服务名称
   - price: 价格（数字）
   - currency: 币种（CNY/USD/EUR等）
   - billing_cycle: 计费周期（monthly/yearly/weekly/daily）
   - start_date: 订阅日期（YYYY-MM-DD格式，从用户描述中提取，如"10月11日"→"2025-10-11"）
   - category: 服务分类（entertainment/productivity/storage/business/education/health/other）

2. **重要：多年订阅处理**
   - 如果用户说"3年"、"两年"等，billing_cycle应为"yearly"，并在notes中注明总年限
   - 例如："99元三年" → price: 99, billing_cycle: "yearly", notes: "3年订阅，总价99元"

3. **日期提取规则**：
   - "10月11日" → "2025-10-11"（当年）
   - "昨天" → 昨天的日期
   - "上周" → 上周今天的日期
   - 没有提及日期 → 使用今天的日期

4. 用友好的方式确认识别到的信息
5. 在回复末尾添加JSON格式的结构化数据（使用代码块包裹）

**JSON格式要求**：
在回复末尾添加包含以上所有字段的JSON对象，用代码块包裹。

**重要输出格式要求**：
- 使用友好的语气和适当的Emoji表情符号
- 使用Markdown格式组织内容（标题、列表、加粗等）
- 关键数字和指标使用**加粗**显示
- 建议使用分点列表
- 适当使用分隔线 --- 来组织内容
- 回复简洁明了，控制在150字以内

**Emoji使用建议**：
- 💰 金钱相关
- 📊 数据分析
- 💡 建议提示
- ✅ 确认成功
- ⚠️ 警告注意
- 🎬 娱乐类服务
- 💼 生产力工具
- 📈 增长趋势
- 📉 下降趋势
- ➕ 添加订阅

用户当前状态：
{context}

用户问题：{message}"""

            prompt = system_prompt.format(
                context=context_str if context_str else "暂无订阅数据",
                message=sanitized_message
            )

            # 检查模型是否已初始化
            if self.model is None:
                self.logger.warning("模型未初始化，使用降级响应")
                fallback_response = self._get_fallback_response(sanitized_message, user_context)
                return {
                    "response": fallback_response,
                    "intent": self._analyze_intent(sanitized_message),
                    "confidence": 0.3,
                    "tokens_used": 0,
                    "response_time": time.time() - start_time,
                    "model": "gemini-not-initialized",
                    "error": "模型未初始化"
                }

            # 调用Gemini API（带超时保护）
            try:
                # 使用线程池执行器添加超时保护
                import concurrent.futures
                
                def call_api():
                    return self.model.generate_content(prompt)
                
                # 设置30秒超时
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(call_api)
                    try:
                        response = future.result(timeout=30.0)
                    except concurrent.futures.TimeoutError:
                        self.logger.error("Gemini API调用超时（30秒）")
                        raise TimeoutError("API调用超时，请稍后重试")

                if response and hasattr(response, 'text') and response.text:
                    ai_response = response.text.strip()
                else:
                    ai_response = "抱歉，我现在无法生成回复，请稍后再试。"

                # 分析意图
                intent = self._analyze_intent(sanitized_message)

                # 计算置信度
                confidence = self._calculate_confidence(response, sanitized_message)

                # 统计token使用（近似）
                tokens_used = len(prompt.split()) + len(ai_response.split())

                self.logger.info(f"Gemini API调用成功，用时: {time.time() - start_time:.2f}秒")

                return {
                    "response": ai_response,
                    "intent": intent,
                    "confidence": confidence,
                    "tokens_used": tokens_used,
                    "response_time": time.time() - start_time,
                    "model": self.model_name
                }

            except TimeoutError as timeout_error:
                self.logger.error(f"Gemini API调用超时: {timeout_error}")
                # 降级响应
                fallback_response = self._get_fallback_response(sanitized_message, user_context)
                return {
                    "response": f"请求超时，请稍后重试。\n\n{fallback_response}",
                    "intent": self._analyze_intent(sanitized_message),
                    "confidence": 0.3,
                    "tokens_used": 0,
                    "response_time": time.time() - start_time,
                    "model": "gemini-timeout",
                    "error": str(timeout_error)
                }
            except Exception as api_error:
                self.logger.error(f"Gemini API调用失败: {api_error}", exc_info=True)

                # 降级响应
                fallback_response = self._get_fallback_response(sanitized_message, user_context)
                return {
                    "response": fallback_response,
                    "intent": self._analyze_intent(sanitized_message),
                    "confidence": 0.3,
                    "tokens_used": 0,
                    "response_time": time.time() - start_time,
                    "model": "gemini-fallback",
                    "error": str(api_error)
                }

        except Exception as e:
            self.logger.error(f"处理用户请求时发生错误: {e}")
            return {
                "response": "抱歉，处理您的请求时发生了错误，请稍后再试。",
                "intent": "error",
                "confidence": 0.0,
                "tokens_used": 0,
                "response_time": time.time() - start_time,
                "model": "gemini-error",
                "error": str(e)
            }

    async def get_ai_response_async(self, user_message: str, user_context: Dict[str, Any] = None, user_id: str = "default") -> Dict[str, Any]:
        """异步获取AI响应"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.get_ai_response_sync,
            user_message,
            user_context,
            user_id
        )

    def analyze_bill_image(self, image_data: bytes, file_type: str = "image/jpeg") -> Dict[str, Any]:
        """分析账单图片 - OCR功能"""
        try:
            # 构建优化的OCR提示词
            ocr_prompt = """你是一个专业的账单识别专家。请仔细分析这张账单/收据图片，提取订阅服务信息。

## 分析步骤：
1. **全面扫描**: 识别图片中所有可见文字，包括公司logo、服务名称、金额、日期等
2. **重点关注**: 寻找以下关键信息：
   - 公司/服务名称（如Netflix、Spotify、ChatGPT等）
   - 付费金额（可能包含¥、$、€等货币符号）
   - 账单日期或付费周期
   - 服务类型或描述

## 常见订阅服务识别提示：
- **娱乐类(entertainment)**: Netflix、爱奇艺、腾讯视频、Spotify、Apple Music、YouTube Premium、SVIP
- **生产力(productivity)**: ChatGPT、Claude、Notion、Microsoft 365、Adobe Creative Cloud、夸克网盘、OneDrive、Dropbox、百度网盘
- **商务服务(business)**: AWS、阿里云、腾讯云、GitHub、JetBrains、Salesforce、Zoom Pro
- **教育培训(education)**: Coursera、Udemy、知乎付费、得到、极客时间
- **健康健身(health_fitness)**: Keep、咕咚、Nike Training Club
- **其他(other)**: VPN服务、域名注册、SSL证书等

## 金额识别规则：
- 如果显示"免费"、"Free"、"试用"，金额为0
- 提取纯数字，忽略货币符号
- 月付/年付从上下文判断

## 输出格式：
**原始文本：**
[按行列出图片中识别的所有文字内容]

**结构化数据：**
```json
{
    "service_name": "服务名称（如识别不出使用图片中的公司名）",
    "amount": 金额数字（数字类型，免费服务为0）,
    "currency": "币种代码（CNY/USD/EUR等）",
    "billing_date": "YYYY-MM-DD格式（如无法确定使用当前日期）",
    "billing_cycle": "monthly/yearly/weekly/daily",
    "category": "entertainment/productivity/education/business/health_fitness/storage/other",
    "confidence": 置信度（0.1-1.0，基于识别清晰度）
}
```

**账单描述：**
[用一句话描述这是什么服务的账单，包含服务类型和主要特征]

注意：如果图片模糊或信息不完整，请在相应字段标注并降低confidence值。"""

            # 准备图片数据
            import PIL.Image as Image
            import io

            # 将字节数据转换为PIL图像
            image = Image.open(io.BytesIO(image_data))

            # 调用Gemini Vision API
            response = self.model.generate_content([ocr_prompt, image])

            if response.text:
                # 提取各部分内容
                raw_text = self._extract_raw_text(response.text)
                description = self._extract_description(response.text)
                structured_data = self._extract_structured_data(response.text)

                # 记录结构化数据类型以进行调试
                self.logger.debug(f"提取的结构化数据类型: {type(structured_data)}")
                self.logger.debug(f"结构化数据内容: {structured_data}")

                # 验证和标准化结构化结果
                validated_result = self._validate_ocr_result(structured_data)

                # 记录提取结果
                self.logger.info(f"OCR文本提取结果: {len(raw_text)} 字符")
                self.logger.debug(f"提取的原始文本: {raw_text[:200]}...")
                self.logger.debug(f"提取的描述: {description[:100]}...")
                self.logger.debug(f"结构化数据: {structured_data}")

                return {
                    "success": True,
                    "extracted_data": validated_result,  # main.py期望的字段名
                    "raw_text": raw_text,
                    "description": description,
                    "confidence": validated_result.get("confidence", 0.8),
                    "model": self.model_name
                }

            else:
                raise Exception("Gemini未返回响应内容")

        except Exception as e:
            # 安全地处理异常信息，避免编码问题
            try:
                error_msg = str(e)
                # 如果错误消息包含特殊字符，用安全的方式处理
                safe_error_msg = error_msg.encode('utf-8', errors='replace').decode('utf-8')
                self.logger.error(f"账单OCR分析失败: {safe_error_msg}")
            except:
                # 如果连错误处理都失败，使用最简单的信息
                self.logger.error("账单OCR分析失败: 编码错误")
                safe_error_msg = "编码错误"

            # 返回默认结果
            default_result = self._get_default_ocr_result()
            return {
                "success": True,  # 即使失败也返回success=True，让前端可以使用默认数据
                "extracted_data": default_result,
                "raw_text": "OCR识别遇到问题，请手动输入信息",
                "description": "OCR识别遇到问题，请手动检查并输入正确信息。",
                "confidence": 0.3,
                "model": self.model_name,
                "error": "OCR处理异常"
            }

    def _validate_ocr_result(self, ocr_result: Any) -> Dict[str, Any]:
        """验证和标准化OCR结果"""
        # 处理各种可能的输入类型
        if isinstance(ocr_result, list):
            # 如果是列表，取第一个元素（如果有的话）
            if ocr_result and isinstance(ocr_result[0], dict):
                ocr_result = ocr_result[0]
            else:
                ocr_result = {}
        elif not isinstance(ocr_result, dict):
            # 如果不是字典也不是列表，使用空字典
            ocr_result = {}

        # 安全地处理金额转换
        amount_value = ocr_result.get("amount", 0.0)
        if amount_value:
            try:
                # 尝试转换为float，处理各种可能的字符串格式
                if isinstance(amount_value, str):
                    # 移除可能的非数字字符，但保留小数点
                    clean_amount = ''.join(c for c in amount_value if c.isdigit() or c == '.')
                    if clean_amount and clean_amount != '.':
                        amount_float = float(clean_amount)
                    else:
                        amount_float = 0.0
                else:
                    amount_float = float(amount_value)
            except (ValueError, TypeError):
                amount_float = 0.0
        else:
            amount_float = 0.0

        validated = {
            "service_name": str(ocr_result.get("service_name", "未知服务")),
            "amount": amount_float,
            "currency": str(ocr_result.get("currency", "CNY")),
            "billing_date": str(ocr_result.get("billing_date", datetime.now().strftime("%Y-%m-%d"))),
            "billing_cycle": str(ocr_result.get("billing_cycle", "monthly")),
            "category": str(ocr_result.get("category", "other")),
            "confidence": float(ocr_result.get("confidence", 0.7))
        }

        # 验证枚举值
        valid_cycles = ["monthly", "yearly", "weekly", "daily"]
        if validated["billing_cycle"] not in valid_cycles:
            validated["billing_cycle"] = "monthly"

        valid_categories = ["entertainment", "productivity", "education", "business", "health_fitness", "other"]
        if validated["category"] not in valid_categories:
            validated["category"] = "other"

        return validated

    def _extract_raw_text(self, response_text: str) -> str:
        """从Gemini响应中提取原始文本"""
        try:
            # 多种模式匹配原始文本
            patterns = [
                "**原始文本：**",
                "原始文本：",
                "**原始文本**",
                "原始文本",
                "文本内容：",
                "识别文本："
            ]

            for pattern in patterns:
                if pattern in response_text:
                    start = response_text.find(pattern) + len(pattern)

                    # 寻找结束标记
                    end_patterns = [
                        "**结构化数据：**", "结构化数据：", "**结构化数据**",
                        "```json", "{", "**账单描述：**", "账单描述："
                    ]

                    end = len(response_text)
                    for end_pattern in end_patterns:
                        end_pos = response_text.find(end_pattern, start)
                        if end_pos != -1:
                            end = end_pos
                            break

                    raw_text = response_text[start:end].strip()
                    if raw_text:
                        return raw_text

            # 如果都没找到标记，尝试从响应开头提取一些有意义的文本
            lines = response_text.strip().split('\n')
            meaningful_lines = []
            for line in lines[:10]:  # 只看前10行
                line = line.strip()
                if line and not line.startswith('*') and not line.startswith('```') and not line.startswith('{'):
                    meaningful_lines.append(line)

            if meaningful_lines:
                return '\n'.join(meaningful_lines)
            else:
                # 最后的备用方案
                return response_text[:300] + "..." if len(response_text) > 300 else response_text

        except Exception as e:
            return f"文本提取失败: {str(e)}"

    def _extract_description(self, response_text: str) -> str:
        """从Gemini响应中提取账单描述"""
        try:
            # 多种模式匹配描述
            patterns = [
                "**账单描述：**", "账单描述：", "**账单描述**", "账单描述",
                "**描述：**", "描述：", "**描述**", "描述",
                "**分析：**", "分析：", "**分析**", "分析"
            ]

            for pattern in patterns:
                if pattern in response_text:
                    start = response_text.find(pattern) + len(pattern)
                    description = response_text[start:].strip()
                    if description:
                        # 清理描述，去掉多余的格式符号
                        description = description.replace("```", "").replace("**", "").strip()
                        return description

            # 如果没有找到专门的描述标记，尝试从JSON或结构化数据后面找描述性文本
            if "confidence" in response_text:
                json_end = response_text.rfind("}")
                if json_end != -1:
                    after_json = response_text[json_end + 1:].strip()
                    if after_json:
                        return after_json

            # 备用方案：生成基本描述
            return "基于OCR识别的账单信息"

        except Exception as e:
            return f"描述提取失败: {str(e)}"

    def _extract_structured_data(self, response_text: str) -> Dict[str, Any]:
        """从Gemini响应中提取结构化数据"""
        try:
            json_text = ""

            # 方法1: 寻找```json代码块
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()

            # 方法2: 寻找```代码块（可能没有json标记）
            elif "```" in response_text and "{" in response_text:
                start = response_text.find("```")
                if start != -1:
                    # 跳过第一个```后找到{
                    bracket_start = response_text.find("{", start)
                    if bracket_start != -1:
                        bracket_end = response_text.rfind("}")
                        if bracket_end > bracket_start:
                            json_text = response_text[bracket_start:bracket_end + 1]

            # 方法3: 直接寻找JSON对象
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]

            if json_text:
                # 清理JSON文本
                json_text = json_text.strip()
                # 移除可能的前缀文本
                if json_text.startswith("```json"):
                    json_text = json_text[7:].strip()
                if json_text.endswith("```"):
                    json_text = json_text[:-3].strip()

                return json.loads(json_text)

            return {}

        except (json.JSONDecodeError, Exception) as e:
            # 如果JSON解析失败，尝试从响应中提取关键信息
            self.logger.debug(f"JSON解析失败，尝试手动提取: {str(e)}")
            return self._extract_data_manually(response_text)

    def _extract_data_manually(self, response_text: str) -> Dict[str, Any]:
        """手动从文本中提取数据（当JSON解析失败时的备用方案）"""
        result = {}

        try:
            lines = response_text.lower().split('\n')

            # 扩展的服务名称识别词典
            service_patterns = {
                # 娱乐类
                'netflix': ['netflix', '奈飞', 'netflix.com'],
                'spotify': ['spotify', 'spotify音乐'],
                'youtube': ['youtube', 'youtube premium', 'youtube会员'],
                'tencent_video': ['腾讯视频', 'tencent video', 'qq音乐'],
                'iqiyi': ['爱奇艺', 'iqiyi', 'iq.com'],
                'bilibili': ['bilibili', 'b站', '哔哩哔哩'],

                # 生产力类
                'chatgpt': ['chatgpt', 'chat gpt', 'openai'],
                'claude': ['claude', 'anthropic'],
                'notion': ['notion', 'notion.so'],
                'microsoft': ['microsoft', '微软', 'office', 'office365'],
                'adobe': ['adobe', 'creative cloud', 'photoshop'],

                # 开发工具
                'github': ['github', 'github.com'],
                'jetbrains': ['jetbrains', 'intellij', 'pycharm'],
                'aws': ['aws', 'amazon web services', '亚马逊云'],
                'aliyun': ['阿里云', 'aliyun', 'alibaba cloud'],
                'tencent_cloud': ['腾讯云', 'tencent cloud'],

                # 其他常见服务
                'icloud': ['icloud', 'apple storage', '苹果存储'],
                'dropbox': ['dropbox', 'dropbox.com'],
                'google': ['google', 'gmail', 'google drive'],
                'zoom': ['zoom', 'zoom会议'],
                'vpn': ['vpn', 'nordvpn', 'expressvpn']
            }

            for line in lines:
                line = line.strip()

                # 使用扩展的服务识别
                for service_key, patterns in service_patterns.items():
                    for pattern in patterns:
                        if pattern in line:
                            result['service_name'] = service_key.replace('_', ' ').title()
                            break
                    if 'service_name' in result:
                        break

                # 提取金额 - 改进的模式匹配
                import re

                # 检查免费服务关键词
                free_keywords = ['免费', 'free', '试用', 'trial', '0.00', '0元']
                if any(keyword in line for keyword in free_keywords):
                    result['amount'] = 0.0
                else:
                    # 多种金额格式识别
                    money_patterns = [
                        r'(\d+\.?\d*)\s*元',           # 15.99元
                        r'¥\s*(\d+\.?\d*)',           # ¥15.99
                        r'\$\s*(\d+\.?\d*)',          # $15.99
                        r'CNY\s*(\d+\.?\d*)',         # CNY 15.99
                        r'USD\s*(\d+\.?\d*)',         # USD 15.99
                        r'(\d+\.?\d*)\s*CNY',         # 15.99 CNY
                        r'(\d+\.?\d*)\s*USD',         # 15.99 USD
                        r'金额[：:]\s*(\d+\.?\d*)',    # 金额：15.99
                        r'费用[：:]\s*(\d+\.?\d*)',    # 费用：15.99
                        r'价格[：:]\s*(\d+\.?\d*)',    # 价格：15.99
                        r'(\d+\.?\d*)',               # 纯数字（最后备选）
                    ]

                    for pattern in money_patterns:
                        match = re.search(pattern, line)
                        if match and ('价格' in line or '金额' in line or '费用' in line or 'price' in line or 'amount' in line or '$' in line or '¥' in line):
                            try:
                                result['amount'] = float(match.group(1))
                                break
                            except (ValueError, TypeError):
                                continue

                # 提取币种
                if 'usd' in line or '$' in line:
                    result['currency'] = 'USD'
                elif 'cny' in line or 'yuan' in line or '元' in line:
                    result['currency'] = 'CNY'
                elif 'eur' in line or '€' in line:
                    result['currency'] = 'EUR'

                # 提取付费周期
                if 'monthly' in line or '月' in line:
                    result['billing_cycle'] = 'monthly'
                elif 'yearly' in line or '年' in line:
                    result['billing_cycle'] = 'yearly'
                elif 'weekly' in line or '周' in line:
                    result['billing_cycle'] = 'weekly'

            # 智能分类逻辑
            self._assign_smart_category(result)

            # 设置默认值
            if not result.get('service_name'):
                result['service_name'] = '未知服务'
            if not result.get('amount'):
                result['amount'] = 0.0
            if not result.get('currency'):
                result['currency'] = 'CNY'
            if not result.get('billing_cycle'):
                result['billing_cycle'] = 'monthly'
            if not result.get('category'):
                result['category'] = 'other'

            result['confidence'] = 0.4  # 手动提取的置信度稍高

        except Exception as e:
            # 安全地处理异常，避免编码问题
            try:
                safe_error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
                self.logger.error(f"手动数据提取失败: {safe_error_msg}")
            except:
                self.logger.error("手动数据提取失败: 编码错误")
            result = {
                'service_name': '未知服务',
                'amount': 0.0,
                'currency': 'CNY',
                'billing_cycle': 'monthly',
                'category': 'other',
                'confidence': 0.1
            }

        return result

    def _assign_smart_category(self, result: Dict[str, Any]) -> None:
        """根据服务名称智能分配分类"""
        service_name = result.get('service_name', '').lower()

        # 分类映射
        category_mappings = {
            'entertainment': [
                'netflix', 'spotify', 'youtube', 'tencent video', 'iqiyi', 'bilibili',
                '奈飞', '腾讯视频', '爱奇艺', '哔哩哔哩', 'qq音乐', 'apple music', 'amazon prime'
            ],
            'productivity': [
                'chatgpt', 'claude', 'notion', 'microsoft', 'adobe', 'office',
                'creative cloud', 'photoshop', 'canva', 'figma', 'slack'
            ],
            'business': [
                'github', 'jetbrains', 'aws', 'aliyun', 'tencent cloud', 'google workspace',
                'dropbox', 'zoom', 'salesforce', 'hubspot', 'mailchimp'
            ],
            'health_fitness': [
                'apple fitness', 'nike', 'peloton', 'myfitnesspal', 'headspace', 'calm'
            ],
            'education': [
                'coursera', 'udemy', 'masterclass', 'linkedin learning', 'skillshare'
            ]
        }

        # 根据服务名称匹配分类
        for category, services in category_mappings.items():
            for service in services:
                if service in service_name:
                    result['category'] = category
                    return

        # 如果没有匹配到，保持默认值
        if 'category' not in result:
            result['category'] = 'other'

    def _get_default_ocr_result(self) -> Dict[str, Any]:
        """获取默认OCR结果"""
        return {
            "service_name": "示例服务",
            "amount": 15.99,
            "currency": "CNY",
            "billing_date": datetime.now().strftime("%Y-%m-%d"),
            "billing_cycle": "monthly",
            "category": "entertainment",
            "confidence": 0.5
        }

    def _calculate_confidence(self, response: Any, user_message: str) -> float:
        """计算响应置信度"""
        base_confidence = 0.8

        # 根据消息长度调整置信度
        message_length = len(user_message)
        if message_length < 10:
            base_confidence -= 0.1
        elif message_length > 100:
            base_confidence += 0.1

        # 根据响应长度调整
        if hasattr(response, 'text') and response.text:
            response_length = len(response.text)
            if response_length < 20:
                base_confidence -= 0.2
            elif response_length > 100:
                base_confidence += 0.1

        return max(0.1, min(1.0, base_confidence))

    def _get_fallback_response(self, user_message: str, user_context: Dict[str, Any] = None) -> str:
        """获取降级响应"""
        intent = self._analyze_intent(user_message)

        fallback_responses = {
            "spending_query": f"根据您的数据，当前月度支出约为CNY {user_context.get('monthly_spending', 0):.2f}。",
            "subscription_count": f"您当前有{len(user_context.get('subscriptions', []))}个订阅服务。",
            "cancel_request": "您可以在订阅列表中找到相应服务，点击删除按钮来取消订阅。",
            "optimization_advice": "建议您定期检查订阅服务的使用情况，取消不常用的服务来节省开支。",
            "add_subscription": "您可以点击「添加订阅」按钮来添加新的订阅服务。",
            "general_query": "我是您的AI订阅管家，可以帮助您管理和优化订阅服务。有什么可以为您做的吗？"
        }

        return fallback_responses.get(intent, "抱歉，我现在无法处理您的请求，请稍后再试。")


# 创建全局客户端实例
_gemini_client = None

def get_gemini_client() -> Optional[GeminiClient]:
    """获取Gemini客户端实例"""
    global _gemini_client

    if _gemini_client is None:
        try:
            _gemini_client = GeminiClient()
            # 验证模型是否成功初始化
            if _gemini_client.model is None:
                logging.getLogger(__name__).warning("Gemini模型初始化失败，但客户端已创建（将使用降级响应）")
        except (ValueError, Exception) as e:
            # API密钥未配置或其他错误
            logging.getLogger(__name__).warning(f"Gemini客户端初始化失败: {e}", exc_info=True)
            # 即使初始化失败，也创建一个客户端实例，但model为None
            # 这样可以在调用时使用降级响应
            # 即使初始化失败，也创建一个带有基础属性的客户端实例
            # 这样可以在调用时使用降级响应而不崩溃
            try:
                class FallbackGeminiClient:
                    def __init__(self):
                        self.model = None
                        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
                        self.logger = logging.getLogger(__name__)
                        self.max_message_length = 2000
                    
                    def get_ai_response_sync(self, *args, **kwargs):
                        return {
                            "response": "抱歉，处理您的请求时发生了错误，请稍后再试。",
                            "intent": "error",
                            "confidence": 0.0
                        }
                    
                    async def get_ai_response_async(self, *args, **kwargs):
                        return self.get_ai_response_sync(*args, **kwargs)

                _gemini_client = FallbackGeminiClient()
            except Exception as fe:
                logging.getLogger(__name__).error(f"FallbackGeminiClient creation failed: {fe}")
                return None

    return _gemini_client

def is_gemini_available() -> bool:
    """检查Gemini API是否可用"""
    return get_gemini_client() is not None