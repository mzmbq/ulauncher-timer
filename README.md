# ulauncher-timer

A simple timer extension for Ulauncher.

## Features

- Set timers with natural language (e.g., `10m`, `1h30m`, `2h15m30s`)
- Add custom messages to timers
- List and cancel active timers
- Send HTTP notifications on timer completion (Discord, Telegram, etc.)

## Usage

### Examples

- `ti 10m` - Set a 10-minute timer
- `ti 2h15m30s` - Set a 2 hour, 15 minute, 30 second timer
- `ti 10m: Check the oven` - Set a 10-minute timer with a custom message
- `ti` - View active timers

## Settings

### Notification URL Format

#### GET Request

```
GET <url>
```

#### POST Request:

```
POST <url> || <body>
```

- You can configure multiple webhooks.
- Lines starting with `#` are ignored.
- `{message}` is replaced with the value from the timer

### Example: Discord Notifications

1. Go to Server Settings → Integrations → Webhooks in Discord
2. Create or copy an existing webhook URL
3. Replace `<WEBHOOK_ID>` and `<TOKEN>` with your values:

```
POST https://discord.com/api/webhooks/<WEBHOOK_ID>/<TOKEN> || {"content": {message}}
```

### Example: Telegram Notifications

1. Create a bot using [@BotFather](https://t.me/botfather)
2. Get your [chat ID](https://gist.github.com/nafiesl/4ad622f344cd1dc3bb1ecbe468ff9f8a)
3. Replace `<TOKEN>` and `<CHAT_ID>` with your values:

```
GET https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<CHAT_ID>&text={message}
```

## Requirements

- Ulauncher 6+
- Python 3.10+
- Python libraries
  - `requests`
