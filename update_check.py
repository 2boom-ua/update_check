#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023-24

import yaml
import os
import telebot
import time
from schedule import every, repeat, run_pending

def get_str_from_file(filename : str):
	ret = ""
	if os.path.exists(filename):
		ret = open(filename, 'r').read().strip('\n')
	return ret

def telegram_message(message : str):
	try:
		tb.send_message(CHAT_ID, message, parse_mode='markdown')
	except Exception as e:
		print(f"error: {e}")

if __name__ == "__main__":
	FileNameMessage = [['/run/dietpi/.apt_updates', 'apt update(s) available'], ['/run/dietpi/.update_available', 'upgrade available'], ['/run/dietpi/.live_patches', 'live patch(es) available']]
	HOSTNAME = open('/proc/sys/kernel/hostname', 'r').read().strip('\n')
	CURRENT_PATH = "/root/update_check"
	TMP_FILE = "/tmp/status_update.tmp"
	ORANGE_DOT, GREEN_DOT = "\U0001F7E0", "\U0001F7E2"
	if os.path.exists(f"{CURRENT_PATH}/config.yml"):
		with open(f"{CURRENT_PATH}/config.yml", 'r') as file:
			parsed_yaml = yaml.safe_load(file)
			TOKEN = parsed_yaml["telegram"]["TOKEN"]
			CHAT_ID = parsed_yaml["telegram"]["CHAT_ID"]
			MIN_REPEAT = parsed_yaml["timeout"]["MIN_REPEAT"]
		file.close()
		tb = telebot.TeleBot(TOKEN)
		telegram_message(f"*{HOSTNAME}* (updates)\nupgrade, updates, patches monitor started: check period {MIN_REPEAT} minute(s)")
	else:
		print("config.yml not found")
	
@repeat(every(MIN_REPEAT).minutes)
def update_check():
	NEW_STATUS = MESSAGE = OLD_STATUS = ""
	OLD_STATUS += "0" * len(FileNameMessage)
	li = list(OLD_STATUS )
	if not os.path.exists(TMP_FILE) or os.path.getsize(TMP_FILE) != len(FileNameMessage):
		with open(TMP_FILE, "w") as file:
			file.write(OLD_STATUS)
		file.close()
	else:
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
		telegram_message(f"*{HOSTNAME}* (updates)\n{MESSAGE}")

while True:
    run_pending()
    time.sleep(1)