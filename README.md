# update_check
update informer for Dietpi (Telegram, Discord, Gotify, Ntfy, Pushbullet, Slack) as linux service

![alt text](https://github.com/2boom-ua/update_check/blob/main/screen-tg.jpg?raw=true)

**crontab**
```
0 */1 * * * /boot/dietpi/dietpi-update 2
```

```
pip install -r requirements.txt
```

**config.json**
```
{
    "TELEGRAM": {
        "ON": true,
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
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ]
    },
    "SLACK": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
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
        "CHAT_WEB": [
            "first server_url",
            "second server_url",
            "...."
        ]
    },
    "NTFY": {
        "ON": true,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "CHAT_WEB": [
            "first server_url",
            "second server_url",
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
    "MIN_REPEAT": 1
}
```
**make as service**
```
nano /etc/systemd/system/update_check.service
```
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
