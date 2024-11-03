#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Copyright (c) 2024 2boom.

import json
import os
import time
import requests
from schedule import every, repeat, run_pending


def GetString(filename: str) -> str:
	"""Return the content of the file as a string"""
	if os.path.exists(filename):
		with open(filename, 'r') as file:
			return file.read().strip('\n')
	return ""


def getHostName() -> str:
	"""Get the hostname."""
	hostname = ""
	hostname_path = '/proc/sys/kernel/hostname'
	if os.path.exists(hostname_path):
		with open(hostname_path, "r") as file:
			hostname = file.read().strip()
	return hostname

def SendMessage(message: str):
	"""Send notifications to various messaging services (Telegram, Discord, Gotify, Ntfy, Pushbullet, Pushover, Matrix, Zulip, Flock, Slack, RocketChat, Pumble, Mattermost, CUSTOM)."""
	"""CUSTOM - single_asterisks - Zulip, Flock, Slack, RocketChat, Flock, double_asterisks - Pumble, Mattermost """
	def SendRequest(url, json_data=None, data=None, headers=None):
		"""Send an HTTP POST request and handle exceptions."""
		try:
			response = requests.post(url, json=json_data, data=data, headers=headers)
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending message: {e}")
			
	def toHTMLFormat(message: str) -> str:
		"""Format the message with bold text and HTML line breaks."""
		formatted_message = ""
		for i, string in enumerate(message.split('*')):
			formatted_message += f"<b>{string}</b>" if i % 2 else string
		formatted_message = formatted_message.replace("\n", "<br>")
		return formatted_message
		
	def toMarkdownFormat(message: str, m_format: str) -> str:
		"""Converts a message into a specified format (either Markdown, HTML, or plain text"""
		formatted_message = ""
		formatters = {
			"markdown": lambda msg: msg.replace("*", "**"),
			"html": toHTMLFormat,
			"text": lambda msg: msg.replace("*", ""),
			}
		formatted_message = formatters.get(m_format, lambda msg: msg)(message)
		return formatted_message

	if telegram_on:
		for token, chat_id in zip(telegram_tokens, telegram_chat_ids):
			url = f"https://api.telegram.org/bot{token}/sendMessage"
			json_data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
			SendRequest(url, json_data)
	if slack_on:
		for url in slack_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if rocket_on:
		for url in rocket_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if zulip_on:
		for url in zulip_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if flock_on:
		for url in flock_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if matrix_on:
		for token, server_url, room_id in zip(matrix_tokens, matrix_server_urls, matrix_room_ids):
			url = f"{server_url}/_matrix/client/r0/rooms/{room_id}/send/m.room.message?access_token={token}"
			formatted_message = toHTMLFormat(message)
			json_data = {"msgtype": "m.text", "body": formatted_message, "format": "org.matrix.custom.html", "formatted_body": formatted_message}
			SendRequest(url, json_data)
	if discord_on:
		for url in discord_webhook_urls:
			formatted_message = message.replace("*", "**")
			json_data = {"content": formatted_message}
			SendRequest(url, json_data)
	if mattermost_on:
		for url in mattermost_webhook_urls:
			formatted_message = message.replace("*", "**")
			json_data = {"text": formatted_message}
			SendRequest(url, json_data)
	if pumble_on:
		for url in pumble_webhook_urls:
			formatted_message = message.replace("*", "**")
			json_data = {"text": formatted_message}
			SendRequest(url, json_data)
	if apprise_on:
		for url, format_message in zip(apprise_webhook_urls, apprise_format_messages):
			"""apprise_formats - markdown/html/text."""
			formatted_message = toMarkdownFormat(message, format_message)
			json_data = {"body": formatted_message, "type": "info", "format": format_message}
			SendRequest(url, json_data)
	if custom_on:
		"""custom_name - text/body/formatted_body/content/message/..., custom_format - markdown/html/text/asterisk(non standard markdown - default)."""
		message_str_format = ["text", "content", "message", "body", "formatted_body", "data"]
		for url, header, pyload, format_message in zip(custom_webhook_urls, custom_headers, custom_pyloads, custom_format_messages):
			data, ntfy = None, False
			formated_message = toMarkdownFormat(message, format_message)
			header_json = header if header else None
			for key in list(pyload.keys()):
				if key == "title":
					header, formated_message = formated_message.split("\n", 1)
					pyload[key] = header.replace("*", "")
					if pyload[key] == "extras":
						formated_message = formated_message.replace("\n", "\n\n")
				pyload[key] = formated_message if key in message_str_format else pyload[key]
				if key == "data": ntfy = True
			pyload_json = None if ntfy else pyload
			data = formated_message.encode("utf-8") if ntfy else None
			SendRequest(url, pyload_json, data, header_json)
	if ntfy_on:
		for url in ntfy_webhook_urls:
			headers_data = {"Content-Type": "application/json", "Markdown": "yes"}
			formatted_message = message.replace("*", "**").encode(encoding = "utf-8")
			SendRequest(url, None, formatted_message, headers_data)
	
	header, message = message.split("\n", 1)

	if gotify_on:
		for token, server_url in zip(gotify_tokens, gotify_server_urls):
			url = f"{server_url}/message?token={token}"
			formatted_message = message.replace("*", "**").replace("\n", "\n\n")
			formatted_header = header.replace("*", "")
			json_data = {"title": formatted_header, "message": formatted_message, "priority": 0, "extras": {"client::display": {"contentType": "text/markdown"}}}
			SendRequest(url, json_data)
	if pushover_on:
		for token, user_key in zip(pushover_tokens, pushover_user_keys):
			url = "https://api.pushover.net/1/messages.json"
			formatted_message = toHTMLFormat(message)
			formatted_header = header.replace("*", "")
			json_data = {"token": token, "user": user_key, "title": formatted_header, "message": formatted_message, "html": "1"}
			SendRequest(url, json_data)
	if pushbullet_on:
		for token in pushbullet_tokens:
			url = "https://api.pushbullet.com/v2/pushes"
			formatted_header = header.replace("*", "")
			formatted_message = message.replace("*", "")
			json_data = {"type": "note", "title": formatted_header, "body": formatted_message}
			headers_data = {"Access-Token": token, "Content-Type": "application/json"}
			SendRequest(url, json_data, None, headers_data)


