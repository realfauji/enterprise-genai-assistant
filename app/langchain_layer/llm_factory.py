from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from app.core.config import settings


def get_llm(provider:str | None = None):
    provider = provider or settings.DEFAULT_LLM_PROVIDER
    api_key = settings.GROQ_API_KEY

    if provider == "openai":
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.5, streaming=True)

    if provider == "groq":
        return ChatGroq(model_name="llama-3.1-8b-instant", api_key=api_key, temperature=0.5, streaming=True)

    raise ValueError("Invalid LLM provider")