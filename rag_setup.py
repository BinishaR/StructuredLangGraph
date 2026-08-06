import pandas as pd
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from config.logger import logger
from config.settings import settings


def load_csv_as_documents(csv_path: str, source_name: str) -> list[Document]:

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    documents = []
    for idx, row in df.iterrows():

        content = f"Question: {row['Question']}\nAnswer: {row['Answer']}"

        doc = Document(
            page_content=content,

            metadata={
                "source": source_name,

                "row": idx,

                "question": row['Question'],
            }
        )
        documents.append(doc)

    logger.info(f"Loaded {len(documents)} documents from {source_name}")
    return documents


#  RecursiveCharacterTextSplitter
def chunk_documents(documents: list[Document]) -> list[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=[""],
        length_function=len,

    )

    chunks = splitter.split_documents(documents)
    logger.info(f"Split into {len(chunks)} chunks")
    return chunks

#  OpenAI Embeddings
def get_embeddings():
    return OpenAIEmbeddings(api_key=settings.openai_api_key)

# Chroma Vector Database
def build_vectorstore(chunks: list[Document]) -> Chroma:

    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,

        embedding=embeddings,

        persist_directory=settings.chroma_persist_dir,

        collection_name=settings.chroma_collection_name

    )

    logger.info(f"Vectorstore built with {vectorstore._collection.count()} vectors")
    return vectorstore


def load_vectorstore() -> Chroma:

    embeddings = get_embeddings()

    vectorstore = Chroma(
        persist_directory=settings.chroma_persist_dir,
        embedding_function=embeddings,
        collection_name=settings.chroma_collection_name
    )

    logger.info(f"Loaded vectorstore with {vectorstore._collection.count()} vectors")
    return vectorstore


def setup_rag():

    docs_general = load_csv_as_documents("data/GeneralFAQS.csv", "general")
    docs_mobile = load_csv_as_documents("data/MobileMoney.csv", "mobile")
    docs_wonder = load_csv_as_documents("data/WonderWomanSavings.csv", "wonder")

    all_docs = docs_general + docs_mobile + docs_wonder
    logger.info(f"Total documents: {len(all_docs)}")
    chunks = chunk_documents(all_docs)
    vectorstore = build_vectorstore(chunks)
    return vectorstore


def get_retriever(vectorstore: Chroma):

    return vectorstore.as_retriever(
        search_type="similarity",

        search_kwargs={"k": settings.retriever_k}
    )


if __name__ == "__main__":

    vectorstore = setup_rag()
    logger.info("RAG setup complete! Chroma DB saved to ./chroma_db")
    retriever = get_retriever(vectorstore)
    results = retriever.invoke("what is mobile money")
    logger.info(f"Test search returned {len(results)} results")
    for doc in results:
        logger.info(f"Source: {doc.metadata['source']} | Content: {doc.page_content[:100]}...")