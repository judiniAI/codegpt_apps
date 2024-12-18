require("dotenv").config();
const axios = require("axios");
const { DateTime } = require("luxon");

// Obtener variables de entorno
const api_key_codegpt = process.env.API_KEY_CODEGPT;
const org_id = process.env.ORG_ID;
const agent_id = process.env.AGENT_ID;
const hubspot_api_key = process.env.HUBSPOT_API_KEY;
const group_id = process.env.GROUP_ID;
const name_platform = process.env.NAME_PLATFORM;
const discord_token = process.env.DISCORD_TOKEN;
const discord_channel_id = process.env.DISCORD_CHANNEL_ID;

const fecha = DateTime.local().toFormat("dd/MM/yyyy");

async function obtener_mensajes_de_discord(token, canal_id, fecha) {
  const url = `https://discord.com/api/v9/channels/${canal_id}/messages`;
  const headers = {
    Authorization: `Bot ${token}`,
    "Content-Type": "application/json",
  };

  const fecha_fin = DateTime.fromFormat(fecha, "dd/MM/yyyy");
  const fecha_inicio = fecha_fin.minus({ days: 30 });
  const timestamp_inicio = Math.floor(fecha_inicio.toSeconds());
  const timestamp_fin = Math.floor(fecha_fin.toSeconds());

  const params = {
    after: timestamp_inicio,
    before: timestamp_fin,
    limit: 100,
  };

  try {
    const response = await axios.get(url, { headers, params });
    return response.data;
  } catch (error) {
    throw new Error(
      `Error al obtener mensajes de Discord: ${error.response.status} - ${error.response.statusText}`
    );
  }
}

async function chat_with_agent(agent_id, user_message, api_key, org_id) {
  const url = "https://api.codegpt.co/api/v1/chat/completions";
  const headers = {
    Authorization: `Bearer ${api_key}`,
    "CodeGPT-Org-Id": org_id,
  };
  const data = {
    agentId: agent_id,
    messages: [
      {
        role: "user",
        content: user_message,
      },
    ],
    format: "text",
    stream: false,
  };

  try {
    const response = await axios.post(url, data, { headers });
    return response.data;
  } catch (error) {
    throw new Error(
      `Error: ${error.response.status} - ${error.response.statusText}`
    );
  }
}

async function subir_a_hubspot(
  topic,
  html_content,
  hubspot_api_key,
  group_id,
  name_platform
) {
  const headers = {
    Authorization: hubspot_api_key,
    "Content-Type": "application/json",
  };
  const data = {
    name: `${topic} ${name_platform}`,
    slug: "/version",
    state: "DRAFT",
    contentGroupId: group_id,
    htmlTitle: topic,
    postBody: html_content,
    blogAuthorId: 169677582703,
    language: "en",
    blogAuthor: {
      id: 169677582703,
      language: "en",
    },
    primaryLanguage: "en",
    metaDescription: `Content about ${topic}`,
    useFeaturedImage: false,
    enableFeaturedImage: false,
    languageSettings: {
      language: "en",
      primaryLanguage: "en",
      enableLanguageFallback: true,
    },
  };

  try {
    const response = await axios.post(
      "https://api.hubapi.com/cms/v3/blogs/posts",
      data,
      { headers }
    );
    if ([200, 201].includes(response.status)) {
      console.log("Página de sitio subida exitosamente en HubSpot.");
    } else {
      console.log(
        `Error al subir la página de sitio en HubSpot: ${response.status} - ${response.statusText}`
      );
    }
    return response.status;
  } catch (error) {
    console.log(
      `Error al subir la página de sitio en HubSpot: ${error.response.status} - ${error.response.statusText}`
    );
    return error.response.status;
  }
}

(async () => {
  try {
    // Obtener mensajes de Discord
    const mensajes = await obtener_mensajes_de_discord(
      discord_token,
      discord_channel_id,
      fecha
    );
    if (mensajes.length > 0) {
      // Formatear los mensajes para el agente
      const user_message = mensajes
        .map((msg) => `${msg.author.username}: ${msg.content}`)
        .join("\n");

      // Enviar los mensajes al agente
      const response1 = await chat_with_agent(
        agent_id,
        user_message,
        api_key_codegpt,
        org_id
      );
      console.log("Respuesta del agente:", response1);

      // Extraer el contenido de la respuesta del agente
      const agent_response_content = response1;
      if (agent_response_content) {
        const topic = "Changelog";
        await subir_a_hubspot(
          topic,
          agent_response_content,
          hubspot_api_key,
          group_id,
          name_platform
        );
      } else {
        console.log(
          "No se pudo obtener el contenido de la respuesta del agente."
        );
      }
    } else {
      console.log("No se encontraron mensajes en la fecha especificada.");
    }
  } catch (error) {
    console.error(error);
  }
})();
