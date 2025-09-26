# AI Subscription Butler (AI订阅管家)

An AI-powered subscription management assistant that helps users discover, manage, and optimize their subscriptions through natural conversation.

## 🚀 Features

- **🤖 Conversational AI Assistant**: Natural language interface for all subscription operations
- **📱 Smart Bill Recognition**: OCR-powered bill scanning and automatic subscription extraction
- **📊 Analytics Dashboard**: Visual insights into spending patterns and optimization opportunities
- **🔔 Intelligent Reminders**: Proactive notifications for renewals, unused services, and savings
- **💡 Cost Optimization**: AI-powered suggestions for reducing subscription costs

## 🛠️ Tech Stack

- **Backend**: Python 3.9+, FastAPI, SQLAlchemy
- **Frontend**: Streamlit
- **AI/ML**: OpenAI GPT-4, LangChain, ChromaDB
- **Database**: PostgreSQL (production), SQLite (development)
- **Deployment**: Docker, Railway/Render

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- Git
- OpenAI API key

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

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and other settings
   ```

5. **Initialize database**
   ```bash
   python scripts/setup.py
   ```

6. **Run the application**
   ```bash
   streamlit run app/main.py
   ```

Visit `http://localhost:8501` to access the application.

## 🏗️ Project Structure

```
ai-subscription-butler/
├── app/                    # Application entry point
│   ├── main.py            # Streamlit app
│   ├── config.py          # Configuration
│   └── constants.py       # Application constants
├── core/                  # Core business logic
│   ├── ai/               # AI agent and prompts
│   ├── database/         # Database models and CRUD
│   ├── services/         # Business services
│   └── utils/            # Utility functions
├── ui/                   # User interface components
│   ├── components/       # Reusable UI components
│   ├── pages/           # Streamlit pages
│   └── styles/          # CSS styles
├── tests/               # Test suite
├── docs/               # Documentation
├── scripts/           # Setup and utility scripts
└── data/             # Data storage
```

## 📚 Documentation

- [Requirements Analysis](docs/requirement.md)
- [Technical Architecture](docs/architecture.md)
- [Database Design](docs/database.md)
- [API Documentation](docs/api.md)
- [User Manual](docs/user-manual.md)
- [Troubleshooting](docs/troubleshooting.md)

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
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL_CHAT=gpt-3.5-turbo
OPENAI_MODEL_COMPLEX=gpt-4

# Database
DATABASE_URL=sqlite:///data/subscriptions.db

# Features
FEATURE_AI_CHAT=true
FEATURE_OCR=true
FEATURE_ANALYTICS=true
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

- ✅ Basic subscription management
- ✅ AI conversational interface
- 🔄 OCR bill recognition
- 🔄 Analytics dashboard
- 📅 Family subscription sharing
- 📅 Mobile app
- 📅 Enterprise features

## 🏆 Success Metrics

- **User Satisfaction**: >4.5/5
- **Cost Savings**: >¥50/user/month
- **Response Time**: <2 seconds
- **OCR Accuracy**: >85%

---

**Built with ❤️ using Claude Code**

*Last updated: 2025-01-XX*