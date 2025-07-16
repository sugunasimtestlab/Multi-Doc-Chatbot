def format_prompt(context: str, user_query: str, fallback_message: str = "Sorry, the answer is not available in the document.") -> str:
    """
    Create a structured prompt for the language model using provided context and user question.
    If context is missing or invalid, return a fallback response instruction.
    """
    # Normalize and check if context is validencoding="utf-8"
    cleaned_context = context.strip().lower()
    if not cleaned_context or cleaned_context in {"no relevant context was found", "n/a", "none"}:
        return f'You are a helpful assistant. Respond with:\n"{fallback_message}"'

    # Return formatted prompt
    return (
        "You are a helpful assistant. Answer the user's question using ONLY the context provided below.\n"
        "Be clear, concise, and do not include any external knowledge or assumptions.\n\n"
        f"Context:\n\"\"\"\n{context.strip()}\n\"\"\"\n\n"
        f"Question: {user_query.strip()}\n\n"
        "Answer:"
    )
