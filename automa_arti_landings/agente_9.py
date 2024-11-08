import os
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API Key desde las variables de entorno
api_key = os.getenv("CODEGPT_API_KEY")

def generar_seccion_hero(topic, redirect_url, headline, subheadline, cta):
    # URL del endpoint de CodeGPT
    url = "https://api.codegpt.co/api/v1/chat/completions"
    
    # Datos para la solicitud POST
    data = {
        "agentId": "426c4712-262b-482e-be64-8aa3a28ec3c5",  # Reemplaza con el ID del agente
        "stream": False,
        "format": "json",
        "messages": [
            {
                "content": f"Topic: {topic}\nRedirect URL: {redirect_url}\nHeadline: {headline}\nSubheadline: {subheadline}\nCTA: {cta}",
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
        seccion_hero_html_js = result.get("choices", [{}])[0].get("message", {}).get("completion", "No se pudo generar la sección Hero.")
        # Eliminar etiquetas de bloque de código si están presentes
        return seccion_hero_html_js
    else:
        return "No se pudo generar la sección Hero."

# Ejemplo de uso
# topic = "Python"
# redirect_url = "https://example.com"
# headline = "Unlock Python Potential"
# subheadline = "Enhance your coding skills with AI-powered insights."
# cta = "Try Python AI Assistant Now"
# seccion_hero_html_js = generar_seccion_hero(topic, redirect_url, headline, subheadline, cta)
# print(seccion_hero_html_js)