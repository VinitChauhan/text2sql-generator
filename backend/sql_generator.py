import os
import requests
import logging
from prompt_builder import SQLPromptBuilder

def generate_sql_with_ollama(prompt: str, schema_context: str = "") -> str:
    ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
    ollama_port = os.getenv('OLLAMA_PORT', '11434')
    model = os.getenv('OLLAMA_MODEL', 'llama3.2:3b-instruct-q4_0')
    timeout = int(os.getenv('OLLAMA_READ_TIMEOUT', '90'))
    max_tokens = int(os.getenv('OLLAMA_MAX_TOKENS', '500'))
    full_prompt = SQLPromptBuilder.build_sql_prompt(prompt, schema_context)
    try:
        response = requests.post(
            f"http://{ollama_host}:{ollama_port}/api/generate",
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "max_tokens": max_tokens
                }
            },
            timeout=timeout
        )
        if response.status_code == 200:
            result = response.json()
            sql_query = result.get('response', '').strip()
            if sql_query.startswith('```sql'):
                sql_query = sql_query[6:]
            if sql_query.endswith('```'):
                sql_query = sql_query[:-3]
            return sql_query.strip()
        else:
            logging.error(f"Ollama API error: {response.status_code}")
            raise Exception("LLM generation failed")
    except requests.exceptions.RequestException as e:
        logging.error(f"Ollama request error: {e}")
        raise Exception("LLM service unavailable")