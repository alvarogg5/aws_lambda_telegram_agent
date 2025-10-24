from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from loguru import logger

from telegram_agent_aws.config import settings
from telegram_agent_aws.infrastructure.clients.qdrant import get_qdrant_client

def generate_split_documents():
    loader = PyPDFLoader("./data/karan_full_biography.pdf")
    pages = loader.load()

    # Unir páginas
    full_text = "\n\n".join(p.page_content for p in pages)
    merged = Document(page_content=full_text, metadata={"source": "./data/karan_full_biography.pdf"})

    # Split con solapamiento cross-page
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200,
        separators=["\n## ", "\n", " ", ""],
        add_start_index=True
    )
    return splitter.split_documents([merged])

def index_documents():
    all_splits = generate_split_documents()

    # (Opcional) añadir page_start/page_end si lo necesitas para UI/debug
    # all_splits = add_page_ranges_to_chunks(all_splits, pages)  # ver función arriba

    embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL, api_key=settings.OPENAI_API_KEY)
    vector_store = QdrantVectorStore(
        client=get_qdrant_client(),
        collection_name="telegram_agent_aws_collection",
        embedding=embeddings,
    )
    vector_store.add_documents(all_splits)
    logger.info("Documents indexed successfully.")
