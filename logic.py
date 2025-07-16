from extract import embed_documents, filter_relevant_chunks, build_context, load_vector_db
from model import query_lmstudio


def initialize_db():
    return load_vector_db()


def handle_file_changes(uploaded_files, vectordb, files_to_remove=None):
    vectordb, _ = embed_documents(uploaded_files, vectordb, files_to_remove)
    return vectordb


def handle_user_query(user_query, vectordb):
    retriever = vectordb.as_retriever()
    relevant_docs = retriever.get_relevant_documents(user_query)

    if not relevant_docs:
        return None, None, None

    filtered_chunks = filter_relevant_chunks(user_query, relevant_docs)
    if not filtered_chunks:
        return None, None, None

    context = build_context(filtered_chunks)
    result = query_lmstudio(context, user_query)

    top_doc_content, top_doc_name = filtered_chunks[0]
    return result, top_doc_content, top_doc_name
