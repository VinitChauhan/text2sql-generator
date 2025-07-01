import os
import requests
from datetime import datetime
from mysql.connector import Error

## Function to read MySQL schema, tokenize it, create a vector embedding using Ollama, and store it in ChromaDB
def embed_and_store_schema(chroma_client, get_mysql_connection, logger):
    """
    Reads MySQL schema, tokenizes it, creates a vector embedding using Ollama, and stores it in ChromaDB.
    Should be called only at backend application startup.
    """
    try:
        collection = chroma_client.get_or_create_collection(
            name="db_schema",
            metadata={"description": "Vector embedding of MySQL schema"}
        )
        logger.info("ChromaDB schema collection ready")

        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        schema_text = ""
        for table in tables:
            table_name = list(table.values())[0]
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            schema_text += f"Table: {table_name}\n"
            for column in columns:
                schema_text += f"  - {column['Field']} ({column['Type']})\n"
            
        # Tokenize and embed schema text using Ollama
        schema_embedding = get_ollama_embedding(schema_text, logger=logger)
        logger.info(f"MySQL schema embedding Type : {type(schema_embedding)}")
        # Remove old if exists
        try:
            collection.delete(ids=["mysql_schema"])
        except Exception:
            pass

        collection.add( 
            embeddings=[schema_embedding],
            documents=[schema_text],
            metadatas=[{"type": "schema", "timestamp": datetime.now().isoformat()}],
            ids=["mysql_schema"]
        )
        logger.info("MySQL schema embedded and stored in ChromaDB.")

        cursor.close()
        connection.close()
    except Error as e:
        logger.error(f"Schema embedding error: {e}")
    except Exception as e:  
        logger.error(f"Unexpected error during schema embedding: {e}")
        
## Function to get Ollama embedding for a given text
def get_ollama_embedding(text, ollama_host=None, ollama_port=None, model=None, logger=None):
    ollama_host = ollama_host or os.getenv('OLLAMA_HOST', 'localhost')
    ollama_port = ollama_port or os.getenv('OLLAMA_PORT', '11434')
    model = model or os.getenv('EMBEDDING_MODEL', 'nomic-embed-text')
    url = f"http://{ollama_host}:{ollama_port}/api/embeddings"
    payload = {
        "model": model,
        "prompt": text
    }
    try:
        if logger:
            logger.info(f"\n Sending embedding request to {url} with payload: {payload}")
        response = requests.post(url, json=payload, timeout=30)
        # if logger:
        #     logger.info(f"\n Ollama embedding response: {response.status_code} {response.text}")
        response.raise_for_status()
        result = response.json()
        return result["embedding"]
    except Exception as e:
        if logger:
            logger.error(f"Ollama embedding error: {e}")
        raise