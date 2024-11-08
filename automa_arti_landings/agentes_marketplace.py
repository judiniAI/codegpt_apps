import os
import requests
import streamlit as st
from bs4 import BeautifulSoup
from agente_0 import generar_informe_completo
from agente_1 import generar_titular
from agente_2 import generar_subtitulo
from agente_3 import generar_cta
from agente_4 import generar_titulo_producto
from agente_5 import generar_texto_introductorio
from agente_6 import generar_como_funciona
from agente_7 import generar_cta_final
from agente_8 import generar_faqs
from agente_9 import generar_seccion_hero
from agente_10 import generar_seccion_why
from agent_0_researcher import generar_informe_completo as generar_informe_articulo
from agent_1_seo_outline import procesar_outline
from agent_2_seo_draft import procesar_draft
from agent_3_content_enrichment import procesar_enriquecimiento
from agent_4_tone import procesar_tono
from agent_5_refine import procesar_formato_final
from dotenv import load_dotenv

# Configuración de la API de HubSpot
HUBSPOT_API_URL = "https://api.hubapi.com/cms/v3/pages/site-pages"
HUBSPOT_BLOG_URL = "https://api.hubapi.com/cms/v3/blogs/posts"

# Cargar las variables del archivo .env si existen
load_dotenv()

# Solicitar credenciales en Streamlit y permitir que el usuario las sobrescriba
CODEGPT_API_KEY = st.text_input("Ingrese su CODEGPT_API_KEY", value=os.getenv("CODEGPT_API_KEY"), type="password")
GOOGLE_API_KEY = st.text_input("Ingrese su GOOGLE_API_KEY", value=os.getenv("GOOGLE_API_KEY"), type="password")
GOOGLE_CX = st.text_input("Ingrese su GOOGLE_CX", value=os.getenv("GOOGLE_CX"))
HUBSPOT_ACCESS_TOKEN = st.text_input("Ingrese su HUBSPOT_ACCESS_TOKEN", value=os.getenv("HUBSPOT_ACCESS_TOKEN"), type="password")

# Sobrescribir variables de entorno si el usuario ingresa nuevas credenciales
if CODEGPT_API_KEY:
    os.environ["CODEGPT_API_KEY"] = CODEGPT_API_KEY
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
if GOOGLE_CX:
    os.environ["GOOGLE_CX"] = GOOGLE_CX
if HUBSPOT_ACCESS_TOKEN:
    os.environ["HUBSPOT_ACCESS_TOKEN"] = HUBSPOT_ACCESS_TOKEN

# Mostrar mensaje de éxito
if CODEGPT_API_KEY and GOOGLE_API_KEY and GOOGLE_CX and HUBSPOT_ACCESS_TOKEN:
    st.success("Las credenciales se han ingresado correctamente.")
else:
    st.warning("Por favor, complete todos los campos para continuar.")





headers = {
    "Authorization": HUBSPOT_ACCESS_TOKEN,
    "Content-Type": "application/json"
}

st.title("Generador de Landing y Artículo para HubSpot")

def extraer_titulos_sugeridos(informe, keyword=""):
    """Extrae los títulos sugeridos del informe del agente 0."""
    try:
        # Buscar la sección específica como está en el informe
        start_marker = "**1. Suggested Article Titles and Headlines:**"
        end_marker = "**2. Suggestions for Subtopics and Unique Angles:**"
        
        if start_marker in informe:
            start_idx = informe.find(start_marker) + len(start_marker)
            end_idx = informe.find(end_marker)
            
            if end_idx == -1:
                end_idx = len(informe)
                
            titles_section = informe[start_idx:end_idx].strip()
            
            # Extraer títulos que comienzan con * o **
            raw_titles = [
                line.strip('* ').strip('**').strip() 
                for line in titles_section.split('\n')
                if line.strip().startswith('*') and len(line.strip()) > 10
            ]
            
            # Filtrar títulos vacíos y duplicados
            optimized_titles = [
                title for title in raw_titles 
                if title and not title.startswith('**') and len(title) >= 20
            ]
            
            return optimized_titles[:10]
            
        return []
        
    except Exception as e:
        print(f"Error al extraer títulos: {e}")
        return []

