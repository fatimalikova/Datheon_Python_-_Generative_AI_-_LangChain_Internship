from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import EMBED_MODEL, GOOGLE_API_KEY, MODEL

BASE = Path(__file__).parent
DATA_DIR = BASE / "data"
PERSIST_DIR = str(BASE / "chroma_db")
COLLECTION = "docs"

PROMPT = ChatPromptTemplate.from_template(
    """Answer the question using ONLY the context below.
If the answer is not in the context, say "I could not find this in the documents."

Conversation so far:
{history}

Context:
{context}

Question: {question}
Answer:"""
)


def _embeddings():
    return GoogleGenerativeAIEmbeddings(model=EMBED_MODEL, google_api_key=GOOGLE_API_KEY)


def load_documents():
    docs = []
    for path in sorted(DATA_DIR.glob("*")):
        if path.suffix.lower() == ".pdf":
            docs += PyPDFLoader(str(path)).load()
        elif path.suffix.lower() == ".txt":
            docs += TextLoader(str(path), encoding="utf-8").load()
    if not docs:
        raise FileNotFoundError(f"{DATA_DIR} içinə PDF və ya TXT at.")
    return docs


def build_vectorstore(rebuild: bool = False) -> Chroma:
    store = Chroma(
        collection_name=COLLECTION,
        embedding_function=_embeddings(),
        persist_directory=PERSIST_DIR,
    )
    if not rebuild and store._collection.count() > 0:
        return store

    store.delete_collection()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(load_documents())
    return Chroma.from_documents(
        chunks,
        _embeddings(),
        collection_name=COLLECTION,
        persist_directory=PERSIST_DIR,
    )


def _page(doc) -> str:
    p = doc.metadata.get("page")
    return f"page {p + 1}" if isinstance(p, int) else "n/a"


def format_docs(docs) -> str:
    return "\n\n".join(
        f"[Source: {Path(d.metadata.get('source', '')).name}, {_page(d)}]\n{d.page_content}"
        for d in docs
    )


def sources_of(docs) -> list[str]:
    seen = []
    for d in docs:
        s = f"{Path(d.metadata.get('source', '')).name} ({_page(d)})"
        if s not in seen:
            seen.append(s)
    return seen


def _llm():
    return ChatGoogleGenerativeAI(model=MODEL, google_api_key=GOOGLE_API_KEY, temperature=0)


def answer(question: str, store: Chroma, history: str = ""):
    docs = store.as_retriever(search_kwargs={"k": 4}).invoke(question)
    chain = PROMPT | _llm() | StrOutputParser()
    text = chain.invoke({"context": format_docs(docs), "question": question, "history": history})
    return text, sources_of(docs)


def stream_answer(question: str, store: Chroma, history: str = ""):
    """Returns (token_generator, sources)."""
    docs = store.as_retriever(search_kwargs={"k": 4}).invoke(question)
    chain = PROMPT | _llm() | StrOutputParser()
    gen = chain.stream({"context": format_docs(docs), "question": question, "history": history})
    return gen, sources_of(docs)