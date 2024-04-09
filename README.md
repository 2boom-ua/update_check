# update_check
update informer for Dietpi (Telegram, Discord, Gotify, Ntfy, Pushbullet) as linux service

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
		"WEB": "server_url"
	},
	"NTFY": {
		"ON": true,
		"SUB": "your_subscribe",
		"WEB": "server_url"
	},
	"PUSHBULLET": {
		"ON": false,
		"API": "your_api_key"
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
