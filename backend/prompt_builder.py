class SQLPromptBuilder:
    @staticmethod
    def build_sql_prompt(prompt: str, schema_context: str = "") -> str:
        return (
            "You are an expert SQL query generator. Given a natural language question and database schema, generate a precise SQL query.\n\n"
            f"Database Schema:\n{schema_context}\n\n"
            f"Natural Language Question: {prompt}\n\n"
            "Generate ONLY the SQL query without any explanation or formatting. The query should be executable and follow MySQL syntax.\n\n"
            "SQL Query:"
        )
