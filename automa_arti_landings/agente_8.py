import os
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API Key desde las variables de entorno
api_key = os.getenv("CODEGPT_API_KEY")

def generar_faqs(topic, report):
    # URL del endpoint de CodeGPT
    url = "https://api.codegpt.co/api/v1/chat/completions"
    
    # Datos para la solicitud POST
    data = {
        "agentId": "054b949c-86fb-4077-a404-1390d59cdf30",  # Reemplaza con el ID del agente
        "stream": False,
        "format": "json",
        "messages": [
            {
                "content": f"Topic: {topic}\nReport: {report}",
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
        faqs_html = result.get("choices", [{}])[0].get("message", {}).get("completion", "No se pudo generar las FAQs.")
        # Eliminar etiquetas de bloque de código si están presentes
        return faqs_html
    else:
        return "No se pudo generar las FAQs."

# Ejemplo de uso
# topic = "Python"
# report = "Python is a versatile programming language..."
# faqs_html = generar_faqs(topic, report)
# print(faqs_html)