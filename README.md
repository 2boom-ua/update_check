# update_check
update notifier for Dietpi (Telegram, Discord, Gotify)

*** [Gotify - a simple server for sending and receiving messages (in real time per WebSocket). ](https://github.com/gotify/server)

**config.json**
```
{
	"TELEGRAM": {
		"ON": true,
		"TOKEN": "your_token",
		"CHAT_ID": "your_chat_id"
	},
	"DISCORD": {
		"ON": true,
		"WEB": "web_your_channel"
	},
	"GOTIFY": {
		"ON": true,
		"TOKEN": "your_token",
		"WEB": "server_url/message"
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
