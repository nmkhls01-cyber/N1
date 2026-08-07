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

def send_telegram_media(caption, photo_url, link):
    # إرسال التغريدة مع صورة في حال توفرت صورة مرفقة
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload, timeout=10)
    
    # إذا فشل إرسال الصورة لسبب ما، يرسلها كنص عادي مع الرابط لضمان عدم ضياع التغريدة
    if response.status_code != 200:
        send_telegram_text(caption)

def send_telegram_text(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": False}
    requests.post(url, json=payload, timeout=10)

def check_tweets():
    seen = load_seen()
    new_seen = set(seen)
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            # استخراج اسم الحساب من عنوان الـ RSS العام
            account_name = feed.feed.get.get("title", "تويتر") if hasattr(feed, 'feed') else "تويتر"
            
            for entry in feed.entries[:3]:
                if entry.id not in seen:
                    # تنظيف النص
                    soup = BeautifulSoup(entry.summary, "html.parser")
                    clean_text = soup.get_text()
                    
                    # محاولة البحث عن صورة مرفقة داخل التغريدة
                    img_tag = soup.find("img")
                    img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else None
                    
                    # محاولة استخراج اسم صاحب الحساب من عنوان التغريدة إذا وجد (مثل: Name on Twitter)
                    author = getattr(entry, 'author', 'حساب تويتر')
                    
                    message = f"🚨 <b>تغريدة جديدة</b>\n👤 <b>الحساب:</b> {author}\n\n💬 {clean_text}\n\n🔗 <a href='{entry.link}'>رابط التغريدة الأصلي</a>"
                    
                    if img_url:
                        send_telegram_media(message, img_url, entry.link)
                    else:
                        send_telegram_text(message)
                        
                    new_seen.add(entry.id)
        except Exception as e:
            print(f"Error parsing {feed_url}: {e}")
            
    save_seen(new_seen)

if __name__ == "__main__":
    check_tweets()
