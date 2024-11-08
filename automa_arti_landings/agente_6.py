import os
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API Key desde las variables de entorno
api_key = os.getenv("CODEGPT_API_KEY")

def generar_como_funciona(topic):
    # URL del endpoint de CodeGPT
    url = "https://api.codegpt.co/api/v1/chat/completions"
    
    # Datos para la solicitud POST
    data = {
        "agentId": "35d4cdd4-9b40-461a-b862-4f1b6ab957e3",  # Reemplaza con el ID del agente
        "stream": False,
        "format": "json",
        "messages": [
            {
                "content": f"Topic: {topic}",
                "role": "user"
            }
        ]
    }
    
    # Encabezados para la solicitud
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Realizar la solicitud POST al endpoint de CodeGPT
    response = requests.post(url, json=data, headers=headers)
    
    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        # Obtener los datos JSON de la respuesta
        result = response.json()
        como_funciona_html = result.get("choices", [{}])[0].get("message", {}).get("completion", "No se pudo generar la sección 'Cómo Funciona'.")
        # Eliminar etiquetas de bloque de código si están presentes
        return como_funciona_html
    else:
        return "No se pudo generar la sección 'Cómo Funciona'."