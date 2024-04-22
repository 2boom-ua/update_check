#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023-24

import json
import os
import time
import requests
from schedule import every, repeat, run_pending

def get_str_from_file(filename : str):
	ret = ""
	if os.path.exists(filename):
		ret = open(filename, 'r').read().strip('\n')
	return ret

def send_message(message : str):
	message = message.replace("\t", "")
	if TELEGRAM_ON:
		try:
			response = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if DISCORD_ON:
		try:
			response = requests.post(DISCORD_WEB, json={"content": message.replace("*", "**")})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if SLACK_ON:
		try:
			response = requests.post(SLACK_WEB, json = {"text": message})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	message = message.replace("*", "")
	header = message[:message.index("\n")].rstrip("\n")
	message = message[message.index("\n"):].strip("\n")
	if GOTIFY_ON:
		try:
			response = requests.post(f"{GOTIFY_WEB}/message?token={GOTIFY_TOKEN}",\
			json={'title': header, 'message': message, 'priority': 0})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if NTFY_ON:
		try:
			response = requests.post(f"{NTFY_WEB}/{NTFY_SUB}", data=message.encode(encoding='utf-8'), headers={"Title": header})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if PUSHBULLET_ON:
		try:
			response = requests.post('https://api.pushbullet.com/v2/pushes',\
			json={'type': 'note', 'title': header, 'body': message},\
			headers={'Access-Token': PUSHBULLET_API, 'Content-Type': 'application/json'})
		except requests.exceptions.RequestException as e:
			print("error:", e)

if __name__ == "__main__":
	FileNameMessage = [['/run/dietpi/.apt_updates', 'apt update(s) available'], ['/run/dietpi/.update_available', 'upgrade available'],\
	['/run/dietpi/.live_patches', 'live patch(es) available']]
	HOSTNAME = open('/proc/sys/kernel/hostname', 'r').read().strip('\n')
	CURRENT_PATH =  os.path.dirname(os.path.realpath(__file__))
	TMP_FILE = "/tmp/status_update.tmp"
	ORANGE_DOT, GREEN_DOT = "\U0001F7E0", "\U0001F7E2"
	TELEGRAM_ON = DISCORD_ON = GOTIFY_ON = NTFY_ON = SLACK_ON = PUSHBULLET_ON = False
	TOKEN = CHAT_ID = DISCORD_WEB = GOTIFY_WEB = GOTIFY_TOKEN = NTFY_WEB = NTFY_SUB = PUSHBULLET_API = SLACK_WEB = MESSAGING_SERVICE = ""
	if os.path.exists(f"{CURRENT_PATH}/config.json"):
		parsed_json = json.loads(open(f"{CURRENT_PATH}/config.json", "r").read())
		TELEGRAM_ON = parsed_json["TELEGRAM"]["ON"]
		DISCORD_ON = parsed_json["DISCORD"]["ON"]
		GOTIFY_ON = parsed_json["GOTIFY"]["ON"]
		NTFY_ON = parsed_json["NTFY"]["ON"]
		PUSHBULLET_ON = parsed_json["PUSHBULLET"]["ON"]
		SLACK_ON = parsed_json["SLACK"]["ON"]
		if TELEGRAM_ON:
			TOKEN = parsed_json["TELEGRAM"]["TOKEN"]
			CHAT_ID = parsed_json["TELEGRAM"]["CHAT_ID"]
			MESSAGING_SERVICE += "- messenging: Telegram,\n"
		if DISCORD_ON:
			DISCORD_WEB = parsed_json["DISCORD"]["WEB"]
			MESSAGING_SERVICE += "- messenging: Discord,\n"
		if GOTIFY_ON:
			GOTIFY_WEB = parsed_json["GOTIFY"]["WEB"]
			GOTIFY_TOKEN = parsed_json["GOTIFY"]["TOKEN"]
			MESSAGING_SERVICE += "- messenging: Gotify,\n"
		if NTFY_ON:
			NTFY_WEB = parsed_json["NTFY"]["WEB"]
			NTFY_SUB = parsed_json["NTFY"]["SUB"]
			MESSAGING_SERVICE += "- messenging: Ntfy,\n"
		if PUSHBULLET_ON:
			PUSHBULLET_API = parsed_json["PUSHBULLET"]["API"]
			MESSAGING_SERVICE += "- messenging: Pushbullet,\n"
		if SLACK_ON:
			SLACK_WEB = parsed_json["SLACK"]["WEB"]
			MESSAGING_SERVICE += "- messenging: Slack,\n"
		MIN_REPEAT = int(parsed_json["MIN_REPEAT"])
		send_message(f"*{HOSTNAME}* (updates)\nupgrade, updates, patches monitor:\n{MESSAGING_SERVICE}- polling period: {MIN_REPEAT} minute(s).")
	else:
		print("config.json not found")
	
@repeat(every(MIN_REPEAT).minutes)
def update_check():
	NEW_STATUS = MESSAGE = OLD_STATUS = ""
	OLD_STATUS += "0" * len(FileNameMessage)
	li = list(OLD_STATUS )
	if not os.path.exists(TMP_FILE) or os.path.getsize(TMP_FILE) != len(FileNameMessage):
		with open(TMP_FILE, "w") as file:
			file.write(OLD_STATUS)
		file.close()
	with open(TMP_FILE, "r") as file:
		OLD_STATUS = file.read()
	file.close()
	for i in range(len(OLD_STATUS)):
		if os.path.exists(FileNameMessage[i][0]):
			MESSAGE += f"{ORANGE_DOT} - {get_str_from_file(FileNameMessage[i][0])} {FileNameMessage[i][1]}\n"
			li[i] = "1"
		else:
			MESSAGE += f"{GREEN_DOT} - no {FileNameMessage[i][1]}\n"
			li[i] = "0"
	NEW_STATUS = "".join(li)
	if OLD_STATUS != NEW_STATUS:
		with open(TMP_FILE, "w") as file:
			file.write(NEW_STATUS)
		file.close()
		send_message(f"*{HOSTNAME}* (updates)\n{MESSAGE}")

while True:
    run_pending()
    time.sleep(1)