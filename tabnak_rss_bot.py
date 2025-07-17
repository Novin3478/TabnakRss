import feedparser
import requests
import time
import os
from datetime import datetime

# تنظیمات
RSS_FEED_URL = "https://www.khabaronline.ir/rss?cat=3"  # اقتصاد کلان به‌عنوان نمونه
BOT_TOKEN = os.getenv("BALA_BOT_TOKEN")
CHANNEL_ID = os.getenv("BALA_CHANNEL_ID")
MAX_SUMMARY_LENGTH = 300  # حداکثر تعداد کاراکتر خلاصه
FETCH_INTERVAL = 1800  # هر 30 دقیقه یک بار بررسی فید

sent_links = set()

# تابع خلاصه‌سازی ساده
def summarize(text, max_length):
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(".", 1)[0] + "..."

# تابع ارسال پیام به بله
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
    except Exception as e:
        print(f"❌ خطا در ارسال پیام به بله: {e}")

# حلقه اصلی
while True:
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
            send_to_bale(message)
            sent_links.add(link)
            time.sleep(5)
    
        print(f"🔁 بررسی مجدد در {FETCH_INTERVAL//60} دقیقه...")
        time.sleep(FETCH_INTERVAL)

    except Exception as e:
        print(f"💥 خطا در اجرای ربات: {e}")
        time.sleep(60)
