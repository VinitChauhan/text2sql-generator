from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import mysql.connector
from mysql.connector import Error
import chromadb
from chromadb.config import Settings
import requests
import json
import os
from datetime import datetime
import logging
from contextlib import asynccontextmanager
from embedding_generator import embed_and_store_schema, get_ollama_embedding
from sql_generator import generate_sql_with_ollama

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for models and clients
embedding_model = None
chroma_client = None

# Debugpy remote debugging
# if os.getenv("DEBUGPY", "0") == "1":
#     import debugpy
#     debugpy.listen(("0.0.0.0", 5678))
#     print("Waiting for debugger attach...")
#     debugpy.wait_for_client()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global embedding_model, chroma_client
    
    # Initialize embedding model
    # logger.info("Loading embedding model...")
    # embedding_model_name = os.getenv('EMBEDDING_MODEL', 'nomic-embed-text')
    # embedding_model = SentenceTransformer(embedding_model_name)
    
    # Initialize ChromaDB client
    logger.info("Connecting to ChromaDB...")
    chroma_client = chromadb.HttpClient(
        host=os.getenv('CHROMA_HOST', 'localhost'),
        port=int(os.getenv('CHROMA_PORT', '8000'))
    )
    
    # Create collection if it doesn't exist
    try:
        collection = chroma_client.get_or_create_collection(
            name="db_schema",
            metadata={"description": "SQL query examples for training"}
        )
        logger.info("ChromaDB collection ready")
        # Embed and store schema at startup
        embed_and_store_schema(chroma_client, get_mysql_connection, logger)
        logger.info(f"ChromaDB collection after embed: {collection.get(ids=['mysql_schema'])}")
    except Exception as e:
        logger.error(f"ChromaDB initialization error: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(title="Text2SQL API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TextToSQLRequest(BaseModel):
    text: str
    context: Optional[str] = None

class QueryFeedback(BaseModel):
    query_id: str
    natural_language: str
    generated_sql: str
    feedback: str  # "thumbs_up" or "thumbs_down"
    corrected_sql: Optional[str] = None
    comments: Optional[str] = None

class SQLExecutionRequest(BaseModel):
    query: str

class DatabaseSchema(BaseModel):
    tables: List[Dict[str, Any]]

# Database connection
def get_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'mysql'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            user=os.getenv('MYSQL_USER', 'app_user'),
            password=os.getenv('MYSQL_PASSWORD', 'app_password'),
            database=os.getenv('MYSQL_DATABASE', 'text2sql_db')
        )
        return connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Ollama LLM integration
generate_sql_with_llama = generate_sql_with_ollama

# API endpoints
@app.get("/")
async def root():
    return {"message": "Text2SQL API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "mysql": "connected",
            "chroma": "connected",
            "ollama": "available"
        }
    }

@app.get("/schema")
async def get_database_schema():
    """Get database schema information"""
    connection = None
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        schema_info = []
        for table in tables:
            table_name = list(table.values())[0]
            
            # Get table structure
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            schema_info.append({
                "table_name": table_name,
                "columns": columns
            })
        
        return {"tables": schema_info}
        
    except Error as e:
        logger.error(f"Schema retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve schema")
    finally:
        if connection and connection.is_connected():
            connection.close()

@app.post("/generate-sql")
async def generate_sql(request: TextToSQLRequest):
    """Generate SQL query from natural language"""
    try:
        # Get database schema for context
        schema_response = await get_database_schema()
        schema_context = ""
        
        for table in schema_response["tables"]:
            schema_context += f"\nTable: {table['table_name']}\n"
            for column in table["columns"]:
                schema_context += f"  - {column['Field']} ({column['Type']})\n"
        
        # Generate SQL using Llama
        generated_sql = generate_sql_with_llama(request.text, schema_context)
        
        # Create query ID for tracking
        query_id = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        return {
            "query_id": query_id,
            "natural_language": request.text,
            "generated_sql": generated_sql,
            "schema_context": schema_context
        }
        
    except Exception as e:
        logger.error(f"SQL generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate SQL")

