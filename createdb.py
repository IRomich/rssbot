import sqlite3
from pathlib import Path

script_dir = Path(__file__).parent.absolute()
#Connecting to sqlite
conn = sqlite3.connect(str(script_dir) + '/rss.db')

cursor = conn.cursor()
cursor.execute("CREATE TABLE feeds (id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name TEXT, url TEXT, last_id INTEGER)")
cursor.execute("CREATE TABLE records (id INTEGER PRIMARY KEY ASC AUTOINCREMENT, title TEXT, link TEXT, published DATETIME, feed_id INTEGER NOT NULL REFERENCES feeds(id))")
conn.commit()
