## Update Monitoring Script
<div align="center">  
	<img src="https://github.com/2boom-ua/update_check/blob/main/update_check.jpg?raw=true" alt="" width="209" height="98">
</div>

### Overview

This Python script monitors the availability of system updates, upgrades, and live patches on a DietPi system. It periodically checks specific files and sends notifications through various messaging services when updates are available.

### Features

- **Update Monitoring:** Checks for available updates, upgrades, and live patches.
- **Real-time notifications with support for multiple accounts** via:
  - Telegram
  - Discord
  - Slack
  - Gotify
  - Ntfy
  - Pushbullet
  - Pushover
  - Rocket.chat
  - Matrix
  - Mattermost
  - Pumble
  - Flock
  - Zulip
  - Apprise
  - Webntfy
  - Custom webhook
- **Dynamic Configuration:** Load settings from a JSON configuration file.
- **Polling Period:** Adjustable interval for checking updates.

![alt text](https://github.com/2boom-ua/update_check/blob/main/screenshot_tg.png?raw=true)

### Requirements
- Python 3.x
- Docker installed and running
- Dependencies: `requests`, `schedule`

### Edit config.json:
You can use any name and any number of records for each messaging platform configuration, and you can also mix platforms as needed. The number of message platform configurations is unlimited.

[Configuration examples for Telegram, Matrix, Apprise, Pumble, Mattermost, Discord, Ntfy, Gotify, Zulip, Flock, Slack, Rocket.Chat, Pushover, Pushbullet](docs/json_message_config.md)
```
    "CUSTOM_NAME": {
        "ENABLED": false,
        "WEBHOOK_URL": [
            "first url",
            "second url",
            "...."
        ],
        "HEADER": [
            {first JSON structure},
            {second JSON structure},
            {....}
        ],
        "PYLOAD": [
            {first JSON structure},
            {second JSON structure},
            {....}
        ],
        "FORMAT_MESSAGE": [
            "markdown",
            "html",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Custom notifications |
| WEBHOOK_URL | url | The URL of your Custom webhook |
| HEADER | JSON structure | HTTP headers for each webhook request. This varies per service and may include fields like {"Content-Type": "application/json"}. |
| PAYLOAD | JSON structure | The JSON payload structure for each service, which usually includes message content and format. Like as  {"body": "message", "type": "info", "format": "markdown"}|
| FORMAT_MESSAGE | markdown,<br>html,<br>text,<br>simplified | Specifies the message format used by each service, such as markdown, html, or other text formatting.|

- **markdown** - a text-based format with lightweight syntax for basic styling (Pumble, Mattermost, Discord, Ntfy, Gotify),
- **simplified** - simplified standard Markdown (Telegram, Zulip, Flock, Slack, RocketChat).
- **html** - a web-based format using tags for advanced text styling,
- **text** - raw text without any styling or formatting.


```
 "STARTUP_MESSAGE": true,
 "DEFAULT_DOT_STYLE": true,
 "MIN_REPEAT": 1
```

| Item   | Required   | Description   |
|------------|------------|------------|
| STARTUP_MESSAGE | true/false | On/Off startup message. |
| DEFAULT_DOT_STYLE | true/false | Round/Square dots. |
| MIN_REPEAT | 1 | Set the poll period in minutes. Minimum is 1 minute. | 

### Edit crontab (crontab -e)
```
0 */1 * * * /boot/dietpi/dietpi-update 2
```
### Clone the repository:
```
git clone https://github.com/2boom-ua/update_check.git
cd dockcheck
```

## Docker
```bash
  docker build -t update_check .
```
or
```bash
  docker pull ghcr.io/2boom-ua/update_check:latest
```
### Dowload and edit config.json
```bash
curl -L -o ./config.json  https://raw.githubusercontent.com/2boom-ua/update_check/main/config.json
```
### docker-cli
```bash
  docker run -v ./config.json:/update_check/config.json -v /run/dietpi:/run/dietpi --name update_check -e TZ=UTC ghcr.io/2boom-ua/update_check:latest 
```
### docker-compose
```
version: "3.8"
services:
  update_check:
    container_name: update_check
    image: ghcr.io/2boom-ua/update_check:latest
    network_mode: host
    volumes:
      - ./config.json:/update_check/config.json
      - /run/dietpi:/run/dietpi
    environment:
      - TZ=UTC
    restart: always
```

```bash
docker-compose up -d
```
---
### Running as a Linux Service
You can set this script to run as a Linux service for continuous monitoring.

### Install required Python packages:
```
pip install -r requirements.txt
```
Create a systemd service file:
```
nano /etc/systemd/system/update_check.service
```
Add the following content:
```
[Unit]
Description=check update aviable
After=multi-user.target
[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /opt/update_check/update_check.py
[Install]
WantedBy=multi-user.target
```
```
systemctl daemon-reload
```
```
systemctl enable update_check.service
```
```
systemctl start update_check.service
```

### License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) for details.

### Author

- **2boom** - [GitHub](https://github.com/2boom-ua)
