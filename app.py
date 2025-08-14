import os
from typing import List, Dict, Any, Tuple

from dotenv import find_dotenv, load_dotenv

# Load environment variables early
_ = load_dotenv(find_dotenv())

import streamlit as st
from langchain_groq import ChatGroq
from prompts import character_prompts


# -----------------------------
# Page config and styling
# -----------------------------
st.set_page_config(
    page_title="Anime Role-Based Chatbot",
    page_icon="🎭",
    layout="wide",
)

_CUSTOM_CSS = """
<style>
/***** Hero header *****/
.hero {
  padding: 1rem 1.25rem;
  border-radius: 14px;
  margin-bottom: 0.5rem;
  background: linear-gradient(90deg, #f97316 0%, #ef4444 25%, #8b5cf6 65%, #06b6d4 100%);
  color: white;
}
.hero h1 { font-size: 1.6rem; margin: 0; }
.hero p { margin: 0.25rem 0 0 0; opacity: 0.95; }

/***** Tighten chat spacing *****/
.block-container { padding-top: 1.2rem; }

/***** Subtle code style for small captions *****/
.small { opacity: 0.85; font-size: 0.9rem; }
</style>
"""

st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)

# Character avatars for the chat bubbles
CHAR_AVATARS: Dict[str, str] = {
    "Naruto Uzumaki": "🌀",
    "Monkey D. Luffy": "🏴\u200d☠️",
    "Son Goku": "⚡",
}


# -----------------------------
# Session state initialization
# -----------------------------
def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, Any]] = []
    if "selected_character" not in st.session_state:
        # Default to the first character in prompts
        st.session_state.selected_character = list(character_prompts.keys())[0]
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "llama3-70b-8192"  # quality default
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7


init_session_state()


# -----------------------------
# Sidebar: settings & controls
# -----------------------------
with st.sidebar:
    st.markdown("### Settings")

    # API key input (session-only)
    api_key_input = st.text_input(
        "GROQ API Key",
        type="password",
        placeholder="sk_...",
        help="Used only for this session. You can also set GROQ_API_KEY in a .env file.",
    )

    model_friendly_to_id: Dict[str, str] = {
        "LLaMA 3 70B (quality)": "llama3-70b-8192",
        "Mixtral 8x7B (fast)": "mixtral-8x7b-32768",
    }
    model_friendly_names: List[str] = list(model_friendly_to_id.keys())
    # Keep the select consistent with current state
    default_model_idx = (
        model_friendly_names.index("LLaMA 3 70B (quality)")
        if st.session_state.selected_model == "llama3-70b-8192"
        else model_friendly_names.index("Mixtral 8x7B (fast)")
    )
    model_label = st.selectbox("Model", model_friendly_names, index=default_model_idx)
    st.session_state.selected_model = model_friendly_to_id[model_label]

    st.session_state.temperature = st.slider(
        "Creativity (temperature)", 0.0, 1.0, float(st.session_state.temperature), 0.05
    )

    # Character selection
    character_names: List[str] = list(character_prompts.keys())
    current_character_idx = character_names.index(st.session_state.selected_character)
    selected_character = st.selectbox("Character", character_names, index=current_character_idx)

    # Warn about persona change in the middle of a chat
    if selected_character != st.session_state.selected_character and st.session_state.messages:
        st.info("Character changed. Click 'Clear chat' to start a fresh conversation with the new persona.")
    st.session_state.selected_character = selected_character

    # Clear chat
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()


# -----------------------------
# Helpers
# -----------------------------
def ensure_api_key(input_key: str | None) -> bool:
    key = input_key or os.getenv("GROQ_API_KEY")
    if key:
        os.environ["GROQ_API_KEY"] = key
        return True
    return False


def build_model(model_name: str, temperature: float) -> ChatGroq:
    return ChatGroq(model=model_name, temperature=temperature)


def to_lc_messages(persona: str, history: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    messages: List[Tuple[str, str]] = [("system", persona)]
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        # Map streamlit roles to LangChain chat roles
        if role == "user":
            messages.append(("human", content))
        elif role == "assistant":
            messages.append(("ai", content))
        elif role == "system":
            messages.append(("system", content))
    return messages


# -----------------------------
# Main content
# -----------------------------
st.markdown(
    """
<div class="hero">
  <h1>Anime Role-Play Chatbot</h1>
  <p>Chat with your favorite anime characters and enjoy immersive conversations.</p>
</div>
    """,
    unsafe_allow_html=True,
)

# Show past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get("avatar")):
        st.markdown(message["content"]) 

# Chat input prompt
chat_placeholder = f"Ask {st.session_state.selected_character} something..."
user_text = st.chat_input(chat_placeholder)

if user_text:
    # Append user message immediately
    st.session_state.messages.append({
        "role": "user",
        "content": user_text,
        "avatar": "👤",
    })

    # Ensure API key available
    if not ensure_api_key(api_key_input):
        with st.chat_message("assistant", avatar=CHAR_AVATARS.get(st.session_state.selected_character, "🤖")):
            st.error("GROQ_API_KEY is missing. Add it in the sidebar or in your .env file.")
    else:
        # Prepare model and persona
        persona_prompt = character_prompts[st.session_state.selected_character].strip()
        lc_messages = to_lc_messages(persona_prompt, st.session_state.messages)
        model = build_model(st.session_state.selected_model, float(st.session_state.temperature))

        assistant_avatar = CHAR_AVATARS.get(st.session_state.selected_character, "🤖")
        with st.chat_message("assistant", avatar=assistant_avatar):
            stream_placeholder = st.empty()
            full_response = ""

            # Try streaming first; fallback to single invoke
            try:
                for chunk in model.stream(lc_messages):
                    full_response += getattr(chunk, "content", "") or ""
                    stream_placeholder.markdown(full_response)
            except Exception:
                try:
                    response = model.invoke(lc_messages)
                    full_response = getattr(response, "content", "")
                    stream_placeholder.markdown(full_response)
                except Exception as e:
                    st.error("Something went wrong while generating a response.")
                    st.caption(str(e))
                    full_response = ""

            if full_response:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "avatar": assistant_avatar,
                })

# Footer / credit
st.markdown("---")
st.caption("💬 Anime Role-Play Chatbot by Kurma Ritish — powered by Groq")
