import streamlit as st
from groq import Groq
import json
import re
import logging
from datetime import datetime, timedelta
from typing import Tuple

# Local imports
from config import settings, MAX_CHAT_HISTORY, DEFAULT_MAX_TOKENS
from database import db
from auth import init_auth_session, render_auth_page, check_usage_limit, render_premium_badge, logout
from payments import render_pricing_table

# ╔════════════════════════════════════════════════════════════════╗
# ║                  ATHENA AI — COMPLETE DSE TEACHER              ║
# ║        📚 Learn   🧠 Quiz   📝 Past Paper   📋 Planner        ║
# ╚════════════════════════════════════════════════════════════════╝

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Athena AI 🏛️ — DSE Teacher",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
# INITIALIZE SESSION & AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════

init_auth_session()

if not st.session_state.get("is_authenticated"):
    render_auth_page()
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# USER AUTHENTICATED - CONTINUE WITH APP
# ═══════════════════════════════════════════════════════════════════

MODEL = settings.GROQ_MODEL
MAX_CHAT_HISTORY_LIMIT = MAX_CHAT_HISTORY


# ╔════════════════════════════════════════════════════════════════╗
# ║                          STYLING                               ║
# ╚════════════════════════════════════════════════════════════════╝

st.markdown("""
<style>
    .block-container { max-width: 800px; padding-top: 2rem; }

    h1 {
        background: linear-gradient(135deg, #6C63FF 0%, #48C6EF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }

    .stButton > button {
        border-radius: 12px;
        font-size: 14px;
        font-weight: 500;
        padding: 10px 20px;
        transition: all 0.25s ease;
        border: 1px solid rgba(108, 99, 255, 0.15);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(108, 99, 255, 0.2);
    }
    .stButton > button:active { transform: translateY(0); }

    .stChatMessage { border-radius: 16px; }
    .stAlert { border-radius: 12px; }
    hr { border-color: rgba(108, 99, 255, 0.1); }
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #6C63FF; }

    .stForm {
        border: 1px solid rgba(108, 99, 255, 0.12);
        border-radius: 16px;
        padding: 20px;
    }

    @keyframes fireGlow {
        0%, 100% { text-shadow: 0 0 4px #ff6b35; }
        50%      { text-shadow: 0 0 16px #ff6b35, 0 0 24px #ffa07a; }
    }
    .streak-fire { animation: fireGlow 1.5s infinite; font-size: 1.15rem; }

    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ╔════════════════════════════════════════════════════════════════╗
# ║                     SUBJECTS & TOPIC HINTS                     ║
# ╚════════════════════════════════════════════════════════════════╝

SUBJECTS = {
    "📐 Mathematics":         "DSE Mathematics (Compulsory Part)",
    "📐 M1 (Calc & Stats)":   "DSE Mathematics Module 1 (Calculus and Statistics)",
    "📐 M2 (Algebra & Calc)": "DSE Mathematics Module 2 (Algebra and Calculus)",
    "🔬 Physics":             "DSE Physics",
    "🧪 Chemistry":           "DSE Chemistry",
    "🧬 Biology":             "DSE Biology",
    "📖 English":             "DSE English Language",
    "✍️ Chinese 中文":        "DSE Chinese Language 中國語文",
    "🌍 Geography":           "DSE Geography",
    "📜 History":             "DSE History",
    "💼 Economics":           "DSE Economics",
    "🏛️ Citizenship 公民科":  "DSE Citizenship and Social Development",
    "💻 ICT":                 "DSE Information and Communication Technology",
    "📊 BAFS":                "DSE Business, Accounting and Financial Studies",
}

TOPIC_HINTS = {
    "DSE Mathematics (Compulsory Part)":
        "Quadratic equations, Trigonometry, Probability, Sequences",
    "DSE Mathematics Module 1 (Calculus and Statistics)":
        "Binomial distribution, Definite integrals, Normal distribution",
    "DSE Mathematics Module 2 (Algebra and Calculus)":
        "Matrix operations, Limits, Vectors, Mathematical induction",
    "DSE Physics":
        "Newton's laws, Radioactivity, Electromagnetism, Wave motion",
    "DSE Chemistry":
        "Organic chemistry, Mole concept, Redox reactions, Chemical bonding",
    "DSE Biology":
        "Photosynthesis, DNA replication, Ecosystems, Human reproduction",
    "DSE English Language":
        "Passive voice, Conditionals, Argumentative essay, Summary writing",
    "DSE Chinese Language 中國語文":
        "文言文, 修辭手法, 議論文寫作, 閱讀理解",
    "DSE Geography":
        "Plate tectonics, Urbanization, Climate change, Coastal processes",
    "DSE History":
        "Cold War, May Fourth Movement, Japanese invasion, Modernization",
    "DSE Economics":
        "Supply and demand, GDP, Monetary policy, Market structures",
    "DSE Citizenship and Social Development":
        "National security, Rule of law, Globalization, APEC",
    "DSE Information and Communication Technology":
        "Networking, Database, Algorithms, Cybersecurity",
    "DSE Business, Accounting and Financial Studies":
        "Ratio analysis, Accounting cycle, Marketing mix, Budgeting",
}


# ╔════════════════════════════════════════════════════════════════╗
# ║                      SYSTEM PROMPTS                            ║
# ╚════════════════════════════════════════════════════════════════╝

LEARN_SYSTEM = """You are Athena AI — the smartest, most beloved DSE teacher in Hong Kong.
Subject: {subject}

When a student asks about ANY topic, respond with this SMART SUMMARY:

🎯 **Core Concept**
[1–2 sentences. Explain like talking to a smart friend. SIMPLE.]

🔑 **Key Points**
1. **[Point]** — [real-life example or analogy]
2. **[Point]** — [example]
3. **[Point]** — [example]
(add 4–6 if truly needed)

📊 **Key Formulas / Rules**
[Relevant formulas, equations, grammar rules, or key terms]
[Skip this section entirely if not applicable]

📝 **DSE Exam Tip**
[One SPECIFIC tip for scoring marks on this topic in the real DSE exam]

🧠 **Memory Trick**
[A mnemonic, analogy, visual image, or story to lock this in memory]

🔗 **Also Study:** [related topic 1] → [related topic 2] → [related topic 3]

RULES:
- Be CONCISE — students are busy and stressed
- Use Hong Kong daily life examples when possible (MTR, dim sum, Mark Six, etc.)
- For Math/Science: ALWAYS include key formulas with clear variable definitions
- For Languages: include practical sentence examples
- For Humanities: include key dates, names, cause-effect chains
- Understand Chinese/Cantonese input; respond in English unless user writes in Chinese
- If the student asks a follow-up, build on your previous summary
- Make the complex SIMPLE, never the simple complex
- Be encouraging — DSE students need support!"""

QUIZ_SYSTEM = """You are a DSE quiz question generator.
Subject: {subject}. Topic: {topic}.

Generate exactly ONE challenging multiple choice question.

RESPOND WITH ONLY THIS JSON — no other text before or after:
{{"question":"clear question text","A":"option A","B":"option B","C":"option C","D":"option D","answer":"C","explanation":"detailed explanation: WHY the correct answer is right and WHY each wrong answer is wrong"}}

RULES:
- DSE exam difficulty level
- Wrong options must be PLAUSIBLE (based on real student mistakes)
- Explanation must TEACH the concept, not just state the answer
- For Math/Physics: include step-by-step calculation in explanation
- Vary question types: conceptual, calculation, application, analysis
- ONLY output the JSON object"""

PAST_PAPER_MC_SYSTEM = """You are a DSE past paper question simulator.
Subject: {subject}. Topic: {topic}.

Generate ONE question that mirrors a real DSE past paper MC question.

RESPOND WITH ONLY THIS JSON — no other text:
{{"year":"2023","paper":"Paper 1","qnum":15,"question":"question text in authentic DSE style","A":"option A","B":"option B","C":"option C","D":"option D","answer":"B","explanation":"detailed explanation referencing marking principles","concept":"core concept tested","difficulty":"medium"}}

RULES:
- Must feel AUTHENTIC to real DSE papers in wording and style
- Use proper DSE terminology and phrasing
- Include diagram descriptions in [brackets] if relevant
- Wrong options should reflect REAL common student errors
- Explanation should reference how marks are awarded
- difficulty must be "easy", "medium", or "hard"
- ONLY output the JSON"""

PAST_PAPER_LONG_SYSTEM = """You are a DSE past paper structured question simulator.
Subject: {subject}. Topic: {topic}.

Generate ONE structured question (long question) in authentic DSE style.

Format EXACTLY like this:

📝 **{subject} — Structured Question**
**Topic:** {topic}
**Total Marks:** [X marks]

---

[Context paragraph — realistic data, scenarios, tables, or diagram descriptions exactly like real DSE papers]

**(a)** [Question — DSE command words: State, Describe, Explain] **({x} marks)**

**(b)** [Harder question building on (a) — Calculate, Explain, Compare] **({x} marks)**

**(c)** [Hardest — Evaluate, Discuss, Suggest, Justify] **({x} marks)**

---

✏️ *Attempt this question before checking the marking scheme!*

RULES:
- Parts MUST increase in difficulty: (a) recall → (b) apply → (c) analyze/evaluate
- Use REAL DSE command words and phrasing
- Include realistic numerical data for science/math subjects
- Include source material/passages for humanities subjects
- Mark allocation must match DSE standards (typically 2–8 marks per part)
- DO NOT include answers — the student must attempt first"""

MARKING_SYSTEM = """You are a DSE chief examiner generating an official-style marking scheme.
Subject: {subject}

The student was given this question:
{question}

Provide a comprehensive DSE marking scheme:

✅ **Marking Scheme**

**(a)** [{x} marks]
- [Answer point] ✓ (1 mark)
- [Answer point] ✓ (1 mark)
[Full working for calculations]

**(b)** [{x} marks]
- [Answer with marking points]

**(c)** [{x} marks]
- [Model answer with marking criteria]

📊 **Examiner's Notes:**
- **Common mistakes:** [specific errors students make]
- **Full marks tip:** [exactly what examiners look for]
- **Partial credit:** [how to get marks even if stuck]

RULES:
- Match real DSE marking scheme style precisely
- Show every mark point clearly with ✓
- For calculations: separate marks for METHOD + ANSWER
- Include common errors and partial credit guidance"""

PLANNER_SYSTEM = """You are Athena AI — the best DSE study planner in Hong Kong.
Create a DETAILED, PERSONALIZED study plan.

📊 **Your DSE Dashboard**
- Days remaining: [X]
- Subjects: [X]
- Daily study hours: [X]
- Priority level: [assessment]

---

🎯 **Priority Ranking** (weakest → strongest)
1. 🔴 [Subject] — [specific weak area] — [strategy]
2. 🟡 [Subject] — [area] — [strategy]
3. 🟢 [Subject] — [area] — [strategy]

---

📅 **Weekly Schedule Template**

| Day | Session 1 | Session 2 | Session 3 |
|-----|-----------|-----------|-----------|
| Mon | Subject (topic) | Subject (topic) | Review |
[… complete table]

---

⏰ **Daily Schedule Template** (for {hours}hr study day)
[Specific time blocks with Pomodoro technique. Include breaks, meals, exercise.]

---

📋 **Week-by-Week Roadmap**

**Weeks 1–2:** [Foundation — specific topics]
**Weeks 3–4:** [Deep practice — specific topics]
**Weeks 5–6:** [Past paper intensive — specific papers]
**Weeks 7–8:** [Final revision — specific strategy]

---

⚡ **Quick Wins** (easiest marks to gain FAST)
1. [Specific topic/technique] — [why easy marks]
2. [Specific topic/technique] — [why]
3. [Specific topic/technique] — [why]

---

⚠️ **Mistakes to Avoid**
1. [Common DSE mistake]
2. [Study habit mistake]
3. [Time management mistake]

---

🧠 **Study Techniques for Your Subjects**
- [Subject]: [specific technique + application]

RULES:
- Be REALISTIC — don't overload
- Include REST days and breaks
- Give SPECIFIC topics, not vague advice
- Prioritize weak areas but maintain strong ones
- Include past paper practice weekly
- Factor in Hong Kong school schedule
- Be encouraging but honest"""


# ╔════════════════════════════════════════════════════════════════╗
# ║                       API CLIENT (GROQ)                        ║
# ╚════════════════════════════════════════════════════════════════╝

@st.cache_resource
def get_client():
    """Initialize and cache the Groq client."""
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "") or settings.GROQ_API_KEY
        if not api_key:
            st.error("⚠️ `GROQ_API_KEY` not found in Streamlit secrets.")
            st.info(
                "Add it to Streamlit secrets:\n"
                '```\nGROQ_API_KEY = "gsk_..."\n```'
            )
            st.stop()
        c = Groq(api_key=api_key)
        logger.info("Groq client initialized successfully")
        return c
    except Exception as e:
        st.error(f"⚠️ Failed to initialize Groq: {e}")
        st.stop()


client = get_client()


# ╔════════════════════════════════════════════════════════════════╗
# ║                      SESSION STATE                             ║
# ╚════════════════════════════════════════════════════════════════╝

DEFAULTS = {
    "messages":        [],
    "quiz":            None,
    "answered":        False,
    "picked":          None,
    "score":           0,
    "total":           0,
    "topic":           None,
    "streak":          0,
    "best_streak":     0,
    "pp_mc":           None,
    "pp_mc_answered":  False,
    "pp_mc_picked":    None,
    "pp_mc_score":     0,
    "pp_mc_total":     0,
    "pp_question":     None,
    "pp_answer":       None,
    "pp_show_answer":  False,
    "plan":            None,
    "prev_subject":    None,
    "prev_mode":       None,
}

for key, default in DEFAULTS.items():
    st.session_state.setdefault(key, default)


# ╔════════════════════════════════════════════════════════════════╗
# ║                    HELPER FUNCTIONS                            ║
# ╚════════════════════════════════════════════════════════════════╝

def parse_json(text):
    """Robustly extract a JSON object from AI response."""
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    code_match = re.search(r"```(?:json)?\s*(\{[^`]*\})\s*```", text, re.DOTALL)
    if code_match:
        try:
            return json.loads(code_match.group(1))
        except json.JSONDecodeError:
            pass
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(text[first_brace : last_brace + 1])
        except json.JSONDecodeError:
            pass
    logger.warning(f"parse_json: all strategies failed for: {text[:100]}...")
    return None


def validate_mc(data):
    """Return True if dict has all required MC fields."""
    if not isinstance(data, dict):
        return False
    required = {"question", "A", "B", "C", "D", "answer", "explanation"}
    if not required.issubset(data.keys()):
        return False
    if data["answer"] not in ("A", "B", "C", "D"):
        return False
    return True


def call_claude(system, user_msg, max_tokens=DEFAULT_MAX_TOKENS):
    """Single-turn Groq call with error handling."""
    try:
        logger.info(f"Groq call: max_tokens={max_tokens}")
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=0.7,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
        )
        if response and response.choices:
            logger.info("Groq response successful")
            return response.choices[0].message.content
        logger.warning("Groq returned empty response")
        return None
    except Exception as e:
        logger.error(f"Groq error: {e}", exc_info=True)
        st.error(f"❌ AI Error: {e}")
        return None


def call_claude_stream(system, messages, max_tokens=1500):
    """Streaming generator for multi-turn chat using Groq."""
    try:
        logger.info(f"Groq stream: {len(messages)} messages")

        groq_messages = [{"role": "system", "content": system}]
        for msg in messages:
            groq_messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        stream = client.chat.completions.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=0.7,
            messages=groq_messages,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

        logger.info("Groq stream completed")
    except Exception as e:
        logger.error(f"Groq stream error: {e}", exc_info=True)
        yield f"\n\n❌ Error: {e}"


def check_and_log_feature(feature: str) -> Tuple[bool, str]:
    """Check if user can access feature and log usage."""
    user_id = st.session_state.get("user_id")
    if not user_id:
        return True, ""
    allowed, message, _ = check_usage_limit(user_id, feature)
    if not allowed:
        st.error(message)
        return False, message
    if message:
        st.warning(message)
    return True, message


def generate_quiz(topic, subject):
    """Generate and validate a quiz MC question."""
    text = call_claude(
        QUIZ_SYSTEM.format(subject=subject, topic=topic),
        f"Generate a DSE-level question about: {topic}",
        max_tokens=600,
    )
    data = parse_json(text) if text else None
    if data and validate_mc(data):
        return data
    return None


def generate_pp_mc(topic, subject):
    """Generate and validate a past-paper MC question."""
    text = call_claude(
        PAST_PAPER_MC_SYSTEM.format(subject=subject, topic=topic),
        f"Generate a DSE past paper MC about: {topic}",
        max_tokens=700,
    )
    data = parse_json(text) if text else None
    if data and validate_mc(data):
        return data
    return None


def generate_pp_long(topic, subject):
    """Generate a structured (long) question."""
    return call_claude(
        PAST_PAPER_LONG_SYSTEM.format(subject=subject, topic=topic),
        f"Generate a DSE structured question about: {topic}",
        max_tokens=1500,
    )


def generate_marking(question_text, subject):
    """Generate a marking scheme for a question."""
    return call_claude(
        MARKING_SYSTEM.format(subject=subject, question=question_text),
        "Provide the full marking scheme for this question.",
        max_tokens=1500,
    )


def generate_plan(subjects_taken, exam_date, hours, weak, extra):
    """Generate a personalised study plan."""
    days_left = max((exam_date - datetime.now().date()).days, 1)
    prompt = (
        f"Student Profile:\n"
        f"- Subjects: {subjects_taken}\n"
        f"- DSE Exam Date: {exam_date} ({days_left} days remaining)\n"
        f"- Daily Study Hours: {hours}\n"
        f"- Weakest Areas: {weak}\n"
        f"- Additional Info: {extra}\n\n"
        f"Create a comprehensive, personalized study plan."
    )
    return call_claude(PLANNER_SYSTEM.format(hours=hours), prompt, max_tokens=3500)


def reset_mode(mode_type="all"):
    """Reset state for specific mode or all modes."""
    if mode_type in ("quiz", "all"):
        st.session_state.quiz = None
        st.session_state.answered = False
        st.session_state.picked = None
    if mode_type in ("pp_mc", "all"):
        st.session_state.pp_mc = None
        st.session_state.pp_mc_answered = False
        st.session_state.pp_mc_picked = None
    if mode_type in ("pp_long", "all"):
        st.session_state.pp_question = None
        st.session_state.pp_answer = None
        st.session_state.pp_show_answer = False
    if mode_type == "all":
        st.session_state.topic = None


def reset_quiz():
    reset_mode("quiz")

def reset_pp_mc():
    reset_mode("pp_mc")

def reset_pp_long():
    reset_mode("pp_long")


# ╔════════════════════════════════════════════════════════════════╗
# ║                         SIDEBAR                                ║
# ╚════════════════════════════════════════════════════════════════╝

with st.sidebar:
    render_premium_badge()
    st.divider()

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.get("auth_method") == "demo":
            st.caption("👤 Guest Mode")
        else:
            st.caption(f"👤 {st.session_state.get('user_email', 'User')}")
    with col2:
        if st.button("🚪", help="Logout"):
            logout()

    st.divider()
    st.markdown("# 🏛️ Athena AI")
    st.caption("Your Complete DSE Teacher")
    st.divider()

    sub_key = st.selectbox("📘 Subject", list(SUBJECTS.keys()), key="subject_sel")
    subject = SUBJECTS[sub_key]
    hint = TOPIC_HINTS.get(subject, "Enter any topic")

    if st.session_state.prev_subject and st.session_state.prev_subject != sub_key:
        st.session_state.messages = []
        reset_quiz()
        reset_pp_mc()
        reset_pp_long()
    st.session_state.prev_subject = sub_key

    st.markdown("")

    mode = st.radio(
        "🎯 Mode",
        ["📚 Learn", "🧠 Quiz", "📝 Past Paper", "📋 Study Planner"],
        key="mode_sel",
    )

    if st.session_state.prev_mode and st.session_state.prev_mode != mode:
        if mode != "🧠 Quiz":
            reset_quiz()
        if mode != "📝 Past Paper":
            reset_pp_mc()
            reset_pp_long()
    st.session_state.prev_mode = mode

    if mode == "🧠 Quiz" and st.session_state.total > 0:
        st.divider()
        pct = int(st.session_state.score / st.session_state.total * 100)
        st.metric(
            "📊 Quiz Score",
            f"{st.session_state.score}/{st.session_state.total} ({pct}%)",
        )
        streak = st.session_state.streak
        best = st.session_state.best_streak
        if streak >= 3:
            st.markdown(
                f"<p class='streak-fire'>🔥 Streak: {streak}"
                f" &nbsp;|&nbsp; 🏆 Best: {best}</p>",
                unsafe_allow_html=True,
            )
        else:
            st.caption(f"🔥 Streak: {streak}  |  🏆 Best: {best}")
        if st.button("🗑️ Reset Quiz Score", use_container_width=True):
            st.session_state.score = 0
            st.session_state.total = 0
            st.session_state.streak = 0
            st.session_state.best_streak = 0
            st.rerun()

    if mode == "📝 Past Paper" and st.session_state.pp_mc_total > 0:
        st.divider()
        pct = int(
            st.session_state.pp_mc_score / st.session_state.pp_mc_total * 100
        )
        st.metric(
            "📊 Past Paper MC",
            f"{st.session_state.pp_mc_score}/{st.session_state.pp_mc_total} ({pct}%)",
        )
        if st.button("🗑️ Reset PP Score", use_container_width=True):
            st.session_state.pp_mc_score = 0
            st.session_state.pp_mc_total = 0
            st.rerun()

    st.divider()
    if st.button("🗑️ Clear Everything", use_container_width=True):
        for k, v in DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()

    st.divider()

    if not st.session_state.get("is_premium"):
        if st.button("👑 Upgrade to Premium", use_container_width=True, type="primary"):
            st.session_state.show_pricing = True
            st.rerun()

    st.divider()
    st.markdown("**Built for DSE students** 💪")
    st.caption("Powered by Groq AI • v2.1")


# ╔════════════════════════════════════════════════════════════════╗
# ║                       MAIN CONTENT                             ║
# ╚════════════════════════════════════════════════════════════════╝

if st.session_state.get("show_pricing"):
    st.markdown("# 💰 Upgrade to Premium")
    render_pricing_table()
    if st.button("← Back to App"):
        st.session_state.show_pricing = False
        st.rerun()
    st.stop()

st.title(sub_key)

captions = {
    "📚 Learn":         "💡 Ask any topic → get a smart, exam-ready summary instantly",
    "🧠 Quiz":          "🧪 Enter a topic → answer questions → track your score",
    "📝 Past Paper":    "📋 Practice with authentic DSE-style questions",
    "📋 Study Planner": "📅 Get your personalized DSE study roadmap",
}
st.caption(captions.get(mode, ""))
st.divider()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                        📚  LEARN MODE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if mode == "📚 Learn":

    if len(st.session_state.messages) > MAX_CHAT_HISTORY:
        st.session_state.messages = st.session_state.messages[-MAX_CHAT_HISTORY:]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input(f"What do you want to learn? (e.g. {hint})"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = st.write_stream(
                call_claude_stream(
                    LEARN_SYSTEM.format(subject=subject),
                    st.session_state.messages,
                )
            )
            if response:
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

    if not st.session_state.messages:
        st.markdown("")
        st.info(
            f"👋 **Welcome!** Ask me anything about **{subject}**.\n\n"
            f"Try: *{hint}*"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                        🧠  QUIZ MODE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

elif mode == "🧠 Quiz":

    if st.session_state.quiz is None:
        if not st.session_state.topic:
            st.info(
                f"🧠 **Quiz Mode** — Enter a topic below to start.\n\n"
                f"*e.g. {hint}*"
            )
        if prompt := st.chat_input(f"Topic to quiz on? (e.g. {hint})"):
            st.session_state.topic = prompt
            with st.spinner("🧪 Generating question…"):
                q = generate_quiz(prompt, subject)
                if q:
                    st.session_state.quiz = q
                    st.session_state.answered = False
                    st.session_state.picked = None
                    st.rerun()
                else:
                    st.error("❌ Failed to generate — please try again.")

    else:
        q = st.session_state.quiz

        if st.session_state.topic:
            st.caption(f"📌 Topic: **{st.session_state.topic}**")

        st.markdown(f"### ❓ {q['question']}")
        st.markdown("")

        if not st.session_state.answered:
            cols = st.columns(2)
            for i, opt in enumerate(["A", "B", "C", "D"]):
                with cols[i % 2]:
                    if st.button(
                        f"{opt})  {q[opt]}",
                        key=f"quiz_{opt}",
                        use_container_width=True,
                    ):
                        st.session_state.picked = opt
                        st.session_state.answered = True
                        st.session_state.total += 1
                        if opt == q["answer"]:
                            st.session_state.score += 1
                            st.session_state.streak += 1
                            st.session_state.best_streak = max(
                                st.session_state.best_streak,
                                st.session_state.streak,
                            )
                        else:
                            st.session_state.streak = 0
                        st.rerun()

        else:
            correct = q["answer"]
            picked = st.session_state.picked

            for opt in ["A", "B", "C", "D"]:
                label = f"**{opt})** {q[opt]}"
                if opt == correct:
                    st.success(f"✅ {label}")
                elif opt == picked and picked != correct:
                    st.error(f"❌ {label}")
                else:
                    st.markdown(f"&emsp;⬜ {label}")

            st.markdown("")
            if picked == correct:
                st.balloons()
                s = st.session_state.streak
                if s >= 5:
                    st.success(f"🎉 **AMAZING!** Streak: {s} 🔥🔥🔥")
                elif s >= 3:
                    st.success(f"🎉 **Great job!** Streak: {s} 🔥")
                else:
                    st.success("🎉 **Correct!**")
            else:
                st.error(f"😅 Wrong — Correct answer: **{correct}**")

            with st.expander("📖 **Explanation**", expanded=True):
                st.markdown(q["explanation"])

            st.markdown("")
            c1, c2 = st.columns(2)
            with c1:
                if st.button(
                    "➡️ Next Question",
                    use_container_width=True,
                    type="primary",
                ):
                    with st.spinner("Loading…"):
                        nq = generate_quiz(st.session_state.topic, subject)
                        if nq:
                            st.session_state.quiz = nq
                            st.session_state.answered = False
                            st.session_state.picked = None
                            st.rerun()
                        else:
                            st.error("❌ Failed — try again.")
            with c2:
                if st.button("🔄 Change Topic", use_container_width=True):
                    reset_quiz()
                    st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                      📝  PAST PAPER MODE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

elif mode == "📝 Past Paper":

    pp_type = st.radio(
        "Question Type",
        ["📋 MC (Paper 1)", "✍️ Structured (Paper 2)"],
        horizontal=True,
        key="pp_type_radio",
    )
    st.markdown("")

    if pp_type == "📋 MC (Paper 1)":

        if st.session_state.pp_mc is None:
            if not st.session_state.topic:
                st.info(
                    f"📝 **Past Paper MC** — Enter a topic below.\n\n"
                    f"*e.g. {hint}*"
                )
            if prompt := st.chat_input(f"Topic for past paper MC? (e.g. {hint})"):
                st.session_state.topic = prompt
                with st.spinner("📝 Generating DSE Paper 1 MC…"):
                    q = generate_pp_mc(prompt, subject)
                    if q:
                        st.session_state.pp_mc = q
                        st.session_state.pp_mc_answered = False
                        st.session_state.pp_mc_picked = None
                        st.rerun()
                    else:
                        st.error("❌ Failed to generate — try again.")
        else:
            q = st.session_state.pp_mc

            year = q.get("year", "20XX")
            paper = q.get("paper", "Paper 1")
            qnum = q.get("qnum", "?")
            diff = q.get("difficulty", "medium")
            diff_map = {
                "easy": "🟢 Easy",
                "medium": "🟡 Medium",
                "hard": "🔴 Hard",
            }

            st.markdown(
                f"**{subject}** — {year} {paper}  \n"
                f"**Q{qnum}** &nbsp;|&nbsp; {diff_map.get(diff, '🟡 Medium')}"
            )
            st.markdown(f"### {q['question']}")
            st.markdown("")

            if not st.session_state.pp_mc_answered:
                cols = st.columns(2)
                for i, opt in enumerate(["A", "B", "C", "D"]):
                    with cols[i % 2]:
                        if st.button(
                            f"{opt}.  {q[opt]}",
                            key=f"pp_mc_{opt}",
                            use_container_width=True,
                        ):
                            st.session_state.pp_mc_picked = opt
                            st.session_state.pp_mc_answered = True
                            st.session_state.pp_mc_total += 1
                            if opt == q["answer"]:
                                st.session_state.pp_mc_score += 1
                            st.rerun()
            else:
                correct = q["answer"]
                picked = st.session_state.pp_mc_picked

                for opt in ["A", "B", "C", "D"]:
                    label = f"**{opt}.** {q[opt]}"
                    if opt == correct:
                        st.success(f"✅ {label}")
                    elif opt == picked and picked != correct:
                        st.error(f"❌ {label}")
                    else:
                        st.markdown(f"&emsp;⬜ {label}")

                st.markdown("")
                if picked == correct:
                    st.balloons()
                    st.success("🎉 **Correct!**")
                else:
                    st.error(f"😅 Wrong — Answer: **{correct}**")

                concept = q.get("concept", "")
                if concept:
                    st.caption(f"🎯 **Concept tested:** {concept}")

                with st.expander("📖 **Explanation**", expanded=True):
                    st.markdown(q["explanation"])

                st.markdown("")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(
                        "➡️ Next MC",
                        use_container_width=True,
                        type="primary",
                    ):
                        with st.spinner("Loading…"):
                            nq = generate_pp_mc(st.session_state.topic, subject)
                            if nq:
                                st.session_state.pp_mc = nq
                                st.session_state.pp_mc_answered = False
                                st.session_state.pp_mc_picked = None
                                st.rerun()
                            else:
                                st.error("❌ Failed — try again.")
                with c2:
                    if st.button(
                        "🔄 Change Topic",
                        key="pp_mc_ct",
                        use_container_width=True,
                    ):
                        reset_pp_mc()
                        st.rerun()

    else:

        if st.session_state.pp_question is None:
            if not st.session_state.topic:
                st.info(
                    f"✍️ **Structured Question** — Enter a topic below.\n\n"
                    f"*e.g. {hint}*"
                )
            if prompt := st.chat_input(f"Topic for structured Q? (e.g. {hint})"):
                st.session_state.topic = prompt
                with st.spinner("📝 Generating DSE structured question…"):
                    q_text = generate_pp_long(prompt, subject)
                    if q_text:
                        st.session_state.pp_question = q_text
                        st.session_state.pp_answer = None
                        st.session_state.pp_show_answer = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to generate — try again.")
        else:
            st.markdown(st.session_state.pp_question)
            st.divider()

            if not st.session_state.pp_show_answer:
                st.markdown("### ✏️ Your Answer Space")
                st.caption(
                    "Write your answer below (or on paper), "
                    "then check the marking scheme."
                )

                st.text_area(
                    "Type your answer here:",
                    height=200,
                    placeholder="(a) …\n\n(b) …\n\n(c) …",
                    key="student_answer_box",
                )

                st.markdown("")
                if st.button(
                    "📋 Show Marking Scheme & Model Answer",
                    use_container_width=True,
                    type="primary",
                ):
                    if st.session_state.pp_answer is None:
                        with st.spinner("📋 Generating marking scheme…"):
                            ans = generate_marking(
                                st.session_state.pp_question, subject
                            )
                            if ans:
                                st.session_state.pp_answer = ans
                                st.session_state.pp_show_answer = True
                                st.rerun()
                            else:
                                st.error("❌ Failed — try again.")
                    else:
                        st.session_state.pp_show_answer = True
                        st.rerun()
            else:
                st.markdown("### ✅ Marking Scheme & Model Answer")
                st.markdown(st.session_state.pp_answer)

            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                if st.button(
                    "🆕 New Question (Same Topic)",
                    use_container_width=True,
                    type="primary",
                ):
                    with st.spinner("Generating…"):
                        q_text = generate_pp_long(
                            st.session_state.topic, subject
                        )
                        if q_text:
                            st.session_state.pp_question = q_text
                            st.session_state.pp_answer = None
                            st.session_state.pp_show_answer = False
                            st.rerun()
                        else:
                            st.error("❌ Failed — try again.")
            with c2:
                if st.button(
                    "🔄 Change Topic",
                    key="pp_long_ct",
                    use_container_width=True,
                ):
                    reset_pp_long()
                    st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                    📋  STUDY PLANNER MODE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

elif mode == "📋 Study Planner":

    if st.session_state.plan is None:
        st.markdown("### 📅 Build Your Personal DSE Study Plan")
        st.caption(
            "Fill in your details — Athena will create a "
            "week-by-week roadmap just for you."
        )
        st.markdown("")

        with st.form("planner_form"):
            subjects_taken = st.multiselect(
                "📘 Which subjects are you taking?",
                list(SUBJECTS.keys()),
                default=[
                    "📐 Mathematics",
                    "📖 English",
                    "✍️ Chinese 中文",
                    "🏛️ Citizenship 公民科",
                ],
            )

            st.markdown("")

            col_a, col_b = st.columns(2)
            with col_a:
                exam_date = st.date_input(
                    "📅 When is your DSE?",
                    value=datetime.now() + timedelta(days=120),
                    min_value=datetime.now().date(),
                )
            with col_b:
                hours = st.slider("⏰ Study hours per day", 1, 14, 4)

            days_left = (exam_date - datetime.now().date()).days
            if days_left > 0:
                st.caption(f"⏳ That's **{days_left} days** from today.")

            st.markdown("")

            weak = st.text_area(
                "😰 Your weakest areas (be as specific as possible!)",
                placeholder=(
                    "e.g. Organic Chemistry naming conventions, English "
                    "Paper 2 argumentative essays, M2 integration by "
                    "parts, Chinese classical passages (文言文)…"
                ),
                height=100,
            )

            extra = st.text_area(
                "📝 Anything else Athena should know? (optional)",
                placeholder=(
                    "e.g. Tutorial on Wed & Fri, I want 5** in Physics, "
                    "I procrastinate with Chinese, I study better at "
                    "night, mock exams in March…"
                ),
                height=100,
            )

            st.markdown("")
            submitted = st.form_submit_button(
                "🚀 Generate My Study Plan",
                use_container_width=True,
            )

        if submitted:
            if not subjects_taken:
                st.error("⚠️ Please select at least one subject.")
            elif not weak.strip():
                st.error(
                    "⚠️ Tell Athena your weak areas — "
                    "this is essential for a good plan!"
                )
            elif exam_date <= datetime.now().date():
                st.error("⚠️ Exam date must be in the future.")
            else:
                sub_names = ", ".join(subjects_taken)
                with st.spinner(
                    "🏛️ Athena is building your plan… (this may take a moment)"
                ):
                    plan = generate_plan(
                        sub_names,
                        exam_date,
                        hours,
                        weak.strip(),
                        extra.strip() if extra.strip() else "None provided",
                    )
                    if plan:
                        st.session_state.plan = plan
                        st.rerun()
                    else:
                        st.error("❌ Failed to generate — please try again.")

    else:
        st.markdown("### 📅 Your Personal DSE Study Plan")
        st.markdown("")
        st.markdown(st.session_state.plan)
        st.divider()

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔄 New Plan", use_container_width=True):
                st.session_state.plan = None
                st.rerun()
        with c2:
            st.download_button(
                label="💾 Download .txt",
                data=st.session_state.plan,
                file_name=f"athena_study_plan_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with c3:
            st.download_button(
                label="📄 Download .md",
                data=st.session_state.plan,
                file_name=f"athena_study_plan_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True,
            )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                           FOOTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("")
st.markdown("")
st.divider()
st.caption(
    "🏛️ **Athena AI** v2.1 — Built for DSE students, "
    "by a DSE student. &nbsp;|&nbsp; Powered by Groq AI"
)