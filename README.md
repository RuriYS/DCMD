# DCMD

Discord Messages Dumper

## What is this?
It's a simple script to dump all your messages from Discord into a plain JSON.

## Data Preparation
1. Go to Privacy & Safety on your Discord's user settings.

    ![img](images/user-settings.png)

2. Scroll all the way down and find the blue "**Request Data**" button and click it.
  
    ![img](images/request-data.png)

3. Wait for a few days until you receive `package.zip` from Discord in your email (it takes a very long time, depending on how many messages you've sent, selecting more fields will take it even longer)

## Usage

1. Download this repository and extract it or run `git clone https://github.com/RuriYS/DCMD.git`
2. Download `package.zip` if you haven't already from the email Discord sent 
3. Copy `messages` folder into `DCMD`
4. Configure your filters in `config.json`:
```json
{
    "messages_path": "messages",
    "filters": {
        "links": false,      // Remove messages with URLs
        "emojis": false,     // Remove messages with emojis
        "commands": true,    // Remove messages starting with $, %, !, ., #
        "symbols": false,    // Remove messages containing special symbols
        "multilines": false, // Remove messages with multiple lines
        "duplicates": true,  // Remove duplicate messages
        "numbers": false     // Remove messages containing only numbers
    },
    "length": {
        "min": 1,           // Minimum word count
        "max": null         // Maximum word count (null for unlimited)
    },
    "limit": null,          // Maximum messages to dump (null for unlimited)
    "ignored_channels": ["1005103548939370508"],  // Channel IDs to ignore
    "ignored_guilds": ["A certain guild"],     // Guild names to ignore
    "ignore_dms": false     // Set to true to ignore all DMs
}
```
5. Run the script:
```bash
python main.py
```
6. Filtered messages will be saved to `dump.json` organized by channel ID:
```json
{
    "channel_id_1": [
        "message 1",
        "message 2"
    ],
    "channel_id_2": [
        "message 1",
        "message 2"
    ]
}
```

## Message Filtering

### Channel and Guild Filtering
- **Ignored Channels**: Specific channels can be ignored by adding their IDs to `ignored_channels`
- **Ignored Guilds**: Entire servers can be ignored by adding their names to `ignored_guilds`
- **DM Filtering**: Set `ignore_dms` to `true` to skip all direct messages

### Content Filtering
- **Links**: Remove messages containing URLs
- **Emojis**: Remove messages containing emoji
- **Commands**: Remove messages starting with command prefixes ($, %, !, ., #)
- **Symbols**: Remove messages containing special symbols (\n, **, <@, <#, `, ://)
- **Multilines**: Remove messages containing multiple lines
- **Numbers**: Remove messages containing only numbers
- **Duplicates**: Remove duplicate messages across all channels

### Length Filtering
- **Minimum Length**: Set minimum token count per message
- **Maximum Length**: Set maximum token count per message (null for no limit)
- **Message Limit**: Set maximum number of messages to dump (null for no limit)
