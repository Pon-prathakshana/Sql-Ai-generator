from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
import uvicorn
import psutil
import time
import random
import json

app = FastAPI(title="Text-to-SQL Generator")

# We will serve static files (like custom CSS or JS if needed) from the `static` directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

class SQLRequest(BaseModel):
    schema: str
    query: str
    model: str = "llama3"

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.get("/health", response_class=HTMLResponse)
async def health_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="health.html"
    )

@app.get("/api/models")
async def get_models():
    """Fetch installed models from local Ollama instance"""
    ollama_url = "http://localhost:11434/api/tags"
    try:
        response = requests.get(ollama_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        models = []
        for model in data.get("models", []):
            models.append({
                "name": model.get("name"),
                "size": model.get("size"),
                "digest": model.get("digest")
            })
        return {"models": models}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to Ollama to list models: {str(e)}"}

@app.get("/api/health")
async def system_health():
    """Return system and service health metrics"""
    ollama_url = "http://localhost:11434/"
    
    # Check Ollama
    ollama_status = "offline"
    ollama_latency = 0
    start_time = time.time()
    try:
        req = requests.get(ollama_url, timeout=2)
        if req.status_code == 200:
            ollama_status = "operational"
            ollama_latency = round((time.time() - start_time) * 1000)
    except:
        pass
    
    # System RAM using psutil
    ram = psutil.virtual_memory()
    
    # System CPU using psutil
    cpu = psutil.cpu_percent(interval=0.1)

    return {
        "services": {
            "backend": {
                "status": "operational", 
                "message": "FastAPI is running"
            },
            "ollama": {
                "status": ollama_status,
                "latency_ms": ollama_latency
            }
        },
        "system": {
            "cpu_percent": cpu,
            "ram_percent": ram.percent,
            "ram_used_gb": round(ram.used / (1024**3), 2),
            "ram_total_gb": round(ram.total / (1024**3), 2)
        }
    }

@app.post("/api/generate")
async def generate_sql(request: SQLRequest):
    ollama_url = "http://localhost:11434/api/generate"
    
    system_prompt = f"""You are an expert SQL generation assistant. 
Your task is to take a database schema and a natural language query, and return a single valid JSON object.
Do NOT wrap the JSON in markdown formatting blocks like ```json ... ```.

The JSON object must contain exactly these three keys:
"intent": A short 3-5 word description of the user's intent. It MUST start with the SQL command type (e.g., [DML], [DDL], [DCL], [TCL]). Example: "[DML] Retrieve active users".
"sql": The executable SQL query.
"explanation": A brief, 1-2 sentence explanation of how the SQL query works.

Database Schema:
{request.schema}
"""

    user_prompt = f"Query: {request.query}"

    payload = {
        "model": request.model,
        "prompt": f"{system_prompt}\n\n{user_prompt}",
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }

    try:
        response = requests.post(ollama_url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        raw_output = result.get("response", "").strip()
        # Clean up markdown if the model ignored instructions
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.startswith("```"):
            raw_output = raw_output[3:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]
            
        try:
            json_response = json.loads(raw_output.strip())
            sql_output = json_response.get("sql", "-- Query not found").strip()
            intent = json_response.get("intent", "Unknown Intent")
            explanation = json_response.get("explanation", "No explanation provided.")
        except json.JSONDecodeError:
            # Fallback if json parsing fails
            sql_output = raw_output
            intent = "Parse Error"
            explanation = "Failed to parse JSON response from the model."
            
        metrics = {
            "total_duration": result.get("total_duration"),
            "load_duration": result.get("load_duration"),
            "prompt_eval_count": result.get("prompt_eval_count"),
            "prompt_eval_duration": result.get("prompt_eval_duration"),
            "eval_count": result.get("eval_count"),
            "eval_duration": result.get("eval_duration"),
        }
            
        return {
            "sql": sql_output.strip(), 
            "intent": intent, 
            "explanation": explanation, 
            "metrics": metrics
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to local Ollama instance: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)
