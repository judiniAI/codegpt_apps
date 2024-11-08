import os
import requests
import streamlit as st
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
from bs4 import BeautifulSoup  # Para validar y estructurar el HTML

# Título de la aplicación
st.title("Lista de Agentes en Marketplace")

# URL del endpoint para obtener la lista de agentes
url = "https://api.codegpt.co/api/v1/agents/marketplace/all"

def generar_landing(agent):
    try:
        topic = agent.get("name", "Nombre no disponible")
        redirect_url = agent.get('url', 'URL no disponible')
        image_url = agent.get('image', 'URL de imagen no disponible')  # Obtener la URL de la imagen del agente
        
        informe = generar_informe_completo(topic)

        # Generar componentes con los agentes 1 a 5
        titular = generar_titular(topic, informe)
        subtitulo = generar_subtitulo(topic, informe)
        cta = generar_cta(topic, informe)
        titulo_producto = generar_titulo_producto(topic, informe)
        texto_introductorio = generar_texto_introductorio(topic, informe)

        # Generar secciones con los agentes 6 a 10
        como_funciona = generar_como_funciona(topic)
        cta_final = generar_cta_final(topic, redirect_url)
        faqs = generar_faqs(topic, informe)
        seccion_hero = generar_seccion_hero(topic, redirect_url, titular, subtitulo, cta)
        seccion_why = generar_seccion_why(topic, titulo_producto, texto_introductorio, cta, image_url)  # Pasar la URL de la imagen

        # Ensamblar el contenido completo de forma segmentada
        contenido_completo = f"""
        <html>
        <body>
            <!-- Sección Hero -->
            <section id="hero">
                {seccion_hero}
            </section>

            <!-- Sección Why -->
            <section id="why">
                {seccion_why}
            </section>

            <!-- Sección Cómo Funciona -->
            <section id="como-funciona">
                {como_funciona}
            </section>

            <!-- Sección de CTA Final -->
            <section id="cta-final">
                {cta_final}
            </section>

            <!-- Sección de FAQs -->
            <section id="faqs">
                {faqs}
            </section>
        </body>
        </html>
        """

        # Validar la estructura del HTML con BeautifulSoup
        soup = BeautifulSoup(contenido_completo, 'html.parser')
        html_bien_formateado = soup.prettify()

        # Guardar el contenido en un archivo HTML
        file_name = f"{topic.replace(' ', '_')}.html"
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(html_bien_formateado)

        st.success(f"Landing generada y guardada como {file_name}")

    except Exception as e:
        st.error(f"Error generando la landing para {topic}: {e}")

# Realizar la solicitud GET al endpoint
response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Obtener los datos JSON de la respuesta
    data = response.json()

    # Mostrar los datos en Streamlit
    for agent in data:
        agent_name = agent.get("name", "Nombre no disponible")
        agent_url = agent.get('url', 'URL no disponible')
        image_url = agent.get('image')  # Obtener la URL de la imagen

        # Mostrar el logo pequeño y el nombre del agente en una fila
        col1, col2 = st.columns([1, 10])  # Definir columnas, la primera pequeña para la imagen
        with col1:
            if image_url:
                # Mostrar la imagen como un icono pequeño (tamaño ajustado)
                st.image(image_url, width=30)  # Ajustar el tamaño del icono
        with col2:
            # Mostrar el nombre del agente y su URL
            st.markdown(f"**{agent_name}**")
            st.write(f"[Ir a {agent_name}]({agent_url})")

        # Botón para generar la landing
        if st.button(f"Generar Landing para {agent_name}"):
            generar_landing(agent)

else:
    st.error("No se pudo obtener la lista de agentes.")