from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.llm import LLMChain
from app.langchain_layer.llm_factory import get_llm


def build_simple_llm_chain(provider:str | None, question:str, history_pairs, callbacks:None):
    llm = get_llm(provider)

    history_text = ""
    for user_msg, assistant_msg in history_pairs:
        history_text += f"User: {user_msg}\nAssistant: {assistant_msg}\n"

    prompt = f"""
        You are a highly capable AI assistant.
        Your goal is to help the user clearly and accurately.
        You may use the provided context if it is relevant.
        If the context is not relevant, rely on your general knowledge.
        Always answer the user's question directly.
        Do not say you don't know unless you truly have no information at all.

        Conversation History:
        {history_text}

        User Question:
        {question}

        Answer:
    """
    response = llm.invoke(prompt, config={"callbacks": callbacks} if callbacks else None)

    return {"answer": response.content, "source_documents": []}

def build_rag_chain(provider:str | None, vectorstore, question:str, history_pairs, callbacks:None):
    llm = get_llm(provider)

    history_text = ""
    for user_msg, assistant_msg in history_pairs:
        history_text += f"User: {user_msg}\nAssistant: {assistant_msg}\n"

    docs = vectorstore.similarity_search(question, k=4)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""
        You are a highly capable AI assistant.
        Your goal is to help the user clearly and accurately.
        You may use the provided context if it is relevant.
        If the context is not relevant, rely on your general knowledge.
        Always answer the user's question directly.
        Do not say you don't know unless you truly have no information at all.

        Conversation History:
        {history_text}

        Context (if any):
        {context}

        User Question:
        {question}

        Answer:
    """
    response = llm.invoke(prompt, config={"callbacks": callbacks} if callbacks else None)

    return {"answer": response.content, "source_documents": docs}

def create_auto_title(provider:str | None, question):
    llm = get_llm(provider=None)

    title_prompt = f"""
        Generate a short and clean title (maximum 6 words) 
        that summarizes the user's first message.

        User Message:
        {question}

        Only return the title text.
        Do not include quotes or punctuation.
    """

    title_response = llm.invoke(title_prompt)
    short_title = title_response.content.strip()

    # Safety fallback
    if not short_title:
        short_title = question[:40]

    # Hard truncate safety
    short_title = short_title[:60]
    return short_title