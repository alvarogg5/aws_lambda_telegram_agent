# /scripts/local_server.py

import json
from fastapi import FastAPI, Request, HTTPException
import os
import sys

# --- Setup Paths and Env ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
    
# Importamos la lógica ASÍNCRONA directamente, NO el handler de Lambda
from src.telegram_agent_aws.infrastructure.lambda_function import process_update

# Define the FastAPI app
app = FastAPI()

@app.post("/")
async def handle_webhook(request: Request):
    try:
        # El body del webhook es el update_data que necesitamos
        update_data = await request.json()
        
        print("\n--- Recibida petición de Telegram (Local Server) ---")
        
        # Llamamos a nuestra corutina directamente, sin imitar a Lambda
        await process_update(update_data)
        
        print("--- Proceso de update completado ---")
        
        # Devolvemos un OK simple. La respuesta al usuario se envía dentro de process_update.
        return {"ok": True}
        
    except Exception as e:
        print(f"Error fatal en el handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

