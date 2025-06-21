# Text2SQL Generator

A full-stack application that converts natural language queries into executable SQL using LLMs, with a FastAPI backend, Streamlit frontend, MySQL database, and ChromaDB for vector storage.

## Features
- Natural language to SQL query generation using LLM (Ollama)
- FastAPI backend for API endpoints
- Streamlit frontend for user interaction
- MySQL for structured data storage
- ChromaDB for vector embeddings and semantic search
- Dockerized microservices architecture

## Project Structure
```
text2sql-generator/
├── backend/        # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   └── dockerfile
├── frontend/       # Streamlit frontend
│   ├── app.py
│   ├── requirements.txt
│   └── dockerfile
├── init-db/        # MySQL initialization scripts
│   └── 01_init.sql
├── docker-compose.yml
├── .env            # Environment variables
└── README.md
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- (Optional) Python 3.11+ for local development

### Setup
1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd text2sql-generator
   ```
2. **Configure environment variables:**
   Edit the `.env` file as needed (default values provided):
   ```env
   MYSQL_ROOT_PASSWORD=rootpassword
   MYSQL_DATABASE=text2sql_db
   MYSQL_USER=app_user
   MYSQL_PASSWORD=app_password
   MYSQL_HOST=mysql
   MYSQL_PORT=3306
   ```
3. **Start all services:**
   ```sh
   docker-compose up --build
   ```

### Services
- **FastAPI backend:** [http://localhost:8001](http://localhost:8001)
- **Streamlit frontend:** [http://localhost:8501](http://localhost:8501)
- **ChromaDB:** [http://localhost:8000](http://localhost:8000)
- **MySQL:** localhost:3306

### API Endpoints
- `/generate-sql` – Generate SQL from natural language
- `/execute-sql` – Execute SQL and return results
- `/schema` – Get database schema
- `/feedback` – Submit feedback on generated SQL
- `/feedback-stats` – Get feedback statistics
- `/similar-queries/{query_id}` – Find similar queries

### Development
- Backend code: `backend/main.py`
- Frontend code: `frontend/app.py`
- Database schema: `init-db/01_init.sql`


# Troubleshooting local

To fix this, please follow these steps in your terminal:

Delete the broken virtual environment:
```bash
rm -rf /Users/vinitchauhan/AI-Workspace/text2sql-generator/.venv
```

Recreate the virtual environment:
```bash
python3 -m venv /Users/vinitchauhan/AI-Workspace/text2sql-generator/.venv
```

Activate the virtual environment:
```bash
source /Users/vinitchauhan/AI-Workspace/text2sql-generator/.venv/bin/activate
```

Upgrade pip and install requirements:
```bash
python -m ensurepip --upgrade
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

After these steps, try running your script again:
```bash
python backend/chroma_client.py
```



### Notes
- The backend and frontend are hot-reloaded in development mode via Docker volumes.
- All sensitive credentials are managed via the `.env` file.

## License
MIT
