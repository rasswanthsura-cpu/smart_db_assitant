import base64
import html
import time
from pathlib import Path

import streamlit as st

from app import ask_db


st.set_page_config(
    page_title="AI DB Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


WELCOME_MESSAGE = (
    "Neural database link established. Ask anything about the movies table "
    "and I will translate it into a database-ready answer."
)
BACKGROUND_IMAGE_PATH = (
    Path(__file__).resolve().parent / "assets" / "database_background.svg"
)


def get_background_image() -> str:
    try:
        svg_content = BACKGROUND_IMAGE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "none"

    encoded_svg = base64.b64encode(svg_content.encode("utf-8")).decode("ascii")
    return f'url("data:image/svg+xml;base64,{encoded_svg}")'


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --database-bg: {get_background_image()};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        :root {
            --bg-1: #040816;
            --bg-2: #091126;
            --panel: rgba(9, 15, 34, 0.62);
            --panel-strong: rgba(10, 18, 40, 0.78);
            --stroke: rgba(117, 214, 255, 0.18);
            --stroke-strong: rgba(117, 214, 255, 0.34);
            --cyan: #65f0ff;
            --blue: #38a8ff;
            --blue-bright: #7ad8ff;
            --text: #edf6ff;
            --muted: #96accf;
            --shadow: 0 24px 60px rgba(1, 6, 20, 0.45);
        }

        html, body, [class*="css"] {
            font-family: "Bahnschrift", "Segoe UI Variable", "Segoe UI", sans-serif;
        }

        .stApp {
            color: var(--text);
            background-image:
                var(--database-bg),
                radial-gradient(circle at 18% 20%, rgba(101, 240, 255, 0.12), transparent 28%),
                radial-gradient(circle at 82% 12%, rgba(56, 168, 255, 0.14), transparent 30%),
                radial-gradient(circle at 50% 78%, rgba(53, 127, 255, 0.16), transparent 36%),
                linear-gradient(135deg, rgba(4, 8, 22, 0.92) 0%, rgba(9, 17, 38, 0.82) 46%, rgba(3, 6, 17, 0.96) 100%);
            background-position: center center;
            background-size: cover, auto, auto, auto, auto;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: -20%;
            background:
                radial-gradient(circle at 30% 30%, rgba(101, 240, 255, 0.18), transparent 24%),
                radial-gradient(circle at 68% 30%, rgba(56, 168, 255, 0.18), transparent 26%),
                radial-gradient(circle at 50% 70%, rgba(53, 127, 255, 0.2), transparent 28%);
            filter: blur(70px);
            animation: orb-float 14s ease-in-out infinite alternate;
            pointer-events: none;
            z-index: 0;
        }

        .stApp::after {
            content: "";
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(rgba(101, 240, 255, 0.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(56, 168, 255, 0.07) 1px, transparent 1px);
            background-size: 120px 120px;
            mask-image: radial-gradient(circle at center, black 28%, transparent 78%);
            opacity: 0.26;
            animation: grid-drift 24s linear infinite;
            pointer-events: none;
            z-index: 0;
        }

        [data-testid="stAppViewContainer"] > .main,
        [data-testid="stSidebar"] {
            position: relative;
            z-index: 1;
        }

        [data-testid="stHeader"] {
            background: rgba(0, 0, 0, 0);
        }

        [data-testid="stToolbar"] {
            right: 1rem;
        }

        .block-container {
            max-width: 1040px;
            padding-top: 2.2rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] > div:first-child {
            background:
                linear-gradient(180deg, rgba(6, 11, 25, 0.95), rgba(7, 12, 28, 0.82)),
                radial-gradient(circle at top, rgba(101, 240, 255, 0.12), transparent 55%);
            border-right: 1px solid rgba(117, 214, 255, 0.14);
            box-shadow: 12px 0 36px rgba(0, 0, 0, 0.28);
        }

        .sidebar-shell,
        .sidebar-card {
            background: linear-gradient(180deg, rgba(11, 18, 40, 0.76), rgba(7, 13, 30, 0.58));
            border: 1px solid var(--stroke);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            box-shadow: var(--shadow);
        }

        .sidebar-shell {
            border-radius: 26px;
            padding: 1.1rem 1rem;
            margin-bottom: 1rem;
        }

        .sidebar-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text);
            letter-spacing: 0.04em;
            margin-bottom: 0.35rem;
        }

        .sidebar-subtitle {
            color: var(--muted);
            font-size: 0.95rem;
            line-height: 1.6;
        }

        .sidebar-card {
            border-radius: 22px;
            padding: 0.95rem 1rem;
            margin-bottom: 0.85rem;
        }

        .sidebar-label {
            color: var(--cyan);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }

        .sidebar-card p,
        .sidebar-card li {
            color: var(--text);
            margin: 0;
            line-height: 1.6;
        }

        .sidebar-card ul {
            margin: 0;
            padding-left: 1rem;
        }

        .hero-panel {
            background: linear-gradient(180deg, rgba(11, 18, 40, 0.14), rgba(7, 13, 30, 0.04)) !important;
            border: 1px solid rgba(117, 214, 255, 0.18) !important;
            backdrop-filter: blur(10px) saturate(160%) !important;
            -webkit-backdrop-filter: blur(10px) saturate(160%) !important;
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.12),
                0 18px 42px rgba(1, 6, 20, 0.12) !important;
            border-radius: 32px;
            padding: 1.5rem 1.6rem;
            margin-bottom: 1.5rem;
            overflow: hidden;
            position: relative;
            isolation: isolate;
        }

        .hero-panel::before {
            content: "";
            position: absolute;
            inset: auto -20% -35% auto;
            width: 260px;
            height: 260px;
            background: radial-gradient(circle, rgba(101, 240, 255, 0.18), transparent 65%);
            filter: blur(10px);
            animation: pulse-glow 5s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }

        .hero-panel::after {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.01) 36%, rgba(255, 255, 255, 0));
            pointer-events: none;
            z-index: 1;
        }

        .hero-panel > * {
            position: relative;
            z-index: 2;
        }

        .eyebrow {
            color: var(--cyan);
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.22em;
            margin-bottom: 0.55rem;
        }

        .hero-title {
            margin: 0;
            font-size: clamp(2.2rem, 4.3vw, 4rem);
            line-height: 1.05;
            letter-spacing: 0.04em;
            background: linear-gradient(90deg, #e6fdff 0%, #6cf4ff 26%, #81d5ff 55%, #38a8ff 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-shadow: 0 0 24px rgba(101, 240, 255, 0.18);
            animation: title-shimmer 8s linear infinite;
        }

        .hero-subtitle {
            margin-top: 0.85rem;
            margin-bottom: 1rem;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.7;
            max-width: 760px;
        }

        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem;
            margin-top: 1rem;
        }

        .chip {
            border-radius: 999px;
            border: 1px solid rgba(117, 214, 255, 0.16);
            padding: 0.42rem 0.85rem;
            color: var(--text);
            background: rgba(13, 22, 48, 0.62);
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.02);
            font-size: 0.88rem;
        }

        .section-label {
            color: var(--cyan);
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.22em;
            margin: 0.2rem 0 0.9rem;
            padding-left: 0.25rem;
        }

        .message-row {
            display: flex;
            gap: 0.85rem;
            align-items: flex-end;
            margin-bottom: 1rem;
            animation: message-enter 0.45s ease both;
        }

        .assistant-row {
            justify-content: flex-start;
        }

        .user-row {
            justify-content: flex-end;
        }

        .user-row .avatar {
            order: 2;
        }

        .user-row .message-card {
            order: 1;
        }

        .avatar {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            flex: 0 0 auto;
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            box-shadow: 0 14px 28px rgba(0, 0, 0, 0.28);
        }

        .assistant-avatar {
            background: linear-gradient(135deg, rgba(14, 31, 56, 0.9), rgba(16, 68, 112, 0.68));
            box-shadow: 0 0 24px rgba(101, 240, 255, 0.18);
        }

        .user-avatar {
            background: linear-gradient(135deg, rgba(8, 33, 66, 0.9), rgba(22, 96, 160, 0.68));
            box-shadow: 0 0 24px rgba(56, 168, 255, 0.18);
        }

        .message-card {
            max-width: min(78%, 760px);
            border-radius: 24px;
            border: 1px solid var(--stroke);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            box-shadow: var(--shadow);
            padding: 0.95rem 1rem 1rem;
            position: relative;
            overflow: hidden;
        }

        .message-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0));
            pointer-events: none;
        }

        .assistant-card {
            background: linear-gradient(180deg, rgba(11, 21, 44, 0.78), rgba(7, 14, 31, 0.62));
        }

        .user-card {
            background: linear-gradient(180deg, rgba(10, 30, 58, 0.8), rgba(11, 26, 52, 0.66));
            border-color: rgba(56, 168, 255, 0.24);
        }

        .message-meta {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.55rem;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--muted);
        }

        .message-tag {
            padding: 0.2rem 0.48rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.05);
            color: var(--text);
            font-size: 0.68rem;
        }

        .message-text {
            color: var(--text);
            font-size: 1rem;
            line-height: 1.75;
            word-break: break-word;
        }

        .thinking-card {
            min-width: 220px;
        }

        .thinking-dots {
            display: flex;
            gap: 0.45rem;
            padding: 0.2rem 0 0.2rem;
        }

        .thinking-dots span {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--cyan), var(--blue));
            box-shadow: 0 0 16px rgba(101, 240, 255, 0.35);
            animation: thinking 1.1s infinite ease-in-out;
        }

        .thinking-dots span:nth-child(2) {
            animation-delay: 0.15s;
        }

        .thinking-dots span:nth-child(3) {
            animation-delay: 0.3s;
        }

        form[data-testid="stForm"],
        div[data-testid="stForm"] {
            background: linear-gradient(180deg, rgba(10, 18, 40, 0.72), rgba(8, 14, 30, 0.64));
            border: 1px solid var(--stroke);
            border-radius: 28px;
            padding: 1rem 1rem 0.4rem;
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            box-shadow: var(--shadow);
        }

        div[data-baseweb="input"] > div {
            min-height: 54px;
            background: rgba(6, 12, 28, 0.82);
            border: 1px solid rgba(117, 214, 255, 0.12);
            border-radius: 18px;
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.015);
            transition: border-color 0.24s ease, box-shadow 0.24s ease, transform 0.24s ease;
        }

        div[data-baseweb="input"]:focus-within > div {
            border-color: rgba(101, 240, 255, 0.65);
            box-shadow:
                0 0 0 1px rgba(101, 240, 255, 0.2),
                0 0 26px rgba(101, 240, 255, 0.22),
                inset 0 0 0 1px rgba(255, 255, 255, 0.02);
            transform: translateY(-1px);
        }

        div[data-baseweb="input"] input {
            color: var(--text) !important;
            caret-color: var(--cyan);
            font-size: 1rem;
        }

        div[data-baseweb="input"] input::placeholder {
            color: rgba(150, 172, 207, 0.76);
        }

        .stButton button,
        div[data-testid="stFormSubmitButton"] button {
            min-height: 54px;
            border-radius: 18px;
            border: 1px solid rgba(101, 240, 255, 0.18);
            color: #041221;
            font-weight: 700;
            background: linear-gradient(135deg, var(--cyan), var(--blue-bright) 52%, var(--blue) 100%);
            box-shadow: 0 16px 30px rgba(9, 22, 55, 0.34);
            transition: transform 0.22s ease, box-shadow 0.22s ease, filter 0.22s ease;
        }

        .stButton button:hover,
        div[data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-2px) scale(1.01);
            box-shadow: 0 18px 36px rgba(101, 240, 255, 0.22);
            filter: brightness(1.03);
        }

        .stButton button:focus,
        div[data-testid="stFormSubmitButton"] button:focus {
            outline: none;
            box-shadow:
                0 0 0 1px rgba(255, 255, 255, 0.18),
                0 0 24px rgba(101, 240, 255, 0.22);
        }

        .footer-note {
            color: var(--muted);
            text-align: center;
            font-size: 0.92rem;
            margin-top: 1.15rem;
        }

        .footer-note code {
            color: var(--cyan);
            background: rgba(255, 255, 255, 0.04);
            padding: 0.14rem 0.35rem;
            border-radius: 8px;
        }

        @keyframes orb-float {
            0% { transform: translate3d(-2%, -3%, 0) scale(1); }
            50% { transform: translate3d(3%, 2%, 0) scale(1.06); }
            100% { transform: translate3d(-1%, 4%, 0) scale(0.98); }
        }

        @keyframes grid-drift {
            0% { transform: translate3d(0, 0, 0); }
            50% { transform: translate3d(-26px, 18px, 0); }
            100% { transform: translate3d(0, 0, 0); }
        }

        @keyframes message-enter {
            from {
                opacity: 0;
                transform: translateY(14px) scale(0.985);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        @keyframes thinking {
            0%, 80%, 100% {
                transform: translateY(0);
                opacity: 0.45;
            }
            40% {
                transform: translateY(-6px);
                opacity: 1;
            }
        }

        @keyframes pulse-glow {
            0%, 100% {
                opacity: 0.45;
                transform: scale(1);
            }
            50% {
                opacity: 0.9;
                transform: scale(1.08);
            }
        }

        @keyframes title-shimmer {
            0% {
                filter: drop-shadow(0 0 8px rgba(101, 240, 255, 0.1));
            }
            50% {
                filter: drop-shadow(0 0 18px rgba(56, 168, 255, 0.16));
            }
            100% {
                filter: drop-shadow(0 0 8px rgba(101, 240, 255, 0.1));
            }
        }

        @media (max-width: 900px) {
            .block-container {
                padding-top: 1.2rem;
            }

            .hero-panel {
                padding: 1.2rem 1.1rem;
                border-radius: 24px;
            }

            .message-card {
                max-width: 100%;
            }

            .message-row {
                gap: 0.7rem;
            }

            .avatar {
                width: 40px;
                height: 40px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_session() -> None:
    if "history" not in st.session_state:
        st.session_state.history = [
            {"role": "assistant", "content": WELCOME_MESSAGE, "animate": False}
        ]
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None


def reset_chat() -> None:
    st.session_state.history = [
        {"role": "assistant", "content": WELCOME_MESSAGE, "animate": False}
    ]
    st.session_state.pending_query = None


def format_message(text: str) -> str:
    return html.escape(str(text)).replace("\n", "<br>")


def build_message(role: str, content: str) -> str:
    is_user = role == "user"
    row_class = "user-row" if is_user else "assistant-row"
    card_class = "user-card" if is_user else "assistant-card"
    avatar_class = "user-avatar" if is_user else "assistant-avatar"
    avatar = "🧑" if is_user else "🤖"
    title = "You" if is_user else "AI Core"
    tag = "Command" if is_user else "Response"

    return f"""
    <div class="message-row {row_class}">
        <div class="avatar {avatar_class}">{avatar}</div>
        <div class="message-card {card_class}">
            <div class="message-meta">
                <span>{title}</span>
                <span class="message-tag">{tag}</span>
            </div>
            <div class="message-text">{format_message(content)}</div>
        </div>
    </div>
    """


def build_thinking_message() -> str:
    return """
    <div class="message-row assistant-row">
        <div class="avatar assistant-avatar">🤖</div>
        <div class="message-card assistant-card thinking-card">
            <div class="message-meta">
                <span>AI Core</span>
                <span class="message-tag">Thinking...</span>
            </div>
            <div class="thinking-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    </div>
    """


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-shell">
                <div class="sidebar-title">AI DB Assistant</div>
                <div class="sidebar-subtitle">
                    Futuristic natural-language control panel for your movies database.
                    Type a question, let the AI translate intent, and get answers back in a clean chat flow.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="sidebar-card">
                <div class="sidebar-label">System Status</div>
                <p>Neural UI online</p>
                <p>Backend bridge locked to <strong>ask_db(query)</strong></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="sidebar-card">
                <div class="sidebar-label">Quick Ideas</div>
                <ul>
                    <li>Show the top rated movies</li>
                    <li>List movies released after 2010</li>
                    <li>Which movie has the highest IMDb rating?</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Clear conversation", use_container_width=True):
            reset_chat()
            st.rerun()


def render_header() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <div class="eyebrow">Neural Query Interface</div>
            <h1 class="hero-title">AI Database Assistant</h1>
            <div class="hero-subtitle">
                A Jarvis-style control surface for your movie data. Ask in plain English,
                keep the database logic intact, and let the interface handle the atmosphere.
            </div>
            <div class="chip-row">
                <span class="chip">Live SQL reasoning</span>
                <span class="chip">Glassmorphism UI</span>
                <span class="chip">Animated response flow</span>
                <span class="chip">Movies DB ready</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def animate_message(index: int) -> None:
    placeholder = st.empty()
    content = str(st.session_state.history[index]["content"])
    length = len(content)
    step = 1 if length <= 220 else 2 if length <= 520 else 4
    delay = 0.012 if length <= 220 else 0.007 if length <= 520 else 0.004

    for cursor in range(0, length + step, step):
        placeholder.markdown(
            build_message("assistant", content[:cursor]),
            unsafe_allow_html=True,
        )
        time.sleep(delay)

    st.session_state.history[index]["animate"] = False


def render_chat(pending_query: str | None) -> None:
    st.markdown(
        '<div class="section-label">Conversation Matrix</div>',
        unsafe_allow_html=True,
    )

    for index, message in enumerate(st.session_state.history):
        if message["role"] == "assistant" and message.get("animate"):
            animate_message(index)
        else:
            st.markdown(
                build_message(message["role"], message["content"]),
                unsafe_allow_html=True,
            )

    if pending_query:
        thinking_slot = st.empty()
        thinking_slot.markdown(build_thinking_message(), unsafe_allow_html=True)
        response = ask_db(pending_query)
        thinking_slot.empty()

        st.session_state.history.append(
            {"role": "assistant", "content": str(response), "animate": True}
        )
        st.session_state.pending_query = None
        st.rerun()


def render_input() -> None:
    st.markdown(
        '<div class="section-label">Prompt Console</div>',
        unsafe_allow_html=True,
    )

    with st.form("chat_form", clear_on_submit=True):
        input_col, button_col = st.columns([5, 1])

        with input_col:
            user_query = st.text_input(
                "Ask a database question",
                placeholder=(
                    "Ask about counts, ratings, release years, top movies, or anything else..."
                ),
                label_visibility="collapsed",
            )

        with button_col:
            submitted = st.form_submit_button("Send", use_container_width=True)

    if submitted:
        cleaned_query = user_query.strip()
        if cleaned_query:
            st.session_state.history.append(
                {"role": "user", "content": cleaned_query, "animate": False}
            )
            st.session_state.pending_query = cleaned_query
            st.rerun()

        st.warning("Enter a question before sending it to the assistant.")


inject_styles()
init_session()
render_sidebar()

center_column = st.columns([0.08, 0.84, 0.08])[1]
pending_query = st.session_state.pending_query

with center_column:
    render_header()
    render_chat(pending_query)
    render_input()
    st.markdown(
        '<div class="footer-note">Backend preserved exactly through <code>ask_db(query)</code>.</div>',
        unsafe_allow_html=True,
    )
#python -m streamlit run app_ui.py
