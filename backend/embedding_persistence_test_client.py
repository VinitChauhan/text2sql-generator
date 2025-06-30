import os
import requests
import chromadb
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ollama_embedding(text: str, ollama_host: str, ollama_port: str, model: str = 'nomic-embed-text') -> list[float]:
    """
    Generates an embedding for the given text using the Ollama service.
    """
    url = f"http://{ollama_host}:{ollama_port}/api/embeddings"
    payload = {"model": model, "prompt": text}
    try:
        logger.info(f"Sending embedding request to {url} with payload: {payload}")
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        logger.info("Successfully generated embedding.")
        return result["embedding"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama request error: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during embedding generation: {e}")
        raise

def save_embedding_to_chroma(collection_name: str, embedding: list[float], document: str, doc_id: str, metadata: dict):
    """
    Saves a document and its embedding to a specified ChromaDB collection.
    """
    try:
        chroma_host = os.getenv('CHROMA_HOST', 'localhost')
        chroma_port = int(os.getenv('CHROMA_PORT', '8000'))

        logger.info(f"Connecting to ChromaDB at {chroma_host}:{chroma_port}...")
        chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)

        logger.info(f"Getting or creating collection: {collection_name}")
        collection = chroma_client.get_or_create_collection(name=collection_name)

        logger.info(f"Adding document with ID '{doc_id}' to collection.")
        collection.add(
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata],
            ids=[doc_id]
        )
        logger.info("Successfully saved embedding to ChromaDB.")
    except Exception as e:
        logger.error(f"Failed to save embedding to ChromaDB: {e}")
        raise

if __name__ == "__main__":
    # --- Configuration ---
    # Ollama configuration
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')
    OLLAMA_PORT = os.getenv('OLLAMA_PORT', '11434')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'nomic-embed-text')

    # ChromaDB configuration
    NEW_COLLECTION_NAME = "my_new_collection"

    # Data to embed and store
    TEXT_TO_EMBED = "This is a sample text to test embedding persistence."
    DOCUMENT_ID = "sample_doc_1"
    METADATA = {"source": "embedding_persistence_script", "timestamp": datetime.now().isoformat()}

    # --- Execution ---
    try:
        # 1. Generate embedding
        embedding = get_ollama_embedding(
            text=TEXT_TO_EMBED,
            ollama_host=OLLAMA_HOST,
            ollama_port=OLLAMA_PORT,
            model=EMBEDDING_MODEL
        )

        logger.info(f"Generated embedding of type {type(embedding)} with length {len(embedding)}")
        # 2. Save the embedding to ChromaDB
        if embedding:
            save_embedding_to_chroma(
                collection_name=NEW_COLLECTION_NAME,
                embedding=embedding,
                document=TEXT_TO_EMBED,
                doc_id=DOCUMENT_ID,
                metadata=METADATA
            )
            
            # Optional: Verify the data was saved
            logger.info("Verifying data in ChromaDB...")
            chroma_client = chromadb.HttpClient(host=os.getenv('CHROMA_HOST', 'localhost'), port=int(os.getenv('CHROMA_PORT', '8000')))
            collection = chroma_client.get_collection(name=NEW_COLLECTION_NAME)
            retrieved_doc = collection.get(ids=[DOCUMENT_ID])
            logger.info(f"Retrieved document from ChromaDB: {retrieved_doc}")

    except Exception as e:
        logger.error(f"An error occurred in the main execution block: {e}")
