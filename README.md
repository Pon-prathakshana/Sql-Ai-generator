# Text-to-SQL Generator

A web-based tool powered by FastAPI and locally hosted Large Language Models (via Ollama) that translates natural language questions into valid SQL queries based on a provided database schema.

## Features

- **Interactive UI**: Paste your database schema and input your natural language query in a clean interface.
- **Local LLMs**: Leverages [Ollama](https://ollama.com/) for secure, local, and offline SQL generation.
- **Comprehensive Outputs**: Returns the generated SQL, the predicted intent, and a brief explanation of how the query works.
- **Model Selection**: Automatically fetches and lets you select from available models within your Ollama instance.
- **System Health**: Dedicated monitoring endpoints and metrics for CPU, RAM, and Ollama service status.

## Prerequisites

- **Python 3.8+**
- **Ollama**: Must be installed and running locally on `http://localhost:11434`.
- **LLM Models**: Make sure you have at least one model pulled in Ollama (e.g., `llama3`). 
  ```bash
  ollama run llama3
  ```

## Installation & Setup

1. **Clone or navigate to the repository directory:**
   ```bash
   cd ConversationalText2SQL-Trainer
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - On **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure `psutil` is installed as it's required for system health metrics by running `pip install psutil` if not included in your requirements list.)*

## Running the Application

Start the FastAPI development server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

Alternatively, if you are running it as a script:
```bash
python app/main.py
```

Once running, access the application in your browser:
- **Main Interface**: [http://localhost:5000/](http://localhost:5000/)
- **Health Dashboard**: [http://localhost:5000/health](http://localhost:5000/health)

## API Endpoints

- `GET /` : Renders the main Web UI.
- `GET /health` : Renders the system health dashboard.
- `GET /api/models` : Fetches the list of installed models from the local Ollama instance.
- `GET /api/health` : Returns health metrics for the backend service, Ollama status, and host system RAM/CPU utilization.
- `POST /api/generate` : Takes a JSON payload containing the schema, natural language query, and model. Returns JSON with the generated SQL, predicted intent, and query explanation.

## Technologies Used

- **Backend**: FastAPI, Uvicorn, Python
- **Frontend**: HTML, custom CSS/JS (served via Jinja2 & StaticFiles)
- **AI Integration**: Ollama API, Requests
- **Monitoring**: Psutil