@app.post("/execute-sql")
async def execute_sql(request: SQLExecutionRequest):
    """Execute SQL query and return results"""
    connection = None
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Execute the query
        cursor.execute(request.query)
        
        # Handle different query types
        if request.query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            return {
                "success": True,
                "data": results,
                "row_count": len(results)
            }
        else:
            connection.commit()
            return {
                "success": True,
                "message": f"Query executed successfully. Affected rows: {cursor.rowcount}",
                "affected_rows": cursor.rowcount
            }
            
    except Error as e:
        logger.error(f"SQL execution error: {e}")
        raise HTTPException(status_code=400, detail=f"SQL execution failed: {str(e)}")
    finally:
        if connection and connection.is_connected():
            connection.close()

@app.post("/feedback")
async def submit_feedback(feedback: QueryFeedback):
    """Submit feedback for generated SQL query"""
    try:
        # Store feedback in ChromaDB for training
        collection = chroma_client.get_collection("db_schema")
        # Create embedding for the natural language query using Ollama
        embedding = get_ollama_embedding(feedback.natural_language, logger=logger)
        # Prepare metadata
        metadata = {
            "query_id": feedback.query_id,
            "feedback": feedback.feedback,
            "generated_sql": feedback.generated_sql,
            "timestamp": datetime.now().isoformat()
        }
        if feedback.corrected_sql:
            metadata["corrected_sql"] = feedback.corrected_sql
        if feedback.comments:
            metadata["comments"] = feedback.comments
        # Store in ChromaDB
        collection.add(
            embeddings=[embedding],
            documents=[feedback.natural_language],
            metadatas=[metadata],
            ids=[feedback.query_id]
        )
        # Also store in MySQL for structured querying
        connection = get_mysql_connection()
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO query_feedback 
        (query_id, natural_language, generated_sql, feedback, corrected_sql, comments, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            feedback.query_id,
            feedback.natural_language,
            feedback.generated_sql,
            feedback.feedback,
            feedback.corrected_sql,
            feedback.comments,
            datetime.now()
        ))
        connection.commit()
        connection.close()
        return {"message": "Feedback submitted successfully", "query_id": feedback.query_id}
    except Exception as e:
        logger.error(f"Feedback submission error: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

@app.get("/feedback-stats")
async def get_feedback_stats():
    """Get feedback statistics"""
    connection = None
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get feedback statistics
        cursor.execute("""
            SELECT 
                feedback,
                COUNT(*) as count,
                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM query_feedback) as percentage
            FROM query_feedback 
            GROUP BY feedback
        """)
        
        stats = cursor.fetchall()
        
        # Get recent feedback
        cursor.execute("""
            SELECT query_id, natural_language, feedback, created_at
            FROM query_feedback 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        recent_feedback = cursor.fetchall()
        
        return {
            "statistics": stats,
            "recent_feedback": recent_feedback
        }
        
    except Error as e:
        logger.error(f"Stats retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")
    finally:
        if connection and connection.is_connected():
            connection.close()

@app.get("/similar-queries/{query_id}")
async def get_similar_queries(query_id: str, limit: int = 5):
    """Get similar queries from ChromaDB"""
    try:
        collection = chroma_client.get_collection("db_schema")
        
        # Get the original query
        results = collection.get(ids=[query_id])
        if not results['documents']:
            raise HTTPException(status_code=404, detail="Query not found")
        
        original_query = results['documents'][0]
        
        # Find similar queries
        similar_results = collection.query(
            query_texts=[original_query],
            n_results=limit + 1  # +1 to exclude the original
        )
        
        # Filter out the original query and format response
        similar_queries = []
        for i, (doc, metadata) in enumerate(zip(similar_results['documents'][0], similar_results['metadatas'][0])):
            if metadata['query_id'] != query_id:
                similar_queries.append({
                    "natural_language": doc,
                    "generated_sql": metadata.get('generated_sql', ''),
                    "feedback": metadata.get('feedback', ''),
                    "similarity_score": 1 - similar_results['distances'][0][i]
                })
        
        return {"similar_queries": similar_queries[:limit]}
        
    except Exception as e:
        logger.error(f"Similar queries error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve similar queries")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)