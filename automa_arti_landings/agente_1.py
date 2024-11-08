import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("CODEGPT_API_KEY")

def generar_titular(topic, report):
    url = "https://api.codegpt.co/api/v1/chat/completions"
    
    data = {
        "agentId": "8f83ef1f-135a-4e33-ae4e-b16f32ef2d86",  
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
        titular = result.get("choices", [{}])[0].get("message", {}).get("completion", "No se pudo generar el titular.")
        return titular
    else:
        return "No se pudo generar el titular."