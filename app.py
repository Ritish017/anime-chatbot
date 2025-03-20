import os
from dotenv import find_dotenv , load_dotenv

_ = load_dotenv(find_dotenv())
import streamlit as st
from langchain_groq import ChatGroq
from prompts import character_prompts

llamaChatModel = ChatGroq(model="llama3-70b-8192")
MistralChatModel = ChatGroq(model="mixtral-8x7b-32768")

st.title("Anime Role-Based ChatBot")
st.markdown("Chat with your favorite anime characters and enjoy immersive conversations")


selected_character = st.selectbox(
    "Choose your anime character:", list(character_prompts.keys())

)

user_input = st.text_area(f"Ask {selected_character} something:")

selected_model = st.radio(
    "Choose a Model:",
    ["LLaMa 3 (More natural Responses)", "Mistral (Faster and efficient)"],
    index=0
)

chat_model = llamaChatModel if "LLaMa" in selected_model else MistralChatModel


if st.button("Get response"):
    if user_input.strip():
        prompt = (
            f"{character_prompts[selected_character]}\n"
            f"Human: {user_input}\n"
            f"{selected_character}:"
        )
    
    try:
        response = chat_model.invoke([("system",prompt), ("human",user_input)])
        st.success(f"**{selected_character}** says: {response.content}")
    except Exception as e:
        st.error("Ask your Fav Character something")
        st.text(f"Error details :{e}")
        
    else:
        st.warning("Please enter a question for the character")  
st.markdown("---")
st.markdown("💬 *Anime Role-Play Chatbot by Kurma Ritish*")
