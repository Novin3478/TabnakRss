from flask import Flask, jsonify
import feedparser
import requests
import os

app = Flask(__name__)

# تنظیمات
RSS_FEED_URL = "https://www.khabaronline.ir/rss?cat=3"  # اقتصاد کلان
BOT_TOKEN = os.getenv("BALA_BOT_TOKEN")
CHANNEL_ID = os.getenv("BALA_CHANNEL_ID")
MAX_SUMMARY_LENGTH = 300

sent_links = set()

def summarize(text, max_length):
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(".", 1)[0] + "..."

def send_to_bale(text):
    url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ پیام با موفقیت ارسال شد.")
        return True
    except Exception as e:
        print(f"❌ خطا در ارسال پیام به بله: {e}")
        return False

def fetch_and_send_news():
    feed = feedparser.parse(RSS_FEED_URL)
    new_items = 0
    for entry in feed.entries:
        link = entry.link
        if link in sent_links:
            continue
        title = entry.title.strip()
        summary = summarize(entry.summary.strip(), MAX_SUMMARY_LENGTH)
        published = entry.published if 'published' in entry else ''
        message = f"📌 {title}\n\n📝 {summary}\n\n🕒 {published}"
        if send_to_bale(message):
            sent_links.add(link)
            new_items += 1
    return new_items

@app.route('/')
def home():
    return "ربات خبری تابناک ریسپانس میده! داره کار می‌کنه."

@app.route('/run')
def run_bot():
    count = fetch_and_send_news()
    return jsonify({"status": "done", "new_items_sent": count})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
