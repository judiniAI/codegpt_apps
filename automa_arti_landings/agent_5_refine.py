import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Cargar la clave de la API
codegpt_api_key = os.getenv("CODEGPT_API_KEY")

def formatear_html(contenido_ajustado):
    """
    Formatea el contenido en HTML usando el Agent 5 | Refine
    """
    url = "https://api.codegpt.co/api/v1/chat/completions"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {codegpt_api_key}"
    }
    
    data = {
        "agentId": "9b6094b2-8607-48c0-a2a0-1d6264f97e23",
        "stream": False,
        "messages": [
            {
                "content": (
                    "Format this article in clean, well-structured HTML:\n\n"
                    f"{contenido_ajustado}"
                ),
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
        print(f"Error en formatear_html: {err}")
        return str(err)

def procesar_formato_final(topic, contenido_ajustado):
    """
    Procesa el contenido ajustado y genera la versión final en HTML
    """
    if not contenido_ajustado:
        return "No hay contenido para formatear."
    
    contenido_html = formatear_html(contenido_ajustado)
    
    if contenido_html:
        # Crear un archivo HTML con el contenido
        filename = f"{topic.lower().replace(' ', '_')}_article.html"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(contenido_html)
            
            return contenido_html
            
        except Exception as err:
            return f"Error al guardar el archivo HTML: {err}"
    
    return "No se pudo formatear el contenido en HTML."
# Ejemplo de uso
if __name__ == "__main__":
    from agent_0_researcher import generar_informe_completo
    from agent_1_seo_outline import procesar_outline
    from agent_2_seo_draft import procesar_draft
    from agent_3_content_enrichment import procesar_enriquecimiento
    from agent_4_tone import procesar_tono
    
    topic = "Python 3.14"
    informe_investigacion = generar_informe_completo(topic)
    outline_seo = procesar_outline(topic, informe_investigacion)
    draft_seo = procesar_draft(topic, outline_seo)
    contenido_enriquecido = procesar_enriquecimiento(topic, draft_seo)
    contenido_ajustado = procesar_tono(topic, contenido_enriquecido)
    
    contenido_final = procesar_formato_final(topic, contenido_ajustado)
    print(contenido_final)
