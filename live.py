from bs4 import BeautifulSoup
import markdownify
import requests
import time
import re

GUID_REGEX = r'[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'
URL_REGEX = r'\(https?:.*\)'
MD_URL_REGEX = r'\[.*\]\(.*\)'

REPLACE_CHARS = "<>"

REDDIT_LIVE_LINK = "https://www.reddit.com/live/18hnzysb1elcs"

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/534.11 (KHTML, like Gecko) '
                         'Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'
}


def update_entries():
    # with open("sample.html", 'r', encoding='utf-8') as f:
    #     live = f.read()

    entries = {}

    html_content = requests.get(REDDIT_LIVE_LINK, headers).content

    print(html_content)

    soup = BeautifulSoup(html_content, 'html.parser')

    live_updates = soup.find_all('li', {'class': 'liveupdate'})

    for live_entry in live_updates:
        live_entry.find('a', {'class': 'author'}).decompose()
        live_entry_str = str(live_entry)

        live_entry_guid = re.findall(GUID_REGEX, live_entry_str)[0]

        live_entry_md = markdownify.markdownify(str(live_entry), heading_style="ATX", convert=['a'])

        links = re.findall(URL_REGEX, live_entry_md) # Extract all links
        live_entry_md = re.sub(MD_URL_REGEX, '', live_entry_md) # Remove all markdown links

        for char in REPLACE_CHARS:
            live_entry_md = live_entry_md.replace(char, "")

        msg = f"{live_entry_md.strip()} {','.join(links)}" # Add links to send

        entries[live_entry_guid] = msg

    return entries

if __name__ == "__main__":
    entries_initial = {}

    entries_initial = update_entries() # We don't send existing entries

    #print(entries_initial)

    while True:
        print("Running task...")
        time.sleep(60)

        entries_snapshot = update_entries()
        entries_new = C = {k:v for k,v in entries_snapshot.items() if k not in entries_initial}

        print(entries_new)
