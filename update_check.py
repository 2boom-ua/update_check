#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023-24

import json
import os
import time
import requests
from schedule import every, repeat, run_pending
from requests.exceptions import RequestException


def getStr(filename : str):
	ret = ""
	if os.path.exists(filename):
		with open(filename, 'r') as file:
			ret = file.read().strip('\n')
	return ret


def getHostname():
	hostname = ""
	if os.path.exists('/proc/sys/kernel/hostname'):
		with open('/proc/sys/kernel/hostname', "r") as file:
			hostname = file.read().strip('\n')
	return hostname


def SendMessage(message : str):
	message = message.replace("\t", "")
	if telegram_on:
		try:
			response = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if discord_on:
		try:
			response = requests.post(discord_web, json={"content": message.replace("*", "**")})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if slack_on:
		try:
			response = requests.post(slack_web, json = {"text": message})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	message = message.replace("*", "")
	header = message[:message.index("\n")].rstrip("\n")
	message = message[message.index("\n"):].strip("\n")
	if gotify_on:
		try:
			response = requests.post(f"{gotify_web}/message?token={gotify_token}",\
			json={'title': header, 'message': message, 'priority': 0})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if ntfy_on:
		try:
			response = requests.post(f"{ntfy_web}/{ntfy_sub}", data=message.encode(encoding='utf-8'), headers={"Title": header})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if pushbullet_on:
		try:
			response = requests.post('https://api.pushbullet.com/v2/pushes',\
			json={'type': 'note', 'title': header, 'body': message},\
			headers={'Access-Token': pushbullet_api, 'Content-Type': 'application/json'})
		except requests.exceptions.RequestException as e:
			print("error:", e)


if __name__ == "__main__":
	FileMessage = [['/run/dietpi/.apt_updates', 'apt update(s) available'], ['/run/dietpi/.update_available', 'upgrade available'],\
	['/run/dietpi/.live_patches', 'live patch(es) available']]
	hostname = getHostname()
	current_path =  os.path.dirname(os.path.realpath(__file__))
	old_status = ""
	orange_dot, green_dot = "\U0001F7E0", "\U0001F7E2"
	telegram_on = discord_on = gotify_on = ntfy_on = slack_on = pushbullet_on = False
	token = chat_id = discord_web = gotify_web = gotify_token = ntfy_web = ntfy_sub = pushbullet_api = slack_web = messaging_service = ""
	if os.path.exists(f"{current_path}/config.json"):
		with open(f"{current_path}/config.json", "r") as file:
			parsed_json = json.loads(file.read())
		telegram_on = parsed_json["TELEGRAM"]["ON"]
		discord_on = parsed_json["DISCORD"]["ON"]
		gotify_on = parsed_json["GOTIFY"]["ON"]
		ntfy_on = parsed_json["NTFY"]["ON"]
		pushbullet_on = parsed_json["PUSHBULLET"]["ON"]
		slack_on = parsed_json["SLACK"]["ON"]
		if telegram_on:
			token = parsed_json["TELEGRAM"]["TOKEN"]
			chat_id = parsed_json["TELEGRAM"]["CHAT_ID"]
			messaging_service += "- messenging: Telegram,\n"
		if discord_on:
			discord_web = parsed_json["DISCORD"]["WEB"]
			messaging_service += "- messenging: Discord,\n"
		if gotify_on:
			gotify_web = parsed_json["GOTIFY"]["WEB"]
			gotify_token = parsed_json["GOTIFY"]["TOKEN"]
			messaging_service += "- messenging: Gotify,\n"
		if ntfy_on:
			ntfy_web = parsed_json["NTFY"]["WEB"]
			ntfy_sub = parsed_json["NTFY"]["SUB"]
			messaging_service += "- messenging: Ntfy,\n"
		if pushbullet_on:
			pushbullet_api = parsed_json["PUSHBULLET"]["API"]
			messaging_service += "- messenging: Pushbullet,\n"
		if slack_on:
			slack_web = parsed_json["SLACK"]["WEB"]
			messaging_service += "- messenging: Slack,\n"
		min_repeat = int(parsed_json["MIN_REPEAT"])
		SendMessage(f"*{hostname}* (updates)\nupgrade, updates, patches monitor:\n{messaging_service}- polling period: {min_repeat} minute(s).")
	else:
		print("config.json not found")


@repeat(every(min_repeat).minutes)
def update_check():
	new_status = message =""
	current_status = []
	global old_status
	if len(old_status) == 0:
		old_status += "0" * len(FileMessage)
	current_status = list(old_status)
	for i, item in enumerate(FileMessage):
		if os.path.exists(item[0]):
			if old_status[i] == "0":
				message += f"{orange_dot} {getStr(item[0])} {item[1]}\n"
			current_status[i] = "1"
		else:
			if old_status[i] == "1":
				message += f"{green_dot} no {item[1]}\n"
			current_status[i] = "0"
	new_status = "".join(current_status)
	if old_status != new_status:
		old_status = new_status
		SendMessage(f"*{hostname}* (updates)\n{message}")


while True:
	run_pending()
	time.sleep(1)