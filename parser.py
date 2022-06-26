#!/usr/bin/python3

import feedparser, sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re

tz = {'PDT': '-0700', 'EST': '-0500', 'GMT': '+0000'}
script_dir = Path(__file__).parent.absolute()
conn = sqlite3.connect(str(script_dir) + '/rss.db')
cursor = conn.cursor()
now = datetime.now(timezone.utc) - timedelta(hours=1)
cursor.execute('select * from feeds;')
feeds = cursor.fetchall()
for feed in feeds:
    d = feedparser.parse(feed[2])
    for entry in d['entries']:
        pubDatetime = 0
        if re.match("\w{3},\s\d{2}\s\w{3}\s\d{4}\s\d{2}:\d{2}:\d{2}\s\w{3}", entry['published']):
            entry['published'] = entry['published'][0:-3] + tz[entry['published'][-3:]] 
        if re.match("\w{3},\s\d{2}\s\w{3}\s\d{4}\s\d{2}:\d{2}:\d{2}\s(\+|\-)\d{4}", entry['published']):
            pubDatetime = datetime.strptime(entry['published'], '%a, %d %b %Y %H:%M:%S %z')
        elif re.match("\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}", entry['published']):
            pubDatetime = datetime.strptime(entry['published'], '%Y-%m-%dT%H:%M:%S%z')
        if now >= pubDatetime:
            break
        cursor.execute("insert into records (title,link,published,feed_id) values(?,?,?,?)", (entry['title'],entry['link'],entry['published'],feed[0]))
        conn.commit()
conn.close()
