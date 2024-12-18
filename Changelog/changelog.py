import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

# Cargar variables de entorno
load_dotenv()

# Obtener variables de entorno
api_key_codegpt = os.getenv('API_KEY_CODEGPT')
org_id = os.getenv('ORG_ID')
agent_id = os.getenv('AGENT_ID')
hubspot_api_key = os.getenv('HUBSPOT_API_KEY')
group_id = os.getenv('GROUP_ID')
name_platform = os.getenv('NAME_PLATFORM')
discord_token = os.getenv('DISCORD_TOKEN')
discord_channel_id = os.getenv('DISCORD_CHANNEL_ID')

fecha = datetime.today().strftime("%d/%m/%Y")

def obtener_mensajes_de_discord(token, canal_id, fecha):
    """
    Obtiene los mensajes de un canal de Discord en una fecha determinada.

    Args:
        token (str): Token del bot de Discord.
        canal_id (str): ID del canal de Discord.
        fecha (str): Fecha en formato "dd/mm/yyyy".

    Returns:
        list: Lista de mensajes obtenidos del canal de Discord.

    Raises:
        Exception: Si ocurre un error al obtener los mensajes.
    """
    url = f"https://discord.com/api/v9/channels/{canal_id}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }
    
    # Convertir la fecha a timestamp
    fecha_fin = datetime.strptime(fecha, "%d/%m/%Y")
    fecha_inicio = fecha_fin - timedelta(days=30)
    timestamp_inicio = int(fecha_inicio.timestamp())
    timestamp_fin = int(fecha_fin.timestamp())
    
    params = {
        "after": timestamp_inicio,
        "before": timestamp_fin,
        "limit": 100
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        mensajes = response.json()
        return mensajes
    else:
        raise Exception(f"Error al obtener mensajes de Discord: {response.status_code} - {response.text}")

def chat_with_agent(agent_id, user_message, api_key, org_id):
    """
    Envía un mensaje a un agente y obtiene la respuesta.

    Args:
        agent_id (str): ID del agente.
        user_message (str): Mensaje del usuario.
        api_key (str): Clave API para autenticación.
        org_id (str): ID de la organización.

    Returns:
        dict: Respuesta del agente.

    Raises:
        Exception: Si ocurre un error al obtener la respuesta del agente.
    """
    url = "https://api.codegpt.co/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "CodeGPT-Org-Id": org_id
    }
    data = {
        "agentId": agent_id,
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ],
        "format": "text",
        "stream": False
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        completion = response.json()
        return completion
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")

def subir_a_hubspot(topic, html_content, hubspot_api_key, group_id, name_platform):
    """
    Sube el contenido generado como página de sitio en HubSpot.

    Args:
        topic (str): Título del contenido.
        html_content (str): Contenido HTML a subir.
        hubspot_api_key (str): Clave API de HubSpot.
        group_id (str): ID del grupo de contenido.
        name_platform (str): Nombre de la plataforma.

    Returns:
        int: Código de estado de la respuesta de la API.

    Raises:
        Exception: Si ocurre un error al subir el contenido.
    """
    headers = {
        "Authorization": hubspot_api_key,
        "Content-Type": "application/json"
    }
    data = {
        "name": f"{topic} {name_platform}",
        "slug": "/version",
        "state": "DRAFT",
        "contentGroupId": group_id,
        "htmlTitle": topic, 
        "postBody": html_content,
        "blogAuthorId": 169677582703,
        "language": "en",
        "blogAuthor": {
            "id": 169677582703,            
            "language": "en"
            },
        "primaryLanguage": "en",    
        "metaDescription": f"Content about {topic}",
        "useFeaturedImage": False,
        "enableFeaturedImage": False,
        "languageSettings": {
            "language": "en",
            "primaryLanguage": "en",
            "enableLanguageFallback": True
        }
    }

    response = requests.post(
        "https://api.hubapi.com/cms/v3/blogs/posts", 
        headers=headers, 
        json=data
    )
    
    if response.status_code in [200, 201]:
        print("Página de sitio subida exitosamente en HubSpot.")
    else:
        print(f"Error al subir la página de sitio en HubSpot: {response.status_code} - {response.text}")
    return response.status_code

try:
    # Obtener mensajes de Discord
    mensajes = obtener_mensajes_de_discord(discord_token, discord_channel_id, fecha)
    if mensajes:
        # Formatear los mensajes para el agente
        user_message = "\n".join([f"{msg['author']['username']}: {msg['content']}" for msg in mensajes])
        
        # Enviar los mensajes al agente
        response1 = chat_with_agent(agent_id, user_message, api_key_codegpt, org_id)
        print("Respuesta del agente:", response1)
        
        # Extraer el contenido de la respuesta del agente
        agent_response_content = response1
        if agent_response_content:
            topic = "Changelog"
            subir_a_hubspot(topic, agent_response_content, hubspot_api_key, group_id, name_platform)
        else:
            print("No se pudo obtener el contenido de la respuesta del agente.")
    else:
        print("No se encontraron mensajes en la fecha especificada.")
except Exception as e:
    print(e)
