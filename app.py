import streamlit as st
from PyPDF2 import PdfReader

import os
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
# from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from ui import init_session_state, render_chat_ui, handle_user_input


# Load the environment variable
load_dotenv()

# Streamlit UI or Page config
st.set_page_config(page_title="Multi-PDF Chatbot", page_icon="📄")
st.header("📄 Chat with Multiple PDFs")

# Upload PDF files
with st.sidebar:
    st.title("Your Documents")
    all_files = st.file_uploader(
        "Upload one or more PDF files",
        type="pdf",
        accept_multiple_files=True,
        help="⚠️ Uploaded documents are used only for the current session and are not saved."
    )

# ---------- Initialize session state ----------
init_session_state()

# ---------- Process PDFs ----------

# Extract the text (Read PDF)
if all_files is None or len(all_files) == 0:
    st.info("Please upload one or more PDF files to start chatting.")
    st.stop()

if all_files is not None:
    all_text = ""
    # 🔹 Read ALL PDFs
    for pdf in all_files:
        reader = PdfReader(pdf)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                all_text += page_text

    # Important Check (Weather the text is present or not in the PDFs)
    if not all_text.strip():
        st.error("No readable text found in the uploaded PDFS.")
        st.stop()

        # text is successfully extracted
        # st.write(all_text)

    # Break(Slpit) text into chunks (Text Splitting)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 100
    )

    chunks = text_splitter.split_text(all_text)

    # Important check
    if not chunks:
        st.error("No text chunks found. Please upload a valid document.")
        st.stop()
    # st.write(chunks)

# Generating embedding (HuggingFace Embeddings)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

# Generating vector store  -  FAISS
    vector_store = FAISS.from_texts(chunks, embeddings)
    # '''
    #     Above line done three steps which are follows:-
    #     - embeddings (OpenAI)
    #     - initizling FAISS
    #     - store chunks & embeddings
    # '''

    st.success("Documents processed successfully. You can start chatting!")

# Do similarity search
    # ---------------- Create Conversation Chain (ONCE) ----------------
    if st.session_state.conversation is None:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0,
            convert_system_message_to_human=True
        )

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        st.session_state.conversation = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vector_store.as_retriever(),
            memory=memory
        )

        # ----------- Chat UI ---------------
    if st.session_state.conversation:
        render_chat_ui()
        handle_user_input()