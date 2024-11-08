import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

# Cargar las claves de la API
google_api_key = os.getenv("GOOGLE_API_KEY")
google_cx = os.getenv("GOOGLE_CX")
codegpt_api_key = os.getenv("CODEGPT_API_KEY")

def scrape_google(topic, num_pages=1):
    search_url = "https://www.googleapis.com/customsearch/v1"
    results = []

    for page in range(num_pages):
        params = {
            "q": topic,
            "cx": google_cx,
            "key": google_api_key,
            "start": page * 10 + 1
        }
        response = requests.get(search_url, params=params)
        
        if response.status_code == 200:
            search_results = response.json()
            for item in search_results.get('items', []):
                title = item.get('title')
                link = item.get('link')
                if title and link:
                    results.append((title, link))
        else:
            print(f"Error al realizar la búsqueda en Google: {response.status_code}")

    return results

def obtener_contenido_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')
            content = ' '.join([para.get_text() for para in paragraphs])
            return content
        else:
            return f"Error al acceder a la URL: {url}"
    except Exception as e:
        return f"Error al acceder a la URL: {url} - {str(e)}"

def generar_informe(topic, keyword, search_results):
    url = "https://api.codegpt.co/api/v1/chat/completions"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {codegpt_api_key}"
    }

    contenidos = []
    for title, link in search_results[:3]:
        contenido = obtener_contenido_url(link)
        contenidos.append(f"Title: {title}\nURL: {link}\nContent: {contenido}\n")
    
    contenido_texto = "\n".join(contenidos)
    
    prompt = f"""
    Generate a detailed report on {topic} related to {keyword} using the following information:
    {contenido_texto}
    
    Please structure the report with the following sections:
    1. **Suggested Article Titles and Headlines:**
    (List 10 engaging and SEO-friendly titles that combine {topic} with {keyword})
    
    2. **Suggestions for Subtopics and Unique Angles:**
    (List main subtopics to cover)
    
    3. **Key Points and Information:**
    (Main facts and data)
    
    4. **Expert Insights and Quotes:**
    (Notable opinions and statements)
    
    5. **Current Trends and Updates:**
    (Latest developments)
    """
    
    data = {
        "agentId": "a188a1e6-21a9-4c6b-b7b8-2b5764700993",
        "stream": False,
        "messages": [
            {
                "content": prompt,
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
        print(f"Error en generar_informe: {err}")
        return str(err)

def extraer_titulos_sugeridos(informe, keyword=""):
    """Extrae los títulos sugeridos del informe y los optimiza con la keyword."""
    try:
        # Buscar la sección de títulos con diferentes marcadores posibles
        markers = [
            ("**Suggested Article Titles and Headlines:**", "**Suggestions for Subtopics"),
            ("1. **Suggested Article Titles and Headlines:**", "2. **Suggestions"),
            ("Suggested Article Titles:", "Suggestions for Subtopics"),
            ("1. Suggested Article Titles", "2.")
        ]
        
        titles_section = None
        for start_marker, end_marker in markers:
            if start_marker in informe:
                start_idx = informe.find(start_marker) + len(start_marker)
                end_idx = informe.find(end_marker, start_idx)
                if end_idx != -1:
                    titles_section = informe[start_idx:end_idx].strip()
                    break
        
        if not titles_section:
            return []

        # Procesar los títulos
        raw_titles = []
        for line in titles_section.split('\n'):
            # Limpiar la línea de marcadores comunes
            clean_line = line.strip()
            for char in ['*', '-', '•', '>', '#']:
                clean_line = clean_line.strip(char)
            
            # Eliminar números al inicio de la línea
            while clean_line and clean_line[0].isdigit():
                clean_line = clean_line[1:].strip('.')
            
            clean_line = clean_line.strip()
            
            if clean_line and len(clean_line) > 10 and not clean_line.startswith(('**', '1.', '2.')):
                raw_titles.append(clean_line)

        # Optimizar títulos con la keyword si es necesario
        optimized_titles = []
        keyword = keyword.lower().strip() if keyword else ""
        
        for title in raw_titles:
            if not title:
                continue
                
            if keyword and keyword not in title.lower():
                # Solo agregar keyword si no está ya presente
                if title.endswith(':'):
                    title = title[:-1].strip()
                optimized_title = f"{title} - {keyword.title()}"
            else:
                optimized_title = title
            
            # Verificar longitud y duplicados
            if 20 <= len(optimized_title) <= 100 and optimized_title not in optimized_titles:
                optimized_titles.append(optimized_title)
        
        # Si no se encontraron títulos y hay una keyword, crear algunos básicos
        if not optimized_titles and keyword:
            topic_templates = [
                f"Complete Guide to {keyword.title()}",
                f"How to Master {keyword.title()} - Essential Tips",
                f"Understanding {keyword.title()} - Comprehensive Guide",
                f"{keyword.title()} Best Practices and Advanced Techniques",
                f"Getting Started with {keyword.title()} - Beginner's Guide"
            ]
            optimized_titles.extend(topic_templates)
        
        return optimized_titles[:10]  # Limitar a 10 títulos
        
    except Exception as e:
        print(f"Error al extraer títulos: {e}")
        return []

def generar_informe_completo(topic, keyword=""):
    search_query = f"{topic} {keyword}".strip()
    search_results = scrape_google(search_query)
    
    if not search_results:
        return "No se encontraron resultados de búsqueda."
    
    informe_codegpt = generar_informe(topic, keyword, search_results)
    
    if informe_codegpt and isinstance(informe_codegpt, (str, dict)):
        informe = f"Informe sobre '{search_query}':\n\n"
        informe += "Resultados de Búsqueda:\n"
        for i, (title, link) in enumerate(search_results, start=1):
            informe += f"{i}. {title}\n   {link}\n"
        
        informe_texto = informe_codegpt if isinstance(informe_codegpt, str) else str(informe_codegpt)
        
        informe += "\nAnálisis Detallado:\n" + informe_texto

        suggested_titles = extraer_titulos_sugeridos(informe_texto)
        
        if suggested_titles:
            informe += "\n\nTítulos sugeridos para artículos:\n"
            for i, title in enumerate(suggested_titles, 1):
                informe += f"{i}. {title}\n"

        return informe
    
    return "No se pudieron obtener resultados suficientes para generar el informe."

if __name__ == "__main__":
    topic = "SQL"
    keyword = "AI, CodeGPT"
    informe = generar_informe_completo(topic, keyword)
    print(informe)