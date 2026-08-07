import os
import requests
import feedparser
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = "8947309767:AAEIIbEOKRt9COi2x7rdkNKhewmymZrKPaI"
CHAT_ID = "8925137681"
SEEN_FILE = "seen_tweets.txt"

RSS_FEEDS = [
    "https://rss.app/feeds/3oU5OjGYQb4ZoNSb.xml",
    "https://rss.app/feeds/bu0XxAFEoGwwP7aS.xml",
    "https://rss.app/feeds/5ogaHtHdW8LCyzoR.xml",
    "https://rss.app/feeds/1Z2sBzwxDUVd0kdX.xml",
    "https://rss.app/feeds/68mfHkIfwEv5LeJT.xml",
    "https://rss.app/feeds/0WxElD3bKSrbqXaS.xml",
    "https://rss.app/feeds/WdN4B5y3jEH8H5el.xml",
    "https://rss.app/feeds/ejIPq5QEbz8QE3Is.xml"
]

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    try:
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f)
    except Exception:
        return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        for tweet_id in seen:
            f.write(f"{tweet_id}\n")

def send_telegram_media(caption, photo_url):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

def check_tweets():
    seen = load_seen()
    new_seen = set(seen)
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:
                if entry.id not in seen:
                    soup = BeautifulSoup(entry.summary, "html.parser")
                    # جلب النص
                    text = soup.get_text()
                    # محاولة العثور على صورة حقيقية داخل التغريدة
                    img = soup.find("img")
                    img_url = img["src"] if img else None
                    
                    message = f"🔥 <b>تغريدة جديدة!</b>\n\n{text}\n\n🔗 <a href='{entry.link}'>اضغط هنا للمشاهدة</a>"
                    
                    if img_url:
                        send_telegram_media(message, img_url)
                    else:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                                      json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})
                    
                    new_seen.add(entry.id)
        except Exception as e:
            print(f"Error: {e}")
            
    save_seen(new_seen)

if __name__ == "__main__":
    check_tweets()
