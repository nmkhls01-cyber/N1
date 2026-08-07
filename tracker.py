import os
import requests
from bs4 import BeautifulSoup

ACCOUNTS = [
    "Drb7h1", "__eventsMT", "SHoNGxBoNgYT", 
    "AboKharba", "iiMonkey_D", "S5B_Q", "ASwe7l"
]

TELEGRAM_TOKEN = "8947309767:AAEIIbEOKRt9COi2x7rdkNKhewmymZrKPaI"
CHAT_ID = "8925137681"
SEEN_FILE = "seen_tweets.txt"

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    try:
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f)
    except Exception:
        return set()

def save_seen(seen):
    try:
        with open(SEEN_FILE, "w") as f:
            for tweet_id in seen:
                f.write(f"{tweet_id}\n")
    except Exception as e:
        print(f"Error saving seen file: {e}")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error: {e}")

def check_tweets():
    seen = load_seen()
    new_seen = set(seen)
    
    for account in ACCOUNTS:
        url = f"https://nitter.poast.org/{account}/rss"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, "xml")
            items = soup.find_all("item")
            
            if not items:
                continue

            # فحص آخر 3 تغريدات
            for item in items[:3]:
                link = item.find("link")
                title = item.find("title")
                
                if not link:
                    continue
                
                tweet_link = link.text
                tweet_id = tweet_link.split("/")[-1] # استخراج معرف التغريدة الفريد
                
                # إذا كانت التغريدة مرسلة مسبقاً، تخاطها
                if tweet_id in seen:
                    continue
                
                tweet_title = title.text if title else "تغريدة جديدة"
                
                message = f"🚨 <b>تغريدة جديدة من @{account}</b>\n\n{tweet_title}\n\n🔗 <a href='{tweet_link}'>رابط التغريدة</a>"
                
                send_telegram(message)
                new_seen.add(tweet_id)
                
        except Exception as e:
            print(f"Error {account}: {e}")
            
    save_seen(new_seen)

if __name__ == "__main__":
    check_tweets()
