import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Cargar la clave de la API
codegpt_api_key = os.getenv("CODEGPT_API_KEY")

def generar_outline_seo(informe_investigacion):
    """
    Genera un outline SEO usando el Agent 1 | SEO Outline
    """
    url = "https://api.codegpt.co/api/v1/chat/completions"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {codegpt_api_key}"
    }
    
    data = {
        "agentId": "6756365b-f10b-4cb1-a4ae-9565cc3cfeda",  # ID del Agent 1 | SEO Outline
        "stream": False,
        "messages": [
            {
                "content": f"Based on this research report, create an SEO outline:\n\n{informe_investigacion}",
                "role": "user"
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        response_json = response.json()
        
        if isinstance(response_json, str):
            return response_json
        elif 'choices' in response_json and len(response_json['choices']) > 0:
            choice = response_json['choices'][0]
            if isinstance(choice, str):
                return choice
            elif isinstance(choice, dict):
                if 'message' in choice:
                    return choice['message'].get('content', '')
                elif 'text' in choice:
                    return choice['text']
                else:
                    return str(choice)
            
        return response_json
            
    except Exception as err:
        print(f"Error en generar_outline_seo: {err}")
        return str(err)

def procesar_outline(topic, informe_investigacion):
    """
    Procesa el informe de investigación y genera un outline SEO
    """
    if not informe_investigacion:
        return "No hay informe de investigación para generar el outline."
    
    outline_seo = generar_outline_seo(informe_investigacion)
    
    if outline_seo:
        resultado = f"SEO Outline para '{topic}':\n\n"
        resultado += outline_seo
        return resultado
    
    return "No se pudo generar el outline SEO."

# Ejemplo de uso
if __name__ == "__main__":
    from agent_0_researcher import generar_informe_completo
    
    topic = "Python 3.14"
    informe_investigacion = generar_informe_completo(topic)
    outline = procesar_outline(topic, informe_investigacion)
    print(outline)