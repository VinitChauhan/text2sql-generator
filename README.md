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

## Application Sample Screenshot

![Text2SQL Generator Screenshot]

![image](https://github.com/user-attachments/assets/98d61e10-d474-40e4-8c28-b658da1487f0)


![image](https://github.com/user-attachments/assets/3689c353-5d27-4f16-9f63-277534197b5b)


![image](https://github.com/user-attachments/assets/404aa63f-d24e-4867-8afc-a24871c25289)




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

To fix local compilation issues, please follow these steps in your terminal:

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



## Major Updates (2025)

- **Modularized backend:** Embedding and SQL prompt logic are now in `embedding_generator.py`, `sql_generator.py`, and `prompt_builder.py`.
- **ChromaDB integration:** Embeddings are validated, tokenized, and always stored as 2D lists. ChromaDB is used for both schema and feedback storage.
- **Ollama LLM:** SQL generation uses Ollama with prompt templates in `prompt_builder.py`.
- **Debugging:** Debugpy is enabled for remote debugging in Docker (port 5678). Console logging is added for API calls in the frontend.
- **Networking:** All services communicate via Docker Compose network. MySQL and ChromaDB are accessed by service name (`mysql`, `chroma`).
- **Environment:** `.env` file is required for all secrets and service hostnames. Example values:
  ```env
  MYSQL_HOST=mysql
  CHROMA_HOST=chroma
  OLLAMA_HOST=host.docker.internal
  ```
- **Frontend:** Streamlit uses `FASTAPI_URL=http://fastapi:8000` inside Docker. Use `http://localhost:8001` if running Streamlit on host.
- **Health checks:** `/health` endpoint verifies backend and service status.
- **Testing ChromaDB:** Use `backend/chroma_client.py` for manual ChromaDB queries from inside the container.

## Usage Tips

- **Start all services:**
  ```sh
  docker-compose up --build
  ```
- **Access frontend:** [http://localhost:8501](http://localhost:8501)
- **Access backend:** [http://localhost:8001](http://localhost:8001)
- **Access ChromaDB:** [http://localhost:8000](http://localhost:8000)
- **Test backend health:**
  ```sh
  curl http://localhost:8001/health
  ```
- **Test ChromaDB from backend:**
  ```sh
  docker-compose exec fastapi python chroma_client.py
  ```
- **Debugging:** Attach to port 5678 for remote debugging if needed.

## Troubleshooting

- **MySQL connection errors:** Ensure `MYSQL_HOST=mysql` in `.env` and backend code. Do not use `127.0.0.1` or `localhost` for cross-container DB access.
- **Frontend-backend connection errors:**
  - If running both in Docker, use `FASTAPI_URL=http://fastapi:8000`.
  - If running frontend on host, use `FASTAPI_URL=http://localhost:8001`.
- **ChromaDB errors:** Ensure ChromaDB is healthy and accessible at `chroma:8000` from backend.
- **No error logs but connection refused:** Check Docker Compose port mappings and use `docker-compose logs <service>` for details.

### Notes
- The backend and frontend are hot-reloaded in development mode via Docker volumes.
- All sensitive credentials are managed via the `.env` file.

## License
MIT
