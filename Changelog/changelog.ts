// deno-lint-ignore-file no-explicit-any
const codegptApiKey = Deno.env.get('API_KEY_CODEGPT')
const orgId = Deno.env.get('ORG_ID')
const hubspotApiKey = Deno.env.get('HUBSPOT_API_KEY')
const discordToken = Deno.env.get('DISCORD_TOKEN')
const contentGroupId = Deno.env.get('HUBSPOT_GROUP_ID')

export async function runChangelog({
  channelId,
  agentId,
  platformName
}: {
  channelId: string
  agentId: string
  platformName: string
}) {
  try {
    const messages = await getDiscordMessages({
      channelId
    })

    if (!messages || !Array.isArray(messages) || messages?.length === 0) {
      console.log(`No Discord messages found for today in channel ${channelId}`)
      return
    }

    const userMessage = messages
      .map((message: any) => `${message.author.username}: ${message.content}`)
      .join('\n')

    const content = await chatWithAgent({ userMessage, agentId })

    if (!content) {
      console.log('Error chatting with agent')
      return
    }

    const topic = 'Changelog'
    await uploadToHubspot({
      content,
      platformName,
      topic
    })
  } catch (error) {
    console.log('Error running changelog:', error)
  }
}

async function getDiscordMessages({ channelId }: { channelId: string }) {
  if (!discordToken) {
    console.log('Missing DISCORD_TOKEN environment variable')
    return null
  }

  const today = new Date()
  const timestampEnd = Math.floor(today.getTime() / 1000)

  const startDate = new Date(today)
  startDate.setDate(today.getDate() - 30)

  const timestampStart = Math.floor(startDate.getTime() / 1000)

  const searchParams = new URLSearchParams({
    after: timestampStart.toString(),
    before: timestampEnd.toString(),
    limit: '100'
  })

  const url = `https://discord.com/api/v9/channels/${channelId}/messages?${searchParams.toString()}`

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        Authorization: `Bot ${discordToken}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      console.log(
        `Error al obtener mensajes de Discord: ${response.status} - ${response.statusText}`
      )

      return null
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.log(`Error al obtener mensajes de Discord: ${error}`)
    return null
  }
}

async function chatWithAgent({ agentId, userMessage }: { agentId: string; userMessage: string }) {
  if (!codegptApiKey || !orgId) {
    console.log('Missing required environment variables')
    return null
  }

  const url = 'https://api.codegpt.co/api/v1/chat/completions'

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${codegptApiKey}`,
        'CodeGPT-Org-Id': orgId
      },
      body: JSON.stringify({
        agentId,
        messages: [
          {
            role: 'user',
            content: userMessage
          }
        ],
        format: 'text',
        stream: false
      })
    })

    if (!response.ok) {
      console.log(`Error: ${response.status} - ${response.statusText}`)
      return null
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.log(`Error chatting with agent: ${error}`)
    return null
  }
}

async function uploadToHubspot({
  topic,
  content,
  platformName
}: {
  topic: string
  content: string
  platformName: string
}) {
  if (!hubspotApiKey) {
    console.log('Missing required environment variable HUBSPOT_API_KEY')
    return null
  }

  if (!contentGroupId) {
    console.log('Missing required environment variable HUBSPOT_GROUP_ID')
    return null
  }

  const data = {
    name: `${topic} ${platformName}`,
    slug: '/version',
    state: 'DRAFT',
    contentGroupId,
    htmlTitle: topic,
    postBody: content,
    blogAuthorId: 169677582703,
    language: 'en',
    blogAuthor: {
      id: 169677582703,
      language: 'en'
    },
    primaryLanguage: 'en',
    metaDescription: `Content about ${topic}`,
    useFeaturedImage: false,
    enableFeaturedImage: false,
    languageSettings: {
      language: 'en',
      primaryLanguage: 'en',
      enableLanguageFallback: true
    }
  }

  try {
    const response = await fetch('https://api.hubapi.com/cms/v3/blogs/posts', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${hubspotApiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (![200, 201].includes(response.status)) {
      console.log(`Error uploading to HubSpot: ${response.status} - ${response.statusText}`)
      return null
    }
    return response.status
  } catch (error) {
    console.log(`Error al subir la página de sitio en HubSpot: ${error}`)
    return null
  }
}
