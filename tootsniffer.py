#!/usr/bin/env python

import yaml
import requests
import json
import time
from io import StringIO
from html.parser import HTMLParser
import datetime
from datetime import datetime
from datetime import timedelta
import os

today = datetime.today()
fifteen_minutes_ago = today - timedelta(hours=1)

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

COLOR = {
    "GREY": "\033[90m",
    "GREEN": "\033[92m",
    "ENDC": "\033[0m",
}

def main():
    
    os.system("")  # enables ansi escape characters in terminal
    print("Reading Config")
    with open("config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    print("UserAgent...")
    useragent = config["user_agent"]
    headers = {'User-Agent': useragent}
    print("Server List...")
    serverlist = config["server_list"]
    while True:
        queue = []
        for server in serverlist:
            response = requests.get("https://"+server+"/api/v1/timelines/public?&only_media=false&limit=40", headers=headers)
            print("Recieved",len(response.json()),"toots from", server)
            for item in response.json():
                stamp = datetime.fromisoformat(item["created_at"][:-1])
                if stamp < fifteen_minutes_ago:
                    break
                date_and_content = []
                date_and_content.append(item["created_at"])
                toot  = COLOR["GREEN"]
                toot += "@{}".format(item["account"]["username"])
                toot += " : "
                toot += COLOR["ENDC"]
                toot += strip_tags(item["content"])
                toot += "\n"
                toot += COLOR["GREY"]
                toot += item["url"]
                toot += COLOR["ENDC"]
                toot += "\n"
                toot +=" ↩️:" +str(item["replies_count"])
                toot +=" 🔁:" +str(item["reblogs_count"])
                toot +=" ❤️:" +str(item["favourites_count"])
                toot += "\n"
                date_and_content.append(toot)
                if date_and_content not in queue:
                    queue.append(date_and_content)
                
        
        queue_length = len(queue)
        queue.sort(key=lambda row: row[0])
        for toot in queue:
            print(toot[1])
            time.sleep(900/queue_length)


main()