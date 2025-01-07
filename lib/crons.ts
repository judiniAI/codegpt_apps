import 'jsr:@std/dotenv/load'
import { runChangelog } from '../Changelog/changelog.ts'

// Run at 23:00 UTC on monday every monday
Deno.cron('vscode_weekly_changelog', '0 23 * * 2', async () => {
  const agentId = Deno.env.get('VSCODE_AGENT_ID')
  const channelId = Deno.env.get('VSCODE_DISCORD_CHANNEL_ID')
  const platformName = Deno.env.get('VSCODE_PLATFORM_NAME')
  const groupId = Deno.env.get('VSCODE_GROUP_ID')

  if (!agentId) {
    console.log('Missing VSCODE_AGENT_ID environment variable')
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

  if (!groupId) {
    console.log('Missing VSCODE_GROUP_ID environment variable')
    return
  }

  await runChangelog({
    agentId,
    channelId,
    platformName,
    days: 8,
    groupId
  })
})

// Run at 23:00 UTC on day-of-month 1 every month
Deno.cron('studio_monthly_changelog', '0 23 1 * *', async () => {
  const agentId = Deno.env.get('STUDIO_AGENT_ID')
  const channelId = Deno.env.get('STUDIO_DISCORD_CHANNEL_ID')
  const platformName = Deno.env.get('STUDIO_PLATFORM_NAME')
  const groupId = Deno.env.get('STUDIO_GROUP_ID')

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

  if (!groupId) {
    console.log('Missin STUDIO_GROUP_ID environment variable')
    return
  }

  await runChangelog({
    agentId,
    channelId,
    platformName,
    days: 30,
    groupId
  })
})
