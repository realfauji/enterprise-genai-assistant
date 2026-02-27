from langchain_community.vectorstores import FAISS
from app.langchain_layer.embeddings import get_embeddings
from pathlib import Path


BASE_INDEX_DIR = Path("faiss_indexes")


def get_user_index_path(user_id:int) -> Path:
    path = BASE_INDEX_DIR / f"user_{user_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path

def load_vectorstore(user_id:int):
    embeddings = get_embeddings()
    index_path = get_user_index_path(user_id)
    if not (index_path / "index.faiss").exists():
        raise ValueError("No documents indexed for this user.")

    return FAISS.load_local(str(index_path), embeddings, allow_dangerous_deserialization=True)

def create_new_vectorstore(user_id:int, documents):
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(str(get_user_index_path(user_id)))
    return vectorstore

def add_documents_to_vectorstore(user_id:int, documents):
    embeddings = get_embeddings()
    index_path = get_user_index_path(user_id)
    if (index_path / "index.faiss").exists():
        vs = FAISS.load_local(
            str(index_path),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        vs.add_documents(documents)
    else:
        vs = FAISS.from_documents(documents, embeddings)

    vs.save_local(str(index_path))
    return vs