if __name__ == "__main__":
	"""Load configuration and initialize monitoring"""
	update_status_files = [
		['/run/dietpi/.apt_updates', 'apt update(s) available'],
		['/run/dietpi/.update_available', 'upgrade available'],
		['/run/dietpi/.live_patches', 'live patch(es) available']
	]
	hostname = getHostName()
	header = f"*{hostname}* (updates)\n"
	current_path =  os.path.dirname(os.path.realpath(__file__))
	dots = {"orange": "\U0001F7E0", "green": "\U0001F7E2"}
	square_dots = {"orange": "\U0001F7E7", "green": "\U0001F7E9"}
	monitoring_mg = old_status = ""
	if os.path.exists(f"{current_path}/config.json"):
		with open(f"{current_path}/config.json", "r") as file:
			config_json = json.loads(file.read())
		default_dot_style = config_json["DEFAULT_DOT_STYLE"]
		if not default_dot_style:
			dots = square_dots
		orange_dot, green_dot = dots["orange"], dots["green"]
		messaging_platforms = ["TELEGRAM", "DISCORD", "GOTIFY", "NTFY", "PUSHBULLET", "PUSHOVER", "SLACK", "MATRIX", "MATTERMOST", "PUMBLE", "ROCKET", "ZULIP", "FLOCK", "APPRISE", "CUSTOM"]
		telegram_on, discord_on, gotify_on, ntfy_on, pushbullet_on, pushover_on, slack_on, matrix_on, mattermost_on, pumble_on, rocket_on, zulip_on, flock_on, apprise_on, custom_on = (config_json[key]["ENABLED"] for key in messaging_platforms)
		services = {
			"TELEGRAM": ["TOKENS", "CHAT_IDS"],
			"DISCORD": ["WEBHOOK_URLS"],
			"SLACK": ["WEBHOOK_URLS"],
			"GOTIFY": ["TOKENS", "SERVER_URLS"],
			"NTFY": ["WEBHOOK_URLS"],
			"PUSHBULLET": ["TOKENS"],
			"PUSHOVER": ["TOKENS", "USER_KEYS"],
			"MATRIX": ["TOKENS", "SERVER_URLS", "ROOM_IDS"],
			"MATTERMOST": ["WEBHOOK_URLS"],
			"PUMBLE": ["WEBHOOK_URLS"],
			"ROCKET": ["WEBHOOK_URLS"],
			"ZULIP": ["WEBHOOK_URLS"],
			"FLOCK": ["WEBHOOK_URLS"],
			"APPRISE": ["WEBHOOK_URLS", "FORMAT_MESSAGES"],
			"CUSTOM": ["WEBHOOK_URLS", "HEADERS", "PYLOADS", "FORMAT_MESSAGES"]
		}
		for service, keys in services.items():
			if config_json[service]["ENABLED"]:
				globals().update({f"{service.lower()}_{key.lower()}": config_json[service][key] for key in keys})
				monitoring_mg += f"- messaging: {service.capitalize()},\n"
		min_repeat = max(int(config_json.get("MIN_REPEAT", 1)), 1)
		monitoring_mg += (
			f"- default dot style: {default_dot_style}.\n"
			f"- polling period: {min_repeat} minute(s)."
		)
		SendMessage(f"{header}hosts monitor:\n{monitoring_mg}")
	else:
		print("config.json not found")


@repeat(every(min_repeat).minutes)
def UpdateCheck():
	"""Periodically check for updates, upgrade and patch aviable"""
	new_status = message =""
	current_status = []
	global old_status
	if not old_status: old_status += "0" * len(update_status_files)
	current_status = list(old_status)
	for i, (file_path, description) in enumerate(update_status_files):
		if os.path.exists(file_path):
			if old_status[i] == "0":
				message += f"{orange_dot} {GetString(file_path)} {description}\n"
			current_status[i] = "1"
		else:
			if old_status[i] == "1":
				message += f"{green_dot} no {description}\n"
			current_status[i] = "0"
	new_status = "".join(current_status)
	if old_status != new_status:
		old_status = new_status
		SendMessage(f"{header}{message}")

while True:
	run_pending()
	time.sleep(1)