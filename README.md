<!-- Animated README header -->
<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=24&pause=1000&color=8B7CFF&center=true&vCenter=true&width=780&lines=SMART+DB+ASSISTANT;Natural+Language+%E2%86%92+SQL;Ask+your+movies+database+in+plain+English" alt="Animated Smart DB Assistant title"/>

<p><b>LLM-powered natural-language database assistant</b></p>

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/Ollama-Llama%203-111827?style=for-the-badge" alt="Ollama Llama 3"/>
<img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL"/>
<img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge" alt="LangChain"/>

</div>

---

## `01 / OVERVIEW`

Smart DB Assistant lets a user ask questions in plain English about a MySQL `movies` table. The application asks an LLM to draft a SQL query, checks that it appears read-only, executes it, and asks the model to explain the result.

## `02 / HOW IT WORKS`

```mermaid
flowchart TD
    A[Question in plain English] --> B[Ollama Llama 3]
    B --> C[Generate SQL]
    C --> D{Read-only validation}
    D -->|Allowed| E[Query MySQL movies table]
    D -->|Blocked| F[Return safety message]
    E --> G[LLM explains results]
    G --> H[Answer]
```

## `03 / TECH STACK`

- **Language:** Python
- **LLM runtime:** Ollama with Llama 3
- **LLM orchestration/database integration:** LangChain
- **Database:** MySQL
- **Database connection:** SQLAlchemy via PyMySQL

## `04 / SETUP`

### Prerequisites

- Python installed
- MySQL server with a database and a `movies` table
- Ollama installed, with the Llama 3 model available

### 1. Clone the repository

```bash
git clone https://github.com/rasswanthsura-cpu/smart_db_assitant.git
cd smart_db_assitant
```

### 2. Install dependencies

Install the packages used by the project:

```bash
pip install langchain-community langchain-ollama sqlalchemy pymysql
```

### 3. Configure the database

Set `SMART_DB_DATABASE_URI` to your own MySQL connection string before running the app. Example format:

```text
mysql+pymysql://USERNAME:PASSWORD@localhost:3306/DATABASE_NAME
```

Do not commit credentials, passwords, API keys, or other secrets. If a real password was ever committed to a public repository, rotate it.

### 4. Start Ollama and run

Ensure Ollama is running and the model is available:

```bash
ollama pull llama3
python app.py
```

Ask a question about the configured movies table in the terminal.

## `05 / SAFETY NOTES`

The application contains a basic read-only SQL check intended to block common data-changing statements. This is **not a complete SQL security boundary**. For real deployments, use a dedicated database account with SELECT-only permissions, validate SQL with a proper parser, add timeouts, and avoid exposing the database directly to untrusted users.

## `06 / CURRENT SCOPE & NEXT STEPS`

Current code focuses on a single `movies` table and a terminal workflow. Possible next steps:

- Add tests for SQL generation and validation
- Improve error handling and query logging without storing secrets
- Add a polished web UI
- Add sample questions and a sanitized demo dataset

## `07 / AUTHOR`

**Rasswanth S.** · [GitHub profile](https://github.com/rasswanthsura-cpu) · [Email](mailto:rasswanth.sura@gmail.com)
