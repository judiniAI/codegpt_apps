import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Cargar la clave de la API
codegpt_api_key = os.getenv("CODEGPT_API_KEY")

def enriquecer_contenido(draft_seo, average_word_count=1500):
    """
    Enriquece el contenido del borrador usando el Agent 3 | Content Enrichment
    """
    url = "https://api.codegpt.co/api/v1/chat/completions"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {codegpt_api_key}"
    }
    
    # Calcular el objetivo de palabras (30% más que el promedio o mínimo 1500)
    target_word_count = max(int(average_word_count * 1.3), 1500)
    
    data = {
        "agentId": "f7900685-80c7-4a6e-884d-b10926c01224",  # ID del Agent 3 | Content Enrichment
        "stream": False,
        "messages": [
            {
                "content": (
                    f"Enrich this article draft with additional valuable information, "
                    f"examples, data, and references. Target word count: {target_word_count} words.\n\n"
                    f"Draft Article:\n{draft_seo}"
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
        print(f"Error en enriquecer_contenido: {err}")
        return str(err)

def procesar_enriquecimiento(topic, draft_seo, average_word_count=1500):
    """
    Procesa el borrador SEO y genera una versión enriquecida
    """
    if not draft_seo:
        return "No hay borrador SEO para enriquecer."
    
    contenido_enriquecido = enriquecer_contenido(draft_seo, average_word_count)
    
    if contenido_enriquecido:
        resultado = f"Contenido Enriquecido para '{topic}':\n\n"
        resultado += "============================================\n\n"
        resultado += contenido_enriquecido
        resultado += "\n\n============================================"
        
        # Contar palabras en el contenido enriquecido
        word_count = len(contenido_enriquecido.split())
        target_word_count = max(int(average_word_count * 1.3), 1500)
        
        resultado += f"\n\nEstadísticas del contenido:"
        resultado += f"\n- Palabras totales: {word_count}"
        resultado += f"\n- Objetivo de palabras: {target_word_count}"
        resultado += f"\n- Diferencia: {word_count - target_word_count} palabras"
        
        return resultado
    
    return "No se pudo enriquecer el contenido."

# Ejemplo de uso
if __name__ == "__main__":
    # Este código asume que ya tienes el draft del Agent 2
    from agent_0_researcher import generar_informe_completo
    from agent_1_seo_outline import procesar_outline
    from agent_2_seo_draft import procesar_draft
    
    topic = "Python 3.14"
    informe_investigacion = generar_informe_completo(topic)
    outline_seo = procesar_outline(topic, informe_investigacion)
    draft_seo = procesar_draft(topic, outline_seo)
    contenido_enriquecido = procesar_enriquecimiento(topic, draft_seo)
    print(contenido_enriquecido)