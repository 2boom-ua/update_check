#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Copyright (c) 2024-25 2boom.

import json
import os
import sys
import time
import requests
import logging
import random
from schedule import every, repeat, run_pending
from urllib.parse import urlparse


"""Configure logging"""
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


"""Get base url"""
def GetBaseUrl(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}...."


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
    """Internal function to send HTTP POST requests with error handling"""

    def SendRequest(url, json_data=None, data=None, headers=None):
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                response = requests.post(url, json=json_data, data=data, headers=headers, timeout=(5, 20))
                response.raise_for_status()
                logger.info(f"Message successfully sent to {GetBaseUrl(url)}. Status code: {response.status_code}")
                return
            except requests.exceptions.RequestException as e:
                logger.error(f"Attempt {attempt + 1}/{max_attempts} - Error sending message to {GetBaseUrl(url)}: {e}")
                if attempt == max_attempts - 1:
                    logger.error(f"Failed to send message to {GetBaseUrl(url)} after {max_attempts} attempts")
                else:
                    backoff_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Retrying in {backoff_time:.2f} seconds...")
                    time.sleep(backoff_time)

    """Converts Markdown-like syntax to HTML format."""
    def toHTMLFormat(message: str) -> str:
        message = ''.join(f"<b>{part}</b>" if i % 2 else part for i, part in enumerate(message.split('*')))
        return message.replace("\n", "<br>")

    """Converts the message to the specified format (HTML, Markdown, or plain text)"""
    def toMarkdownFormat(message: str, m_format: str) -> str:
        if m_format == "html":
            return toHTMLFormat(message)
        elif m_format == "markdown":
            return message.replace("*", "**")
        elif m_format == "text":
            return message.replace("*", "")
        elif m_format == "simplified":
            return message
        else:
            logger.error(f"Unknown format '{m_format}' provided. Returning original message.")
            return message

    """Iterate through multiple platform configurations"""
    for url, header, payload, format_message in zip(platform_webhook_url, platform_header, platform_payload, platform_format_message):
        data, ntfy = None, False
        formated_message = toMarkdownFormat(message, format_message)
        header_json = header if header else None
        for key in list(payload.keys()):
            if key == "title":
                delimiter = "<br>" if format_message == "html" else "\n"
                header, formated_message = formated_message.split(delimiter, 1)
                payload[key] = header.replace("*", "")
            elif key == "extras":
                formated_message = formated_message.replace("\n", "\n\n")
                payload["message"] = formated_message
            elif key == "data":
                ntfy = True
            payload[key] = formated_message if key in ["text", "content", "message", "body", "formatted_body", "data"] else payload[key]
        payload_json = None if ntfy else payload
        data = formated_message.encode("utf-8") if ntfy else None
        """Send the request with the appropriate payload and headers"""
        SendRequest(url, payload_json, data, header_json)


if __name__ == "__main__":
    """Load configuration and initialize monitoring"""
    update_status_files = [
        ['/run/dietpi/.apt_updates', 'apt update(s) available'],
        ['/run/dietpi/.update_available', 'upgrade available'],
        ['/run/dietpi/.live_patches', 'live patch(es) available']
    ]
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")
    dots = {"orange": "\U0001F7E0", "green": "\U0001F7E2"}
    square_dots = {"orange": "\U0001F7E7", "green": "\U0001F7E9"}
    monitoring_message = old_status = ""
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config_json = json.loads(file.read())
        try:
            startup_message = config_json.get("STARTUP_MESSAGE", True)
            default_dot_style = config_json.get("DEFAULT_DOT_STYLE", True)
            min_repeat = max(int(config_json.get("MIN_REPEAT", 1)), 1)
        except (json.JSONDecodeError, ValueError, TypeError, KeyError):
            default_dot_style = startup_message = True
            min_repeat = 1
            logger.error("Error or incorrect settings in config.json. Default settings will be used.")
        hostname = getHostName()
        header = f"*{hostname}* (updates)\n"
        if not default_dot_style:
            dots = square_dots
        orange_dot, green_dot = dots["orange"], dots["green"]
        no_messaging_keys = ["STARTUP_MESSAGE", "DEFAULT_DOT_STYLE", "MIN_REPEAT"]
        messaging_platforms = list(set(config_json) - set(no_messaging_keys))
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
        if all(value in globals() for value in ["platform_webhook_url", "platform_header", "platform_payload", "platform_format_message"]):
            logger.info(f"Started!")
            if startup_message:
                SendMessage(f"{header}updates monitor:\n{monitoring_message}")
        else:
            logger.error("config.json is wrong")
            sys.exit(1)
    else:
        logger.error("config.json not found")
        sys.exit(1)


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