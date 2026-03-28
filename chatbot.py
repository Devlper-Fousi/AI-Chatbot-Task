import streamlit as st
import google.generativeai as genai
import os


# --- CONFIGURATION ---
# Replace with your actual Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")

# --- PROMPT ENGINEERING ---
# Requirement: Context-aware prompt with hallucination checks [cite: 17, 19, 20]
SYSTEM_PROMPT = """
You are a helpful, context-aware AI assistant. 
1. Maintain continuity by referencing previous parts of the conversation.
2. If you are unsure or the user's prompt is ambiguous, ask for clarification.
3. Do not make up facts; if the information isn't available, state that you don't know[cite: 19].
4. Avoid repeating previous answers unless asked to elaborate[cite: 6].
"""

st.set_page_config(page_title="AI Intern Assignment - ZenturioTech")
st.title("Context-Aware Chatbot")

# --- MEMORY MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TOKEN OPTIMIZATION / CONTEXT WINDOW  ---
MAX_CONTEXT_LENGTH = 10 

def get_optimized_history():
    return st.session_state.messages[-MAX_CONTEXT_LENGTH:]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT LOGIC ---
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-3-flash-preview')
            
            # Formatting the sliding window history for the LLM 
            formatted_history = [{"role": m["role"], "parts": [m["content"]]} for m in get_optimized_history()]
            
            # Prepend system instructions
            response = model.generate_content(
                contents=[{"role": "user", "parts": [SYSTEM_PROMPT]}] + formatted_history
            )
            
            full_response = response.text
            st.markdown(full_response)
            
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
