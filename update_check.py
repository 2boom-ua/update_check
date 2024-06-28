#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023-24

import json
import os
import time
import requests
from schedule import every, repeat, run_pending


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


def sendMessage(message : str):
	if telegram_on:
		try:
			for telegram_token, telegram_chat_id in zip(telegram_tokens, telegram_chat_ids):
				requests.post(f"https://api.telegram.org/bot{telegram_token}/sendMessage", json = {"chat_id": telegram_chat_id, "text": message, "parse_mode": "Markdown"})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if discord_on:
		try:
			for discord_token in discord_tokens:
				requests.post(f"https://discord.com/api/webhooks/{discord_token}", json = {"content": message.replace("*", "**")})
		except requests.exceptions.RequestException as e:
			print("Error:", e)
	if slack_on:
		try:
			for slack_token in slack_tokens:
				requests.post(f"https://hooks.slack.com/services/{slack_token}", json = {"text": message})
		except requests.exceptions.RequestException as e:
			print("Error:", e)
	message = message.replace("*", "")
	header = message[:message.index("\n")].rstrip("\n")
	message = message[message.index("\n"):].strip("\n")
	if gotify_on:
		try:
			for gotify_chat_web, gotify_token in zip(gotify_chat_webs, gotify_tokens):
				requests.post(f"{gotify_chat_web}/message?token={gotify_token}",\
				json={'title': header, 'message': message, 'priority': 0})
		except requests.exceptions.RequestException as e:
			print("Error:", e)
	if ntfy_on:
		try:
			for ntfy_chat_web, ntfy_token in zip(ntfy_chat_webs, ntfy_tokens):
				requests.post(f"{ntfy_chat_web}/{ntfy_token}", data = message.encode(encoding = 'utf-8'), headers = {"title": header})
		except requests.exceptions.RequestException as e:
			print("Error:", e)
	if pushbullet_on:
		try:
			for pushbullet_token in pushbullet_tokens:
				requests.post('https://api.pushbullet.com/v2/pushes',\
				json = {'type': 'note', 'title': header, 'body': message},\
				headers = {'Access-Token': pushbullet_token, 'Content-Type': 'application/json'})
		except requests.exceptions.RequestException as e:
			print("Error:", e)



if __name__ == "__main__":
	FileMessage = [['/run/dietpi/.apt_updates', 'apt update(s) available'], ['/run/dietpi/.update_available', 'upgrade available'],\
	['/run/dietpi/.live_patches', 'live patch(es) available']]
	hostname = getHostname()
	header = f"*{hostname}* (updates)\n"
	current_path =  os.path.dirname(os.path.realpath(__file__))
	old_status = ""
	orange_dot, green_dot = "\U0001F7E0", "\U0001F7E2"
	monitoring_mg = ""
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
			telegram_tokens = parsed_json["TELEGRAM"]["TOKENS"]
			telegram_chat_ids = parsed_json["TELEGRAM"]["CHAT_IDS"]
			monitoring_mg += "- messenging: Telegram,\n"
		if discord_on:
			discord_tokens = parsed_json["DISCORD"]["TOKENS"]
			monitoring_mg += "- messenging: Discord,\n"
		if slack_on:
			slack_tokens = parsed_json["SLACK"]["TOKENS"]
			monitoring_mg += "- messenging: Slack,\n"
		if gotify_on:
			gotify_tokens = parsed_json["GOTIFY"]["TOKENS"]
			gotify_chat_webs = parsed_json["GOTIFY"]["CHAT_WEB"]
			monitoring_mg += "- messenging: Gotify,\n"
		if ntfy_on:
			ntfy_tokens = parsed_json["NTFY"]["TOKENS"]
			ntfy_chat_webs = parsed_json["NTFY"]["CHAT_WEB"]
			monitoring_mg += "- messenging: Ntfy,\n"
		if pushbullet_on:
			pushbullet_tokens = parsed_json["PUSHBULLET"]["TOKENS"]
			monitoring_mg += "- messenging: Pushbullet,\n"
		min_repeat = int(parsed_json["MIN_REPEAT"])
		sendMessage(f"{header}upgrade, updates, patches monitor:\n{monitoring_mg}- polling period: {min_repeat} minute(s).")
	else:
		print("config.json not found")


@repeat(every(min_repeat).minutes)
def update_check():
	new_status = message =""
	current_status = []
	global old_status
	if not old_status: old_status += "0" * len(FileMessage)
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
		sendMessage(f"{header}{message}")


while True:
	run_pending()
	time.sleep(1)
