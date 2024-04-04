#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023-24

import json
import os
import telebot
import time
import requests
import discord_notify as dn
from schedule import every, repeat, run_pending
from urllib.error import URLError, HTTPError

def get_str_from_file(filename : str):
	ret = ""
	if os.path.exists(filename):
		ret = open(filename, 'r').read().strip('\n')
	return ret

def send_message(message : str):
	if TELEGRAM_ON:
		try:
			tb.send_message(CHAT_ID, message, parse_mode="markdown")
		except Exception as e:
			print(f"error: {e}")
	if DISCORD_ON:
		try:
			notifier.send(message.replace("*", "**").replace("\t", ""), print_message=False)
		except Exception as e:
			print(f"error: {e}")
	if GOTIFY_ON:
		message = message.replace("*", "").replace("\t", "")
		try:
			response = requests.post(f'{GOTIFY_WEB}?token={GOTIFY_TOKEN}', json={"message": message})
		except HTTPError as e:
			print(f"reason: {e.reason}")

if __name__ == "__main__":
	FileNameMessage = [['/run/dietpi/.apt_updates', 'apt update(s) available'], ['/run/dietpi/.update_available', 'upgrade available'],\
	['/run/dietpi/.live_patches', 'live patch(es) available']]
	HOSTNAME = open('/proc/sys/kernel/hostname', 'r').read().strip('\n')
	CURRENT_PATH =  os.path.dirname(os.path.realpath(__file__))
	TMP_FILE = "/tmp/status_update.tmp"
	ORANGE_DOT, GREEN_DOT = "\U0001F7E0", "\U0001F7E2"
	if os.path.exists(f"{CURRENT_PATH}/config.json"):
		parsed_json = json.loads(open(f"{CURRENT_PATH}/config.json", "r").read())
		TELEGRAM_ON = parsed_json["TELEGRAM"]["ON"]
		DISCORD_ON = parsed_json["DISCORD"]["ON"]
		GOTIFY_ON = parsed_json["GOTIFY"]["ON"]
		if TELEGRAM_ON:
			TOKEN = parsed_json["TELEGRAM"]["TOKEN"]
			CHAT_ID = parsed_json["TELEGRAM"]["CHAT_ID"]
			tb = telebot.TeleBot(TOKEN)
		if DISCORD_ON:
			DISCORD_WEB = parsed_json["DISCORD"]["WEB"]
			notifier = dn.Notifier(DISCORD_WEB)
		if GOTIFY_ON:
			GOTIFY_WEB = parsed_json["GOTIFY"]["WEB"]
			GOTIFY_TOKEN = parsed_json["GOTIFY"]["TOKEN"]
		MIN_REPEAT = int(parsed_json["MIN_REPEAT"])
		send_message(f"*{HOSTNAME}* (updates)\nupgrade, updates, patches monitor started:\n\
		- polling period: {MIN_REPEAT} minute(s),\n\
		- messenging Telegram: {str(TELEGRAM_ON).lower()},\n\
		- messenging Discord: {str(DISCORD_ON).lower()},\n\
		- messenging Gotify: {str(GOTIFY_ON).lower()}.")
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