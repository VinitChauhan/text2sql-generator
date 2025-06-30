import chromadb
import os

# Create the ChromaDB HTTP client
chroma_client = chromadb.HttpClient(
    host=os.getenv('CHROMA_HOST', 'localhost'),
    port=int(os.getenv('CHROMA_PORT', '8000'))
)

# collections = chroma_client.list_collections()

# for collection in collections:
#     print(collection.get(collection.name))

# Access an existing collection (e.g., "sql_examples")
collection = chroma_client.get_collection("db_schema")

# Example: Read all document IDs in the collection
result = collection.get()
print(result)


#Test command to run this script in the Docker container:
# docker-compose exec fastapi python chroma_client.py