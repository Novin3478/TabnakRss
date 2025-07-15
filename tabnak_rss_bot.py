# tabnak_rss_bot.py

import requests
import feedparser
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BALE_BOT_TOKEN")
CHANNEL_ID = os.getenv("BALE_CHANNEL_ID")

RSS_URL = "https://www.tabnak.ir/fa/rss/3/mostvisited"  # اقتصادی

def fetch_tabnak_economy_rss():
    feed = feedparser.parse(RSS_URL)
    posts = []
    for entry in feed.entries[:5]:  # فقط ۵ خبر اول
        title = entry.title
        link = entry.link
        summary = entry.summary
        content = f"📌 {title}\n{summary.strip()}\n\n🔗 ادامه خبر:\n{link}\n\n📣 منبع: [کانال نوین ابزار]({SOURCE_LINK})"
        posts.append(content)
    return posts

def send_to_bale(message):
    url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    resp = requests.post(url, json=data)
    print(resp.status_code, resp.text)

if __name__ == "__main__":
    SOURCE_LINK = "https://web.bale.ai/chat?uid=6100393162"
    posts = fetch_tabnak_economy_rss()
    for post in posts:
        send_to_bale(post)
