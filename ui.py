import streamlit as st

def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

def render_chat_ui():
    """
        Render previous chat message 
    """

    for question, answer in st.session_state.chat_history:
        with st.chat_message("user", avatar="👤"):
            st.markdown(question)

        with st.chat_message("ChatBot", avatar="✨"):
            st.markdown(answer)

def handle_user_input():
    """
        Handles user input and chatbot response
    """

    # Get the User question
    user_question = st.chat_input("Ask something about your documents...")

    if user_question and st.session_state.conversation:
        # Show user message immediately
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_question)

        # Get responce
        respose = st.session_state.conversation(
            {"question": user_question}
        )

        # Show ChatBot response
        with st.chat_message("ChatBot", avatar="✨"):
            st.markdown(respose["answer"])

        # Save chat history
        st.session_state.chat_history.append(
            (user_question, respose["answer"])
        )