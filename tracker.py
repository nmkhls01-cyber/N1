import os
import requests
from bs4 import BeautifulSoup

# ==========================================
# إعدادات الأداة (15 حساباً)
# ==========================================
ACCOUNTS = [
    "Drb7h1",         # من الصورة الأولى
    "__eventsMT",     # من الصورة الثانية
    "SHoNGxBoNgYT",   # من الصورة الثالثة
    "AboKharba",      # من الصورة الرابعة
    "iiMonkey_D",     # من الصورة الخامسة
    "S5B_Q",          # من الصورة السادسة
    "user7",          # حساب فارغ (تكدر تغيره بأي وقت)
    "user8",          # حساب فارغ
    "user9",          # حساب فارغ
    "user10",         # حساب فارغ
    "user11",         # حساب فارغ
    "user12",         # حساب فارغ
    "user13",         # حساب فارغ
    "user14",         # حساب فارغ
    "user15"          # حساب فارغ
]

TELEGRAM_TOKEN = "8947309767:AAEIIbEOKRt9COi2x7rdkNKhewmymZrKPaI"
CHAT_ID = "8925137681"
SEEN_FILE = "seen_tweets.txt"

# ==========================================
# الوظائف البرمجية
# ==========================================

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
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending telegram message: {e}")

def check_tweets():
    print("Starting tweet check...")
    seen = load_seen()
    new_seen = set(seen)
    
    nitter_instance = "https://nitter.privacydev.net"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for account in ACCOUNTS:
        # تخطي الحسابات الوهمية التجريبية لكي لا تحدث أخطاء بحث
        if account.startswith("user") and account[4:].isdigit():
            continue

        print(f"Checking account: {account}...")
        url = f"{nitter_instance}/{account}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"Failed to reach Nitter for @{account}")
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            timeline = soup.find_all("div", class_="timeline-item")
            
            if not timeline:
                continue

            for item in timeline[:3]:
                tweet_link_element = item.find("a", class_="tweet-link")
                if not tweet_link_element:
                    continue
                
                tweet_url_path = tweet_link_element.get("href", "")
                tweet_id = tweet_url_path.split("/")[-1]
                
                if tweet_id in seen:
                    continue
                
                tweet_content = item.find("div", class_="tweet-content")
                text = tweet_content.get_text(separator='\n') if tweet_content else "تغريدة جديدة (بدون نص)"
                
                tweet_date = item.find("span", class_="tweet-date")
                date_text = tweet_date.find("a").get_text() if tweet_date and tweet_date.find("a") else "وقت غير معروف"

                full_tweet_url = f"https://twitter.com{tweet_url_path}"
                
                message_title = f"🚨 <b>تغريدة جديدة من @{account}</b>\n"
                message_date = f"📅 {date_text}\n\n"
                message_body = f"{text}\n\n"
                message_link = f"🔗 <a href='{full_tweet_url}'>مشاهدة التغريدة على X</a>"
                
                final_message = message_title + message_date + message_body + message_link
                
                print(f"New tweet found from @{account}! Sending notification...")
                send_telegram(final_message)
                new_seen.add(tweet_id)
                
        except Exception as e:
            print(f"Error checking account {account}: {e}")
            
    save_seen(new_seen)
    print("Tweet check finished.")

if __name__ == "__main__":
    check_tweets()
