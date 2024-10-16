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
- **Dynamic Configuration:** Load settings from a JSON configuration file.
- **Polling Period:** Adjustable interval for checking updates.

![alt text](https://github.com/2boom-ua/update_check/blob/main/screenshot_tg.png?raw=true)

### Requirements
- Python 3.x
- Docker installed and running
- Dependencies: `requests`, `schedule`

### Edit crontab (crontab -e)
```
0 */1 * * * /boot/dietpi/dietpi-update 2
```
### Clone the repository:
```
git clone https://github.com/2boom-ua/update_check.git
cd dockcheck
```
### Install required Python packages:
```
pip install -r requirements.txt
```

### Edit config.json:
A **config.json** file in the same directory as the script, and include your API tokens and configuration settings.
```
{
    "TELEGRAM": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "CHAT_IDS": [
            "first chat_id",
            "second chat_id",
            "...."
        ]
    },
    "DISCORD": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
    "SLACK": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
    "GOTIFY": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "CHAT_URLS": [
            "first server_url",
            "second server_url",
            "...."
        ]
    },
    "NTFY": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "PUSHBULLET": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ]
    },
    "PUSHOVER": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "USER_KEYS": [
            "first user_key",
            "second user_key",
            "...."
        ]
    },
    "MATRIX": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "SERVER_URLS": [
            "first server_url",
            "second server_url",
            "...."
        ],
        "ROOM_IDS": [
            "!first room_id",
            "!second room_id",
            "...."
        ]
    },
    "MATTERMOST": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
    "ROCKET": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
		"USER_IDS": [
            "first user_id",
            "second user_id",
            "...."
        ],
        "SERVER_URLS": [
           "first server_url",
            "second server_url",
            "...."
        ],
		"CHANNEL_IDS": [
            "#first channel",
            "#second channel",
            "...."
        ]
    },
    "PUMBLE": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "ZULIP": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "CUSTOM": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
        "STD_BOLDS" : [
            true,
            false,
            "...."
                ]
    },
    "DEFAULT_DOT_STYLE": true,
    "MIN_REPEAT": 1
}
```
| Item   | Required   | Description   |
|------------|------------|------------|
| STD_BOLDS | true/false | "**" **standard Markdown**, "*" *non-standard Markdown* |
| | | Standard Markdown use - Pumble, Mattermost, Discord, Ntfy, Gotify |
| | | Non-standard Markdown use - Telegram, Zulip, Flock, Slack, RocketChat, Flock. |
| DEFAULT_DOT_STYLE | true/false | Round/Square dots. |
| SEC_REPEAT | 1 | Set the poll period in minutes. Minimum is 1 minute. | 

## Running as a Linux Service
You can set this script to run as a Linux service for continuous monitoring.

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

## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) for details.

## Author

- **2boom** - [GitHub](https://github.com/2boom-ua)