def limpiar_nombre_archivo(nombre):
    """Limpia el nombre del archivo para eliminar caracteres inválidos."""
    return "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in nombre).strip()

def subir_a_hubspot(topic, html_content):
    """Sube el contenido generado como página de sitio en HubSpot."""
    data = {
        "name": f"{topic}",
        "slug": topic.lower().replace(" ", "-"),
        "templatePath": "@hubspot/growth/templates/pricing.html",
        "state": "DRAFT",
        "layoutSections": {
            "main": {
                "type": "section",
                "contents": [
                    {
                        "moduleType": "rich_text",
                        "content": html_content
                    }
                ]
            }
        }
    }

    response = requests.post(HUBSPOT_API_URL, headers=headers, json=data)
    if response.status_code == 201:
        st.success("Página creada en HubSpot exitosamente.")
        page_id = response.json().get("id")
        st.write(f"ID de la página creada: {page_id}")
    else:
        st.error(f"Error al crear la página en HubSpot: {response.status_code} - {response.text}")
def subir_a_hubspot_article(title, html_content):
    """Sube el contenido generado como publicación de blog en HubSpot."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Encontrar el H1 y usar su texto como título
    h1_tag = soup.find('h1')
    if h1_tag:
        article_title = h1_tag.get_text().strip()
        # Eliminar el H1 después de obtener su texto
        h1_tag.decompose()
    else:
        article_title = title
        
    clean_title = limpiar_nombre_archivo(article_title)
    
    body = {
        "name": article_title,
        "slug": clean_title.lower().replace(" ", "-"),
        "contentGroupId": 166239720295,
        "htmlTitle": article_title,
        "postBody": str(soup),
        "metaDescription": f"Artículo sobre {article_title}",
        "authorId": 167640064039,
        "state": "DRAFT",
        "tagIds": [1, 2]
    }

    response = requests.post(HUBSPOT_BLOG_URL, headers=headers, json=body)
    if response.status_code == 201:
        st.success(f"Artículo '{article_title}' creado en HubSpot exitosamente.")
    else:
        st.error(f"Error al crear el artículo '{article_title}' en HubSpot: {response.status_code} - {response.text}")
def generar_articulo_completo(topic, keyword=""):
    """Genera un artículo completo y lo sube a HubSpot."""
    try:
        search_topic = f"{topic} {keyword}".strip()
        informe = generar_informe_articulo(search_topic)
        
        outline = procesar_outline(search_topic, informe)
        draft = procesar_draft(search_topic, outline)
        contenido_enriquecido = procesar_enriquecimiento(search_topic, draft)
        contenido_ajustado = procesar_tono(search_topic, contenido_enriquecido)
        contenido_final = procesar_formato_final(search_topic, contenido_ajustado)
        
        article_title = f"{topic} - {keyword}" if keyword else topic
        subir_a_hubspot_article(article_title, contenido_final)
        
        return True
    except Exception as e:
        st.error(f"Error generando el artículo para {topic}: {e}")
        return False

def generar_varios_articulos(agent_name, keyword, num_articulos):
    """Genera múltiples artículos basados en un tema principal y keyword."""
    try:
        search_topic = f"{agent_name} {keyword}".strip()
        informe = generar_informe_articulo(search_topic)
        
        titulos_sugeridos = extraer_titulos_sugeridos(informe, keyword)
        
        if not titulos_sugeridos:
            st.error("No se encontraron subtemas en el informe.")
            return
        
        st.write(f"Se encontraron {len(titulos_sugeridos)} títulos sugeridos. Se generarán {min(num_articulos, len(titulos_sugeridos))} artículos.")
        
        # Mostrar los títulos que se van a generar
        st.write("Títulos a generar:")
        for i, titulo in enumerate(titulos_sugeridos[:num_articulos], 1):
            st.write(f"{i}. {titulo}")
            
        # Generar los artículos
        for i, titulo in enumerate(titulos_sugeridos[:num_articulos], 1):
            st.write(f"Generando artículo {i}/{num_articulos}: {titulo}")
            
            if generar_articulo_completo(titulo, keyword):
                st.success(f"Artículo {i} generado y subido exitosamente: {titulo}")
            else:
                st.error(f"Error al generar el artículo {i}: {titulo}")
                
    except Exception as e:
        st.error(f"Error en la generación múltiple de artículos: {e}")

def generar_landing(agent):
    """Genera una landing page y la sube a HubSpot."""
    try:
        topic = agent.get("name", "Nombre no disponible")
        redirect_url = agent.get('url', 'URL no disponible')
        
        informe = generar_informe_completo(topic)
        
        titular = generar_titular(topic, informe)
        subtitulo = generar_subtitulo(topic, informe)
        cta = generar_cta(topic, informe)
        titulo_producto = generar_titulo_producto(topic, informe)
        texto_introductorio = generar_texto_introductorio(topic, informe)
        como_funciona = generar_como_funciona(topic)
        cta_final = generar_cta_final(topic, redirect_url)
        faqs = generar_faqs(topic, informe)
        seccion_hero = generar_seccion_hero(topic, redirect_url, titular, subtitulo, cta)
        seccion_why = generar_seccion_why(topic, titulo_producto, texto_introductorio, cta)

        contenido_completo = f"""
        <html>
        <body>
            <section id="hero">{seccion_hero}</section>
            <section id="why">{seccion_why}</section>
            <section id="como-funciona">{como_funciona}</section>
            <section id="cta-final">{cta_final}</section>
            <section id="faqs">{faqs}</section>
        </body>
        </html>
        """

        soup = BeautifulSoup(contenido_completo, 'html.parser')
        html_bien_formateado = soup.prettify()

        file_name = f"{limpiar_nombre_archivo(topic)}.html"
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(html_bien_formateado)
        st.success(f"Archivo HTML guardado como {file_name}")

        subir_a_hubspot(topic, html_bien_formateado)

    except Exception as e:
        st.error(f"Error generando la landing para {topic}: {e}")

# Interfaz principal
url = "https://api.codegpt.co/api/v1/agents/marketplace/all"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
# En la parte donde se procesan los agentes:
for agent in data:
    agent_name = agent.get("name", "Nombre no disponible")
    agent_url = agent.get("url", "URL no disponible")
    image_url = agent.get("image")

    col1, col2, col3 = st.columns([1, 8, 3])
    with col1:
        if image_url:
            st.image(image_url, width=30)
    with col2:
        st.markdown(f"**{agent_name}**")
        st.write(f"[Ir a {agent_name}]({agent_url})")
    with col3:
        if st.button(f"Generar Landing para {agent_name}", key=f"landing_{agent_name}"):
            generar_landing(agent)
    
    col4, col5, col6 = st.columns([2, 2, 3])
    with col4:
        num_articulos = st.number_input(
            "Número de artículos",
            min_value=1,
            max_value=10,
            value=1,
            key=f"num_{agent_name}"
        )
    with col5:
        keyword = st.text_input(
            "Palabra clave",
            value="",
            key=f"keyword_{agent_name}",
            placeholder="Ej: AI, Cloud, etc."
        )
    with col6:
        if st.button(f"Generar {num_articulos} artículos", key=f"articles_{agent_name}"):
            if keyword:
                generar_varios_articulos(agent_name, keyword, num_articulos)  # Aquí está el cambio
            else:
                st.warning("Por favor, ingrese una palabra clave")
    
    st.divider()
else:
    st.error("No se pudo obtener la lista de agentes.")



