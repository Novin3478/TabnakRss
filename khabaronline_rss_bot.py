from flask import Flask, request, jsonify
import feedparser
import requests
import os

app = Flask(__name__)

RSS_FEED_URL = "https://www.khabaronline.ir/rss?cat=3"
BOT_TOKEN = os.getenv("BALA_BOT_TOKEN")
CHANNEL_ID = os.getenv("BALA_CHANNEL_ID")
MAX_SUMMARY_LENGTH = 300
sent_links_file = "sent_links.txt"

def load_sent_links():
    if not os.path.exists(sent_links_file):
        return set()
    with open(sent_links_file, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_sent_link(link):
    with open(sent_links_file, "a") as f:
        f.write(link + "\n")

def summarize(text, max_length):
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(".", 1)[0] + "..."

def send_to_bale(text):
    url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ پیام با موفقیت ارسال شد.")
        return True
    except Exception as e:
        print(f"❌ خطا در ارسال پیام به بله: {e}")
        return False

@app.route("/run", methods=["GET"])
def run_bot():
    sent_links = load_sent_links()
    sent_count = 0
    try:
        feed = feedparser.parse(RSS_FEED_URL)
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
                save_sent_link(link)
                sent_count += 1

        return jsonify({"status": "success", "sent": sent_count})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
