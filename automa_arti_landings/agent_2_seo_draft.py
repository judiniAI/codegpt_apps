import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Cargar la clave de la API
codegpt_api_key = os.getenv("CODEGPT_API_KEY")

def generar_seo_draft(outline_seo, average_word_count=1500):
    """
    Genera un borrador SEO usando el Agent 2 | SEO Draft
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
        "agentId": "02aa8c45-b532-43c0-83aa-415ddc93262f",  # ID del Agent 2 | SEO Draft
        "stream": False,
        "messages": [
            {
                "content": (
                    f"Write a complete SEO-optimized article draft based on this outline. "
                    f"Target word count: {target_word_count} words.\n\n"
                    f"Outline:\n{outline_seo}"
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
        print(f"Error en generar_seo_draft: {err}")
        return str(err)

def procesar_draft(topic, outline_seo, average_word_count=1500):
    """
    Procesa el outline SEO y genera un borrador completo
    """
    if not outline_seo:
        return "No hay outline SEO para generar el borrador."
    
    draft_seo = generar_seo_draft(outline_seo, average_word_count)
    
    if draft_seo:
        resultado = f"SEO Draft para '{topic}':\n\n"
        resultado += "----------------------------------------\n\n"
        resultado += draft_seo
        resultado += "\n\n----------------------------------------"
        
        # Contar palabras en el borrador
        word_count = len(draft_seo.split())
        resultado += f"\n\nPalabras totales: {word_count}"
        
        return resultado
    
    return "No se pudo generar el borrador SEO."

# Ejemplo de uso
if __name__ == "__main__":
    # Este código asume que ya tienes el outline del Agent 1
    from agent_0_researcher import generar_informe_completo
    from agent_1_seo_outline import procesar_outline
    
    topic = "Python 3.14"
    informe_investigacion = generar_informe_completo(topic)
    outline_seo = procesar_outline(topic, informe_investigacion)
    draft = procesar_draft(topic, outline_seo)
    print(draft)