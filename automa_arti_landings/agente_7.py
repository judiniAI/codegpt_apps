import os
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API Key desde las variables de entorno
api_key = os.getenv("CODEGPT_API_KEY")

def generar_cta_final(topic, redirect_url):
    # URL del endpoint de CodeGPT
    url = "https://api.codegpt.co/api/v1/chat/completions"
    
    # Datos para la solicitud POST
    data = {
        "agentId": "74d58a56-9dbb-495a-869a-d45ece2fb785",  # Reemplaza con el ID del agente
        "stream": False,
        "format": "json",
        "messages": [
            {
                "content": f"Topic: {topic}\nRedirect URL: {redirect_url}",
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
        cta_final_html_js = result.get("choices", [{}])[0].get("message", {}).get("completion", "No se pudo generar la CTA final.")
        # Eliminar etiquetas de bloque de código si están presentes
        return cta_final_html_js
    else:
        return "No se pudo generar la CTA final."