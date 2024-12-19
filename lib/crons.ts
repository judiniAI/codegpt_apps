import { runChangelog } from '../Changelog/changelog.ts'

Deno.cron('Run at 23:00 UTC on monday every monday', '0 23 * * 1', async () => {
  const agentId = Deno.env.get('STUDIO_AGENT_ID')
  const channelId = Deno.env.get('VSCODE_DISCORD_CHANNEL_ID')
  const platformName = Deno.env.get('VSCODE_PLATFORM_NAME')

  if (!agentId) {
    console.log('Missing STUDIO_AGENT_ID environment variable')
    return
  }

  if (!channelId) {
    console.log('Missing VSCODE_DISCORD_CHANNEL_ID environment variable')
    return
  }

  if (!platformName) {
    console.log('Missing VSCODE_PLATFORM_NAME environment variable')
    return
  }

  await runChangelog({
    agentId,
    channelId,
    platformName
  })
})

Deno.cron('Run at 23:00 UTC on day-of-month 1 every month', '0 23 1 * *', async () => {
  const agentId = Deno.env.get('STUDIO_AGENT_ID')
  const channelId = Deno.env.get('STUDIO_DISCORD_CHANNEL_ID')
  const platformName = Deno.env.get('STUDIO_PLATFORM_NAME')

  if (!agentId) {
    console.log('Missing STUDIO_AGENT_ID environment variable')
    return
  }

  if (!channelId) {
    console.log('Missing STUDIO_DISCORD_CHANNEL_ID environment variable')
    return
  }

  if (!platformName) {
    console.log('Missing STUDIO_PLATFORM_NAME environment variable')
    return
  }

  await runChangelog({
    agentId,
    channelId,
    platformName
  })
})
