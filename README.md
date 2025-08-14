# Anime Role-Play Chatbot

A polished Streamlit chat UI to talk with your favorite anime characters using Groq models.

## Quick start

1. Create a `.env` file with your Groq API key (or paste it in the app sidebar):
   
   GROQ_API_KEY=sk_your_key_here

2. Install dependencies (if needed):
   
   pip install -r requirements.txt --break-system-packages

3. Run the app:
   
   streamlit run app.py

Then open http://localhost:8501 in your browser.

## Features

- Chat-style UI with history preserved per session
- Easy character switching (Naruto, Luffy, Goku) with persona prompts
- Model selection: LLaMA 3 70B (quality) or Mixtral 8x7B (fast)
- Streaming responses with graceful fallback
- Adjustable creativity (temperature) slider
- One-click “Clear chat” to reset context

## Notes

- You can provide `GROQ_API_KEY` via `.env` or the sidebar input.
- The app uses `langchain_groq.ChatGroq` under the hood.