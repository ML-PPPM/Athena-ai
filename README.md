# 🏛️ Athena AI — Complete DSE Teacher

A **Streamlit-powered AI tutor** for Hong Kong DSE students, powered by OpenRouter AI.

## ✨ Features

- **📚 Learn Mode** — Ask any topic → get smart, exam-ready summaries
- **🧠 Quiz Mode** — Generate random DSE-style questions with streak tracking  
- **📝 Past Paper Mode** — Practice authentic past paper MC and structured questions
- **📋 Study Planner** — Get personalized week-by-week study roadmaps

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Streamlit
- OpenRouter API key

### Installation

```bash
# Clone the repo
git clone https://github.com/ML-PPPM/Athena-ai.git
cd Athena-ai

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
mkdir -p .streamlit
echo 'OPENROUTER_API_KEY = "sk-or-v1-..."' > .streamlit/secrets.toml

# Run the app
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Configuration

### Environment Variables

You can override the default model by setting:

```bash
export OPENROUTER_MODEL="meta-llama/llama-3.3-70b-instruct"
```

Or add to `.streamlit/secrets.toml`:

```toml
OPENROUTER_API_KEY = "sk-or-v1-..."
OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct"
```

## 🎓 Supported Subjects

- 📐 Mathematics (Compulsory + M1 + M2)
- 🔬 Physics, 🧪 Chemistry, 🧬 Biology
- 📖 English, ✍️ Chinese Language  
- 🌍 Geography, 📜 History, 💼 Economics
- 🏛️ Citizenship & Social Development
- 💻 ICT, 📊 BAFS

## 📋 Project Structure

```
streamlit_app.py      # Main application
requirements.txt      # Python dependencies
README.md            # Documentation
.gitignore           # Git ignore rules
```

## 🏗️ Architecture

### Core Components

1. **Session Management** — Streamlit session state for multi-turn interactions
2. **API Client** — Cached OpenRouter client for efficiency
3. **Quiz Engine** — JSON parsing & validation for MC questions
4. **Study Planner** — Personalized study schedules based on user input

### Key Improvements

- ✅ **Logging** — Full logging for debugging and monitoring
- ✅ **Validation** — Input validation for form submissions  
- ✅ **Error Handling** — Robust error handling with user-friendly messages
- ✅ **Docstrings** — Comprehensive function documentation
- ✅ **Code Reuse** — Consolidated reset functions to reduce duplication

## 📝 Usage Examples

### Learn Mode
1. Select "📚 Learn"
2. Pick a subject
3. Ask any topic (e.g., "Trigonometric identities")
4. Get a formatted summary with formulas, examples, and exam tips

### Quiz Mode
1. Select "🧠 Quiz"  
2. Enter a topic
3. Answer multiple choice questions
4. Track your score and streak

### Past Paper Mode
1. Select "📝 Past Paper"
2. Choose MC or Structured questions
3. Practice with authentic DSE-style questions
4. Review marking schemes and model answers

### Study Planner
1. Select "📋 Study Planner"
2. Enter your subjects, exam date, and weak areas
3. Get a personalized week-by-week roadmap
4. Download as .txt or .md file

## 🔧 Development

### Adding New Subjects

Edit the `SUBJECTS` and `TOPIC_HINTS` dictionaries in `streamlit_app.py`:

```python
SUBJECTS = {
    "🎨 Art History": "DSE Art History",
    # ...
}

TOPIC_HINTS = {
    "DSE Art History": "Renaissance, Impressionism, Modern art",
    # ...
}
```

### Customizing System Prompts

Modify the prompt templates (e.g., `LEARN_SYSTEM`, `QUIZ_SYSTEM`) to adjust AI behavior.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m "Add amazing feature"`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 Logging

The app includes comprehensive logging for debugging:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
```

Logs are printed to console and can be exported to file via Streamlit config.

## ⚡ Performance Tips

- **Cold start**: First run takes longer as Streamlit compiles the app
- **Caching**: API client is cached to avoid reinitialization
- **Chat history**: Limited to 20 messages to prevent context overflow
- **Streaming**: Uses streaming for faster perceived performance

## 📄 License

MIT License — see LICENSE file for details.

## 🙋 Support

For issues or questions:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Include your Python version and environment

---

**Built for DSE students, by a DSE student.** 💪

Powered by OpenRouter AI • v2.1