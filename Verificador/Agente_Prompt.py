import requests

API_URL = "https://api.codegpt.co/api/v1/agent"
ANALIZADOR_ID = "ab91b866-da46-480b-9d17-19d7d4c6d208"  # ID del agente analizador

def obtener_agentes(api_key, org_id):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "CodeGPT-Org-Id": org_id
    }

    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error obtaining agents: {e}")
        return []

def imprimir_agentes(agentes):
    if not agentes:
        print("No agents found.")
        return

    for agent in agentes:
        print(f"ID: {agent['id']}")
        print(f"Name: {agent['name']}")
        print(f"Agent type: {agent['agent_type']}")
        print(f"Model: {agent['model']}")
        print(f"Is public: {agent['is_public']}")
        print(f"Created at: {agent['created_at']}")
        print(f"Welcome message: {agent['welcome']}")
        print("---")

def obtener_nombre_agente(agent_id, agentes):
    for agente in agentes:
        if agente['id'] == agent_id:
            return agente['name']
    return "Unknown Agent"

def obtener_prompt_agente(agent_id, api_key, org_id):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "CodeGPT-Org-Id": org_id
    }

    try:
        response = requests.get(f"{API_URL}/{agent_id}", headers=headers)
        response.raise_for_status()
        agent_data = response.json()
        return agent_data.get('prompt', "No se encontró el prompt del agente.")
    except requests.RequestException as e:
        print(f"Error al obtener el prompt del agente: {e}")
        return None

def analizar_prompt(prompt, api_key, org_id):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "CodeGPT-Org-Id": org_id
    }

    payload = {
        "agentId": ANALIZADOR_ID,
        "stream": False,
        "format": "json",
        "messages": [
            {
                "content": f"Analiza el siguiente prompt de un agente:\n\n{prompt}",
                "role": "user"
            }
        ]
    }
    
    try:
        response = requests.post("https://api.codegpt.co/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()

        response_json = response.json()
        # Ajuste para extraer el campo "content" en lugar de "completion"
        content = response_json.get('choices', [{}])[0].get('message', {}).get('content', None)
        
        if content:
            return content
        else:
            return f"No se encontró el campo content. Respuesta completa: {response_json}"

    except requests.RequestException as e:
        print(f"Error al analizar el prompt: {e}")
        return None
