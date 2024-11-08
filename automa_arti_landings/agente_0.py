import os 
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()


###########################################################################################################
#### ANDRES TENE EN CUENTA QUE GOOGLE DA GRATIS 100 CONSULTAS GRATIS POR DIA CON LA API, DESPUES ES PAGO###
###########################################################################################################
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

def generar_informe(topic, search_results):
    url = "https://api.codegpt.co/api/v1/chat/completions"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {codegpt_api_key}"
    }
    
    # Obtener contenido de los primeros tres enlaces
    contenidos = []
    for title, link in search_results[:3]:
        contenido = obtener_contenido_url(link)
        contenidos.append(f"Title: {title}\nURL: {link}\nContent: {contenido}\n")
    
    contenido_texto = "\n".join(contenidos)
    
    data = {
        "agentId": "f4b749d7-8a42-4d9b-890d-c1f8d68159f4",  # Agente 0
        "stream": False,
        "format": "json",
        "messages": [
            {
                "content": f"Generate a detailed report on {topic} using the following information:\n{contenido_texto}",
                "role": "user"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        response_json = response.json()
        if 'choices' in response_json and len(response_json['choices']) > 0:
            return response_json['choices'][0]['message']['completion']  # Cambiar 'content' por 'completion'
        else:
            return 'No se pudo generar el informe.'
    else:
        return f"Error al generar el informe: {response.status_code}"

def generar_informe_completo(topic):
    # Obtener resultados de búsqueda de Google
    search_results = scrape_google(topic)
    
    # Generar informe de CodeGPT usando los primeros tres enlaces
    informe_codegpt = generar_informe(topic, search_results)
    
    # Combinar resultados de búsqueda con el informe de CodeGPT
    if search_results:
        informe = f"Informe sobre '{topic}':\n\n"
        informe += "Resultados de Búsqueda:\n"
        for i, (title, link) in enumerate(search_results, start=1):
            informe += f"{i}. {title}\n   {link}\n"
        informe += "\n" + informe_codegpt
        return informe
    else:
        return "No se encontraron resultados para generar el informe."

# Ejemplo de uso
if __name__ == "__main__":
    topic = "Python"
    informe = generar_informe_completo(topic)
    print(informe)
