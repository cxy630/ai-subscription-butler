# AI Subscription Butler (AI订阅管家)

An AI-powered subscription management assistant that helps users discover, manage, and optimize their subscriptions through natural conversation.

## 🚀 Features

### Core Features
- **🤖 Conversational AI Assistant**: Natural language interface powered by Google Gemini 2.5 Flash Lite
  - Multi-turn conversations with context awareness
  - Smart subscription discovery and management
  - Natural language queries and commands

- **📱 Smart Bill Recognition (OCR)**: Three-step intelligent workflow
  - Automatic text recognition from bill screenshots
  - Interactive confirmation and correction
  - One-click form filling with extracted data
  - Supports Chinese and English bills

- **📊 Analytics Dashboard**: Comprehensive spending insights
  - Spending trends analysis with visual charts
  - Category breakdown and insights
  - Quick stats (total subscriptions, monthly cost, active services)
  - Expandable category details with service lists

- **🔔 Intelligent Reminder System**: Never miss a renewal
  - Automatic billing date calculation (handles edge cases like month-end dates)
  - Priority-based notifications (urgent/high/medium/low)
  - Customizable reminder timelines (7, 14, 21, 28+ days ahead)
  - Color-coded countdown indicators
  - Reminder statistics dashboard

- **✏️ Smart Subscription Management**:
  - Inline accordion-style editing
  - Subscription and renewal date tracking
  - Category-based organization
  - Flexible filtering and sorting
  - Batch operations support

- **💾 Data Export**: Multiple format support
  - CSV export for spreadsheet analysis
  - JSON export for data portability

- **🧠 Advanced AI Agents (v2.0)**: Proactive subscription management
  - **Negotiation Agent**: Personalized price negotiation strategies and message drafting
  - **Optimization Agent**: Automated detection of duplicate services and annual billing savings
  - **Savings War Room**: Value-oriented home page with real-time AI activity logs
  - **Weekly AI Reports**: Automated weekly consumption insights and summaries

## 🛠️ Tech Stack

- **Backend**: Python 3.9+
- **Frontend**: Streamlit
- **AI/ML**:
  - Google Gemini 2.5 Flash Lite (Chat & OCR)
  - Multi-modal AI for text and image processing
- **Database**: JSON file storage (development), PostgreSQL (planned for production)
- **Deployment**: Streamlit Cloud / Docker

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- Git
- Google Gemini API key (free tier available at https://aistudio.google.com/)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/cxy630/ai-subscription-butler.git
   cd ai-subscription-butler
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** 🔑
   ```bash
   cp .env.example .env
   # 编辑.env文件，添加你的Google Gemini API密钥
   # GEMINI_API_KEY=your-api-key-here
   ```

   ⚠️ **安全提醒**:
   - **绝不要**将包含真实API密钥的`.env`文件提交到Git
   - 项目已正确配置`.gitignore`来保护敏感文件
   - 查看 [SECURITY.md](SECURITY.md) 了解完整安全指南

5. **Run the application**
   ```bash
   streamlit run app/main.py --server.port=8501
   ```

Visit `http://localhost:8501` to access the application.

## 🏗️ Project Structure

```
ai-subscription-butler/
├── app/                    # Application entry point
│   ├── main.py            # Streamlit app with navigation
│   ├── config.py          # Configuration management
│   └── constants.py       # Application constants
├── core/                  # Core business logic
│   ├── ai/               # AI integration
│   │   ├── assistant.py  # AI assistant orchestration
│   │   └── gemini_client.py  # Gemini API client
│   ├── agents/           # [NEW] AI Agent Framework
│   │   ├── butler_agent.py   # Central coordinator
│   │   ├── rules_engine.py   # Automated logic engine
│   │   ├── negotiation_agent.py # Negotiation specialist
│   │   └── activity_logger.py # Audit and transparency
│   ├── database/         # Data persistence
│   │   ├── json_storage.py  # JSON file storage
│   │   └── data_interface.py  # Data access layer
│   ├── services/         # Business services
│   │   ├── reminder_system.py # Billing reminder logic
│   │   └── daily_checkup_scheduler.py # Automated task runner
│   └── utils/            # Utility functions
├── ui/                   # User interface components
│   ├── pages/            # Page-level components
│   └── components/       # Reusable UI components
│       ├── activity_stream.py # [NEW] Live AI feed
│       ├── dashboard.py  # Main dashboard with analytics
│       ├── chat.py      # AI chat interface
│       ├── reminders.py # Reminder notifications
│       └── ocr.py      # Bill OCR interface
├── tests/               # Test suite
├── docs/               # Documentation
├── scripts/           # Utility scripts
│   └── fix_categories.py  # Batch category updates
└── data/             # JSON data storage
    ├── subscriptions.json
    ├── users.json
    └── conversations.json
```

## 📚 Documentation

- [Requirements Analysis](docs/requirement.md)
- [Technical Architecture](docs/architecture.md)
- [Database Design](docs/database.md)
- [UI Design](docs/ui-design.md)
- [AI Integration](docs/ai-integration.md)
- [Security Guide](SECURITY.md)

## 🚀 Development

### Development Setup

1. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

3. **Run tests**
   ```bash
   pytest
   ```

4. **Code formatting**
   ```bash
   black .
   isort .
   flake8
   ```

### Sprint Development

The project follows a 4-sprint development cycle:

- **Sprint 0**: Foundation & Documentation
- **Sprint 1**: AI Integration
- **Sprint 2**: Intelligence Features
- **Sprint 3**: Polish & Deployment

See [claude.me](claude.me) for detailed development workflow.

## 🔧 Configuration

Key configuration options in `.env`:

```bash
# Google Gemini Configuration
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash-lite

# Application Settings
APP_PORT=8501
DEBUG_MODE=false

# Features (all enabled by default)
FEATURE_AI_CHAT=true
FEATURE_OCR=true
FEATURE_ANALYTICS=true
FEATURE_REMINDERS=true
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Email**: chenxy@fortune-data.com
- **Issues**: [GitHub Issues](https://github.com/cxy630/ai-subscription-butler/issues)
- **Documentation**: [Project Docs](docs/)

## 🎯 Roadmap

### Completed ✅
- ✅ Basic subscription management with CRUD operations
- ✅ AI conversational interface (Gemini 2.5 Flash Lite)
- ✅ OCR bill recognition with three-step workflow
- ✅ Analytics dashboard with spending trends
- ✅ Intelligent reminder system with priority notifications
- ✅ Data export (CSV, JSON)
- ✅ **Negotiation Agent**: Automated price negotiation strategies
- ✅ **Rule Engine**: Duplicate detection and annual savings logic
- ✅ **Savings War Room**: Redesigned value-centric home page
- ✅ **Automated Weekly Reports**: AI-generated consumption summaries
- ✅ Inline editing with accordion UI
- ✅ Category-based organization

### In Progress 🔄
- 🔄 Email/SMS notification integration
- 🔄 Batch operations for subscriptions
- 🔄 Notification preferences and settings

### Planned 📅
- 📅 Data backup and restore
- 📅 Multi-user support and family sharing
- 📅 Mobile responsive design
- 📅 Budget tracking and alerts
- 📅 Subscription recommendations

## 🏆 Success Metrics

- **User Satisfaction**: >4.5/5
- **Cost Savings**: >¥50/user/month
- **Response Time**: <2 seconds
- **OCR Accuracy**: >85%

---

**Built with ❤️ using Claude Code**

*Last updated: 2025-09-30*