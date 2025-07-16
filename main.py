import streamlit as st
from logic import initialize_db, handle_file_changes, handle_user_query


def main():
    st.set_page_config(page_title="Multi-Doc Chatbot", layout="wide")
    st.title("Multi-Document Chatbot")
    
    # Initialize Vector DB only once
    if "vectordb" not in st.session_state:
        st.session_state.vectordb = initialize_db()

    # Track uploaded filenames in session state
    if "uploaded_file_names" not in st.session_state:
        st.session_state.uploaded_file_names = []

    # Track chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # File uploader
    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf", "txt", "docx", "xlsx"], accept_multiple_files=True)
    current_names = [f.name for f in uploaded_files] if uploaded_files else []
    removed_files = [f for f in st.session_state.uploaded_file_names if f not in current_names]

    # Handle removed files
    if removed_files:
        with st.spinner("Removing deleted documents..."):
            st.session_state.vectordb = handle_file_changes([], st.session_state.vectordb, removed_files)
            # Remove deleted file names from session state
            st.session_state.uploaded_file_names = [f for f in st.session_state.uploaded_file_names if f not in removed_files]
            st.success(f"Removed {len(removed_files)} file(s).")

    # Handle new files
    new_files = [f for f in uploaded_files if f.name not in st.session_state.uploaded_file_names] if uploaded_files else []
    if new_files:
        with st.spinner("Processing and embedding new files..."):
            st.session_state.vectordb = handle_file_changes(new_files, st.session_state.vectordb)
            st.session_state.uploaded_file_names.extend([f.name for f in new_files])
            st.success(f"{len(new_files)} file(s) embedded and stored in vector database.")

    # Show currently uploaded files in sidebar
    st.sidebar.markdown("### Uploaded Files")
    if st.session_state.uploaded_file_names:
        for fname in st.session_state.uploaded_file_names:
            st.sidebar.write(f"{fname}")
    else:
        st.sidebar.info("No files uploaded yet.")

    # Question input
    st.subheader("Ask a Question")
    user_query = st.text_input("Ask a question about your documents:")

    if st.button("Ask") and user_query.strip():
        if not st.session_state.uploaded_file_names:
            st.warning("Please upload documents first.")
            return

        with st.spinner("Getting your answer..."):
            result, top_doc_content, top_doc_name = handle_user_query(user_query, st.session_state.vectordb)

            if result:
                # Append to chat history
                st.session_state.chat_history.append({
                    "question": user_query,
                    "answer": result,
                    "source_doc": top_doc_name,
                    "source_content": top_doc_content
                })

    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### Chat History")
        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**Q:** {chat['question']}")
            st.markdown(f"**A:** {chat['answer']}")
            st.markdown(f"*Source: {chat['source_doc']}*")
            st.write(chat['source_content'][:500] + "..." if len(chat['source_content']) > 500 else chat['source_content'])
            st.markdown("---")


if __name__ == "__main__":
    main()
