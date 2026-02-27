from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import settings


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=settings.HF_EMBEDDING_MODEL)