#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023

import json
import os.path
import os
import telebot
import time
from schedule import every, repeat, run_pending

def get_str_from_file(filename):
	if os.path.exists(filename):
		with open(filename, "r") as data_file:
			ret = data_file.read().strip("\n")
		data_file.close()
		return ret
	return ""
	
def hbold(item):
	return telebot.formatting.hbold(item)

hostname = hbold(get_str_from_file("/proc/sys/kernel/hostname"))
current_path = "/root/update_check"
tmp_file = "/tmp/status_update.tmp"
ORANGE_DOT, GREEN_DOT = "\U0001F7E0", "\U0001F7E2"
file_messages = [['/run/dietpi/.apt_updates', 'apt update(s) available'], ['/run/dietpi/.update_available', 'upgrade available'], ['/run/dietpi/.live_patches', 'live patch(es) available']]

if os.path.exists(f"{current_path}/config.json"):
	parsed_json = json.loads(open(f"{current_path}/config.json", "r").read())
	min_repeat = int(parsed_json["minutes"])
else:
	min_repeat = 3

if os.path.exists(f"{current_path}/telegram_bot.json"):
	parsed_json = json.loads(open(f"{current_path}/telegram_bot.json", "r").read())
	TOKEN = parsed_json["TOKEN"]
	CHAT_ID = parsed_json["CHAT_ID"]
	tb = telebot.TeleBot(TOKEN)
	try:
		tb.send_message(CHAT_ID, f"{hostname} (updates)\nupgrade, updates, patches monitor started: check period {min_repeat} minute(s)", parse_mode='html')
	except Exception as e:
		print(f"error: {e}")
else:
	print("telegram_bot.json not found")

@repeat(every(min_repeat).minutes)
def update_check():
	new_status_str = update_message = ""
	old_status_str = "000"
	li = ["0", "0", "0"]
	if not os.path.exists(tmp_file) or os.path.getsize(tmp_file) != 3:
		with open(tmp_file, "w") as status_file:
			status_file.write(old_status_str)
		status_file.close()
	with open(tmp_file, "r") as status_file:
		old_status_str = status_file.read()
		status_file.close()
	for i in range(0, 3):
		if os.path.exists(file_messages[i][0]):
			update_message += f"{ORANGE_DOT} - {get_str_from_file(file_messages[i][0])} {file_messages[i][1]}\n"
			li[i] = "1"
		else:
			update_message += f"{GREEN_DOT} - no {file_messages[i][1]}\n"
			li[i] = "0"
	new_status_str = "".join(li)
	if old_status_str != new_status_str:
		with open(tmp_file, "w") as status_file:
			status_file.write(new_status_str)
			status_file.close()
		try:
			tb.send_message(CHAT_ID, f"{hostname} (updates)\n{update_message}", parse_mode='html')
		except Exception as e:
			print(f"error: {e}")
while True:
    run_pending()
    time.sleep(1)