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
	def SendRequest(url, json_data=None, data=None, headers=None):
		try:
			response = requests.post(url, json=json_data, data=data, headers=headers)
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending message: {e}")

	def toHTMLFormat(message: str) -> str:
		formatted_message = ""
		for i, string in enumerate(message.split('*')):
			formatted_message += f"<b>{string}</b>" if i % 2 else string
		formatted_message = formatted_message.replace("\n", "<br>")
		return formatted_message
		
	def toMarkdownFormat(message: str, m_format: str) -> str:
		formatted_message = ""
		formatters = {
			"markdown": lambda msg: msg.replace("*", "**"),
			"html": toHTMLFormat,
			"text": lambda msg: msg.replace("*", ""),
			}
		formatted_message = formatters.get(m_format, lambda msg: msg)(message)
		return formatted_message

	for url, header, pyload, format_message in zip(platform_webhook_url, platform_header, platform_pyload, platform_format_message):
		data, ntfy = None, False
		formated_message = toMarkdownFormat(message, format_message)
		header_json = header if header else None
		for key in list(pyload.keys()):
			if key == "title":
				delimiter = "<br>" if format_message == "html" else "\n"
				header, formated_message = formated_message.split(delimiter, 1)
				pyload[key] = header.replace("*", "")
			elif key == "extras":
				formated_message = formated_message.replace("\n", "\n\n")
				pyload["message"] = formated_message
			elif key == "data":
				ntfy = True
			pyload[key] = formated_message if key in ["text", "content", "message", "body", "formatted_body", "data"] else pyload[key]
		pyload_json = None if ntfy else pyload
		data = formated_message.encode("utf-8") if ntfy else None
		SendRequest(url, pyload_json, data, header_json)


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
	monitoring_message = old_status = ""
	if os.path.exists(f"{current_path}/config.json"):
		with open(f"{current_path}/config.json", "r") as file:
			config_json = json.loads(file.read())
		try:
			default_dot_style = config_json.get("DEFAULT_DOT_STYLE", True)
			min_repeat = max(int(config_json.get("MIN_REPEAT", 1)), 1)
		except (json.JSONDecodeError, ValueError, TypeError, KeyError):
			default_dot_style = True
			min_repeat = 1
		if not default_dot_style:
			dots = square_dots
		orange_dot, green_dot = dots["orange"], dots["green"]
		no_messaging_keys = ["DEFAULT_DOT_STYLE", "MIN_REPEAT"]
		messaging_platforms = list(set(config_json) - set(no_messaging_keys))
		globals().update({f"{key.lower()}_on": config_json[key]["ENABLED"] for key in messaging_platforms})
		for platform in messaging_platforms:
			if config_json[platform].get("ENABLED", False):
				for key, value in config_json[platform].items():
					platform_key = f"platform_{key.lower()}"
					if platform_key in globals():
						globals()[platform_key] = (globals()[platform_key] if isinstance(globals()[platform_key], list) else [globals()[platform_key]])
						globals()[platform_key].extend(value if isinstance(value, list) else [value])
					else:
						globals()[platform_key] = value if isinstance(value, list) else [value]
				monitoring_message += f"- messaging: {platform.lower().capitalize()},\n"
		monitoring_message += (
			f"- default dot style: {default_dot_style}.\n"
			f"- polling period: {min_repeat} minute(s)."
		)
		if all(value in globals() for value in ["platform_webhook_url", "platform_header", "platform_pyload", "platform_format_message"]):
			SendMessage(f"{header}hosts monitor:\n{monitoring_message}")
		else:
			print("config.json is wrong")
			exit(1)
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