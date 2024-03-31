# update_check
update notifier for Dietpi (Telegram, Discord)

**config.json**
```{
	"TELEGRAM": {
		"ON": true,
		"TOKEN": "6516846080:AAExanW-S6amGEummCMH-h1Vo6FlbzUUy7M",
		"CHAT_ID": "677895454"
	},
	"DISCORD": {
		"ON": true,
		"WEB": "https://discord.com/api/webhooks/1223926610374426725/tRlqITXcBhRaRbvdPKLQWCIgfkllNZE4WninyLnEuoqeLMrC4iPrQ2jBASfJKBNyW67Q"
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
