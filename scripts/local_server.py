# /scripts/local_server.py

import json
from fastapi import FastAPI, Request, HTTPException
import os
import sys

# --- Setup Paths and Env ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
    
# Importa tu handler de lambda
from src.telegram_agent_aws.infrastructure.lambda_function import lambda_handler

# Define the FastAPI app
app = FastAPI()

@app.post("/")
async def handle_webhook(request: Request):
    try:
        body_json = await request.json()
        event = {"body": json.dumps(body_json)}
        
        print("\n--- Recibida petición de Telegram ---")
        response = await lambda_handler(event, None) 
        print("--- Respuesta de Lambda generada ---")
        
        return response
    except Exception as e:
        print(f"Error fatal en el handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

