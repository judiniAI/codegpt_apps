# Changelog Script

This project is a JavaScript implementation of a script that fetches messages from a Discord channel, processes them with an agent, and uploads the processed content to HubSpot as a blog post.

## Prerequisites

- Node.js installed on your machine
- A Discord bot token
- HubSpot API key
- CodeGPT API key

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/changelog-script.git
cd changelog-script

2. Install the required dependencies:
```bash
npm install axios dotenv luxon

3. Create a .env file in the root directory of the project and add the following environment variables:

```bash
API_KEY_CODEGPT=your_codegpt_api_key
ORG_ID=your_org_id
AGENT_ID=your_agent_id
HUBSPOT_API_KEY=your_hubspot_api_key
GROUP_ID=your_group_id
NAME_PLATFORM=your_platform_name
DISCORD_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_discord_channel_id

## Usage
To run the script, use the following command:

```bash
node changelog.js

## Functions
### obtener_mensajes_de_discord

Fetches messages from a specified Discord channel within a date range.

### Parameters:

- `token` (string): Discord bot token.
- `canal_id` (string): Discord channel ID.
- `fecha` (string): Date in the format "dd/MM/yyyy".
### Returns:

`Array:` List of messages from the Discord channel.

### chat_with_agent
Sends a message to an agent and retrieves the response.

### Parameters:

- `agent_id` (string): Agent ID.
- `user_message` (string): User message.
- `api_key` (string): API key for authentication.
- `org_id` (string): Organization ID.

### Returns:

Object: Response from the agent.

### subir_a_hubspot
Uploads the generated content as a blog post to HubSpot.

### Parameters:

- `topic` (string): Title of the content.
- `html_content` (string): HTML content to upload.
- `hubspot_api_key` (string): HubSpot API key.
- `group_id` (string): Content group ID.
- `name_platform` (string): Platform name.

### Returns:

`number`: Status code of the API response.
## Error Handling
The script includes error handling for API requests. If an error occurs, it will be logged to the console.

## License
This project is licensed under the MIT License. See the LICENSE file for details.