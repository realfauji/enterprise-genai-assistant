# from langchain_community.vectorstores import FAISS
# from app.langchain_layer.embeddings import get_embeddings
# from pathlib import Path

from langchain_postgres import PGVector
from app.langchain_layer.embeddings import get_embeddings
from app.core.config import settings

DATABASE_URL = settings.VECTOR_DB_URL

# BASE_INDEX_DIR = Path("faiss_indexes")


# def get_user_index_path(user_id:int) -> Path:
#     path = BASE_INDEX_DIR / f"user_{user_id}"
#     path.mkdir(parents=True, exist_ok=True)
#     return path

def load_vectorstore(user_id:int):
    embeddings = get_embeddings()
    # index_path = get_user_index_path(user_id)
    # if not (index_path / "index.faiss").exists():
    #     raise ValueError("No documents indexed for this user.")
    vectorstore = PGVector(
        connection_string=DATABASE_URL,
        embedding_function=embeddings,
        collection_name=f"user_{user_id}",
    )

    # return FAISS.load_local(str(index_path), embeddings, allow_dangerous_deserialization=True)
    return vectorstore

def create_new_vectorstore(user_id:int, documents):
    embeddings = get_embeddings()
    # vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore = PGVector.from_documents(documents=documents, embedding=embeddings, connection_string=DATABASE_URL, collection_name=f"user_{user_id}")
    # vectorstore.save_local(str(get_user_index_path(user_id)))
    return vectorstore

def add_documents_to_vectorstore(user_id:int, documents):
    # embeddings = get_embeddings()
    # index_path = get_user_index_path(user_id)
    # if (index_path / "index.faiss").exists():
    #     vs = FAISS.load_local(
    #         str(index_path),
    #         embeddings,
    #         allow_dangerous_deserialization=True,
    #     )
    #     vs.add_documents(documents)
    # else:
    #     vs = FAISS.from_documents(documents, embeddings)

    # vs.save_local(str(index_path))
    # return vs
    vs = load_vectorstore(user_id)
    vs.add_documents(documents)
    return vs
