import os
from typing import Optional

from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama
from sqlalchemy.exc import DBAPIError


DATABASE_URI = os.getenv("SMART_DB_DATABASE_URI")
MOVIES_TABLE = "movies"
MOVIE_COLUMNS = ("movie_id", "title", "release_year", "imdb_rating")
SQL_PREVIEW_LIMIT = 200
DB_ENGINE_ARGS = {
    "pool_pre_ping": True,
    "pool_recycle": 1800,
}

llm = ChatOllama(
    model="llama3",
    temperature=0.2,
)

db: Optional[SQLDatabase] = None


def create_database() -> SQLDatabase:
    if not DATABASE_URI:
        raise RuntimeError(
            "SMART_DB_DATABASE_URI is not set. Configure your MySQL connection "
            "string as an environment variable before starting the assistant."
        )

    return SQLDatabase.from_uri(
        DATABASE_URI,
        engine_args=DB_ENGINE_ARGS,
        include_tables=[MOVIES_TABLE],
        sample_rows_in_table_info=0,
        lazy_table_reflection=True,
    )


def get_database(force_refresh: bool = False) -> SQLDatabase:
    global db

    if force_refresh or db is None:
        db = create_database()

    return db


def reset_database() -> SQLDatabase:
    global db

    if db is not None:
        engine = getattr(db, "_engine", None)
        if engine is not None:
            engine.dispose()

    db = create_database()
    return db


def clean_sql(sql: str) -> str:
    cleaned_sql = sql.strip()

    if "```" in cleaned_sql:
        cleaned_sql = cleaned_sql.replace("```sql", "").replace("```", "")

    if cleaned_sql.lower().startswith("sql:"):
        cleaned_sql = cleaned_sql[4:].strip()

    return cleaned_sql.strip()


def is_safe_sql(sql: str) -> bool:
    normalized_sql = " ".join(sql.strip().lower().split())
    forbidden_words = (
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create",
        "replace",
        "grant",
        "revoke",
    )

    if not normalized_sql.startswith(("select", "with")):
        return False

    return not any(word in normalized_sql for word in forbidden_words)


def build_sql_prompt(question: str) -> str:
    columns = "\n".join(f"- {column}" for column in MOVIE_COLUMNS)

    return f"""
You are a MySQL expert.

Use ONLY this table: {MOVIES_TABLE}

Columns:
{columns}

Question: {question}

Rules:
- Return ONLY one SQL query
- Do NOT explain
- Query only the movies table
- Use a read-only query

Examples:
Q: Show all movies
SQL: SELECT * FROM movies;

Q: Show top 2 movies
SQL: SELECT title FROM movies LIMIT 2;

Q: Top rated movies
SQL: SELECT title FROM movies ORDER BY imdb_rating DESC LIMIT 5;
""".strip()


def build_explain_prompt(question: str, sql_query: str, result: str) -> str:
    return f"""
User Question:
{question}

SQL Query:
{sql_query}

Result:
{result}

Explain the result in simple English.
""".strip()


def execute_sql(sql_query: str) -> str:
    last_error: Optional[Exception] = None

    for attempt in range(2):
        try:
            return get_database(force_refresh=attempt > 0).run(sql_query)
        except DBAPIError as exc:
            last_error = exc
            if attempt == 0:
                reset_database()
                continue
            raise

    if last_error is not None:
        raise last_error

    raise RuntimeError("Database query failed without raising an error.")


def ask_db(question: str) -> str:
    try:
        response = llm.invoke(build_sql_prompt(question))
        raw_sql = response.content[:SQL_PREVIEW_LIMIT]
        sql_query = clean_sql(raw_sql)

        print("Generated SQL:", sql_query)

        if not is_safe_sql(sql_query):
            return "Unsafe query blocked. Please ask a read-only question about the movies table."

        result = execute_sql(sql_query)
        explanation = llm.invoke(build_explain_prompt(question, sql_query, str(result)))
        return str(explanation.content)
    except DBAPIError as exc:
        return (
            "Database connection error. The app retried once, but MySQL is still not "
            f"available: {exc}"
        )
    except Exception as exc:
        return f"Unexpected error: {exc}"


if __name__ == "__main__":
    print("\nAI Database Chatbot Ready!")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not user_input:
            continue

        print("Thinking...\n")
        answer = ask_db(user_input)
        print("Assistant:", answer)
        print("\n" + "-" * 50 + "\n")
