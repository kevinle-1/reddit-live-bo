from bs4 import BeautifulSoup
import markdownify
import requests
import logging
import yaml
import time
import re

logger = logging.getLogger('live')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('live.log')
fh.setLevel(logging.INFO)

logger.addHandler(fh)

GUID_REGEX = r'[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'
URL_REGEX = r'\(https?:.*\)'
MD_URL_REGEX = r'\[.*\]\(.*\)'

REPLACE_CHARS = "<>()"

with open("conf.yaml", "r") as c: cfg = yaml.safe_load(c)

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}

def update_entries():
    entries = {}

    html_content = requests.get(cfg['endpoints']['reddit'], headers=headers).content
    soup = BeautifulSoup(html_content, 'html.parser')

    live_updates = soup.find_all('li', {'class': 'liveupdate'})

    for live_entry in live_updates:
        live_entry.find('a', {'class': 'author'}).decompose()
        live_entry_str = str(live_entry)

        live_entry_guid = re.findall(GUID_REGEX, live_entry_str)[0]

        live_entry_md = markdownify.markdownify(str(live_entry), heading_style="ATX", convert=['a'])

        links = re.findall(URL_REGEX, live_entry_md) # Extract all links
        live_entry_md = re.sub(MD_URL_REGEX, '', live_entry_md) # Remove all markdown links
        
        msg = f"{live_entry_md.strip()} - {', '.join(links)}" # Add links to send

        for char in REPLACE_CHARS:
            msg = msg.replace(char, "")

        entries[live_entry_guid] = msg

    return entries

def send_to_webhook(entries_new):
    for key, value in entries_new.items():
        print(f"Sending {key} to webhook")

        data = {"content": value}
        webhooks = cfg['endpoints']['webhooks']
        
        logger.debug(f"Sending {key} to {len(webhooks)} webhooks")
        
        for webhook in webhooks:
            requests.post(webhook, json=data)

if __name__ == "__main__":
    entries_current_state = update_entries() # Don't send existing entries

    while True:
        logger.info("Checking for additional posts...")
        time.sleep(cfg["refresh"])

        entries_snapshot = update_entries()
        entries_new = C = {k:v for k,v in entries_snapshot.items() if k not in entries_current_state}

        entries_current_state = entries_snapshot

        print(entries_new)

        send_to_webhook(entries_new)