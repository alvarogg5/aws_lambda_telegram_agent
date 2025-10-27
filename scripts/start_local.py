# /scripts/start_local.py
import os
import sys
import subprocess
import time
import httpx  # Importamos la librería que acabamos de instalar
from dotenv import load_dotenv
import atexit

# --- Setup Paths and Env ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.telegram_agent_aws.config import settings

TOKEN = settings.TELEGRAM_BOT_TOKEN
print("Configuración (incl. Token DEV) cargada.")


# --- Gestión de Procesos ---
processes = []
def cleanup():
    """Función para asegurar que ngrok y uvicorn se cierren al salir."""
    print("\nCerrando procesos (ngrok y uvicorn)...")
    for p in processes:
        p.terminate()
        p.wait()
    print("Procesos cerrados. Adiós.")

# Registra la función cleanup para que se ejecute al salir
atexit.register(cleanup)

# --- Paso 1: Iniciar Servidor Local (Uvicorn) ---
print("Iniciando servidor local (Uvicorn)...")
# Comando para que 'uv' ejecute 'uvicorn' apuntando a tu app
server_cmd = [
    "uv", "run", "uvicorn", 
    "scripts.local_server:app",  # Apunta a <fichero>:<variable_app>
    "--host", "0.0.0.0",
    "--port", "8000"
]

server_process = subprocess.Popen(server_cmd, text=True, encoding='utf-8')
processes.append(server_process)
print(f"Servidor local iniciado (PID: {server_process.pid})")
time.sleep(3) # Darle tiempo a Uvicorn para arrancar

# --- Paso 2: Iniciar Ngrok ---
print("Iniciando ngrok...")
ngrok_process = subprocess.Popen(["ngrok", "http", "8000"], text=True, encoding='utf-8')
processes.append(ngrok_process)
print(f"Ngrok iniciado (PID: {ngrok_process.pid})")

# --- Paso 3: Obtener URL pública de Ngrok ---
print("Esperando a que ngrok genere la URL... (max 10s)")
public_url = None
client = httpx.Client()
for _ in range(10): # Intentar durante 10 segundos
    time.sleep(1)
    try:
        # Ngrok expone una API local en el puerto 4040
        response = client.get("http://127.0.0.1:4040/api/tunnels")
        response.raise_for_status() 
        data = response.json()
        
        # Buscar la URL 'https' en la respuesta
        for tunnel in data["tunnels"]:
            if tunnel["proto"] == "https":
                public_url = tunnel["public_url"]
                break
        if public_url:
            break # Salir del bucle si la encontramos
    except Exception:
        # Si falla (porque ngrok aún no está listo), reintentar
        continue 

if not public_url:
    print("Error: No se pudo obtener la URL de ngrok después de 10s.")
    print("Asegúrate de que ngrok está autenticado (`ngrok config add-authtoken ...`)")
    exit(1)

print(f"URL pública de ngrok obtenida: {public_url}")

# --- Paso 4: Configurar Webhook de Telegram ---
print("Configurando webhook de Telegram...")
try:
    set_webhook_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    response = httpx.post(set_webhook_url, data={"url": public_url})
    response.raise_for_status() # Lanza error si Telegram responde mal
    
    if response.json().get("ok"):
        print("¡Webhook configurado con éxito!")
        print(f"URL: {public_url}")
    else:
        print(f"Error de Telegram: {response.json()}")
        exit(1)
except Exception as e:
    print(f"Error al configurar el webhook: {e}")
    exit(1)

# --- Mantener vivo ---
print("\n--- ¡Todo listo! ---")
print("Servidor local y ngrok están en funcionamiento.")
print("Habla con tu bot de desarrollo para probar.")
print("Presiona Ctrl+C en esta terminal para detener todo.")
try:
    # Esperar a que el proceso del servidor termine (o a que el usuario pulse Ctrl+C)
    server_process.wait()
except KeyboardInterrupt:
    pass # Ctrl+C activará la función cleanup
finally:
    client.close()