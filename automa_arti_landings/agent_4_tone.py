import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Cargar la clave de la API
codegpt_api_key = os.getenv("CODEGPT_API_KEY")

def ajustar_tono(contenido_enriquecido, search_intent=None, brand_guidelines=None):
    """
    Ajusta el tono y estilo del contenido usando el Agent 4 | Tone
    """
    url = "https://api.codegpt.co/api/v1/chat/completions"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {codegpt_api_key}"
    }
    
    # Preparar el contexto con la información disponible
    context = "Refine this article considering the following:\n\n"
    if search_intent:
        context += f"Search Intent and Keywords:\n{search_intent}\n\n"
    if brand_guidelines:
        context += f"Brand Guidelines:\n{brand_guidelines}\n\n"
    
    data = {
        "agentId": "09a186fe-a345-4af7-9af2-743d02755104",  # ID del Agent 4 | Tone
        "stream": False,
        "messages": [
            {
                "content": (
                    f"{context}"
                    f"Article to Refine:\n{contenido_enriquecido}"
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
        print(f"Error en ajustar_tono: {err}")
        return str(err)

def procesar_tono(topic, contenido_enriquecido, search_intent=None, brand_guidelines=None):
    """
    Procesa el contenido enriquecido y ajusta su tono y estilo
    """
    if not contenido_enriquecido:
        return "No hay contenido para ajustar el tono."
    
    contenido_ajustado = ajustar_tono(contenido_enriquecido, search_intent, brand_guidelines)
    
    if contenido_ajustado:
        resultado = f"Contenido con Tono Ajustado para '{topic}':\n\n"
        resultado += "********************************************\n\n"
        resultado += contenido_ajustado
        resultado += "\n\n********************************************"
        
        # Contar palabras en el contenido ajustado
        word_count = len(contenido_ajustado.split())
        resultado += f"\n\nEstadísticas finales:"
        resultado += f"\n- Palabras totales: {word_count}"
        
        return resultado
    
    return "No se pudo ajustar el tono del contenido."

# Ejemplo de uso
if __name__ == "__main__":
    # Este código asume que ya tienes el contenido enriquecido del Agent 3
    from agent_0_researcher import generar_informe_completo
    from agent_1_seo_outline import procesar_outline
    from agent_2_seo_draft import procesar_draft
    from agent_3_content_enrichment import procesar_enriquecimiento
    
    topic = "Python 3.14"
    informe_investigacion = generar_informe_completo(topic)
    outline_seo = procesar_outline(topic, informe_investigacion)
    draft_seo = procesar_draft(topic, outline_seo)
    contenido_enriquecido = procesar_enriquecimiento(topic, draft_seo)
    
    # Ejemplo de search_intent y brand_guidelines
    search_intent = "Users are looking for detailed information about Python 3.14 features and improvements"
    brand_guidelines = "Professional but friendly tone, focus on practical applications"
    
    contenido_ajustado = procesar_tono(topic, contenido_enriquecido, search_intent, brand_guidelines)
    print(contenido_ajustado)