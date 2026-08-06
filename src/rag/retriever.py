import gc
import os
import shutil
import chromadb
from config.logger import logger
from config.settings import settings
from rag_setup import load_vectorstore, get_retriever, setup_rag

def _vectorstore_exists() -> bool:
    """Check that the persist dir exists AND actually contains a Chroma database,
    not just an empty folder."""
    persist_dir = settings.chroma_persist_dir
    if not os.path.isdir(persist_dir):
        return False
    return any(os.scandir(persist_dir))

class RetrieverManager:
    def __init__(self):
        self._retriever = None

    def load_or_build(self):
        """Load the existing vectorstore, or build it from CSVs if none exists yet."""
        if _vectorstore_exists():
            logger.info(f"Found existing vectorstore at '{settings.chroma_persist_dir}', loading it.")
            vectorstore = load_vectorstore()
        else:
            logger.info("No vectorstore found (or it's empty). Building it for the first time...")
            vectorstore = setup_rag()

        self._retriever = get_retriever(vectorstore)
        logger.info("Retriever is ready.")
        return self._retriever

    def rebuild(self) -> int:
        persist_dir = settings.chroma_persist_dir
        logger.info("Rebuilding vectorstore from source CSVs...")
        self._retriever = None
        chromadb.api.client.SharedSystemClient.clear_system_cache()
        gc.collect()

        if os.path.isdir(persist_dir):
            logger.info(f"Removing existing vectorstore at '{persist_dir}' before rebuild.")
            shutil.rmtree(persist_dir)

        vectorstore = setup_rag()
        self._retriever = get_retriever(vectorstore)

        count = vectorstore._collection.count()
        logger.info(f"Vectorstore rebuilt with {count} vectors. Retriever refreshed.")
        return count

    def get(self):
        """Return the current retriever, building it lazily on first use."""
        if self._retriever is None:
            return self.load_or_build()
        return self._retriever

retriever_manager = RetrieverManager()