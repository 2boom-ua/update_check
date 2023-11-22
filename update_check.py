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
		
def get_current_version():
	filename = "/boot/dietpi/.version"
	ver = ""
	if os.path.exists(filename):
		for line in open(filename, "r"):
			if line.startswith("G_DIETPI_VERSION_CORE") or line.startswith("G_DIETPI_VERSION_SUB") or line.startswith("G_DIETPI_VERSION_RC"):
				ver += "%s." % line.split('=')[1].rstrip('\n')
		ver = ver.rstrip(".")
		return ver
	else:
		return "unknow"
	
def hbold(item):
	return telebot.formatting.hbold(item)

hostname = hbold(get_str_from_file("/proc/sys/kernel/hostname"))
current_path = "/root/update_check"
tmp_file = "/tmp/status_update.tmp"
mode = mode_command = "silent"
update_message = upgrade_message = patch_message = ""
if os.path.exists(f"{current_path}/config.json"):
	parsed_json = json.loads(open(f"{current_path}/config.json", "r").read())
	min_repeat = int(parsed_json["minutes"])
else:
	min_repeat = 3
ORANGE_DOT, GREEN_DOT = "\U0001F7E0", "\U0001F7E2"

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
	status_message = old_status_str = new_status_str = ""
	if not os.path.exists(tmp_file) or os.path.getsize(tmp_file) != 3:
		with open(tmp_file, "w") as status_file:
			for i in range(0, 3):
				old_status_str += "0"
			status_file.write(old_status_str)
		status_file.close()
	with open(tmp_file, "r") as status_file:
		old_status_str = status_file.read()
		li = list(old_status_str)
		status_file.close()
	if os.path.exists("/run/dietpi/.apt_updates"):
		update_message = f"{ORANGE_DOT} - {get_str_from_file('/run/dietpi/.apt_updates')} apt update(s) available"
		li[0] = "1"
	else:
		update_message = f"{GREEN_DOT} - no apt update(s) available"
		li[0] = "0"
	if os.path.exists("/run/dietpi/.update_available"):
		upgrade_message = f"{ORANGE_DOT} - {get_current_version()}->{get_str_from_file('/run/dietpi/.update_available')} upgrade available"
		li[1] = "1"
	else:
		upgrade_message = f"{GREEN_DOT} - no upgrade available"
		li[1] = "0"
	if os.path.exists("/run/dietpi/.live_patches"):
		patch_message = f"{ORANGE_DOT} - {get_str_from_file('/run/dietpi/.live_patches')} live patch(es) available"
		li[2] = "1"
	else:
		patch_message = f"{GREEN_DOT} - no live patch(es) available"
		li[2] = "0"
	new_status_str = "".join(li)
	if old_status_str == new_status_str:
		mode = "silent"
	else:
		mode = "info"
		with open(tmp_file, "w") as status_file:
			status_file.write(new_status_str)
			status_file.close()
	if mode_command == "info" or mode == "info":
		try:
			tb.send_message(CHAT_ID, f"{hostname} (updates)\n{update_message}\n{upgrade_message}\n{patch_message}\n", parse_mode='html')
		except Exception as e:
			print(f"error: {e}")
	#print(f"{hostname}\n{update_message}\n{upgrade_message}\n{patch_message}")

while True:
    run_pending()
    time.sleep(1)