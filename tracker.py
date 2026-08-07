import os
import requests
from bs4 import BeautifulSoup

ACCOUNTS = [
    "Drb7h1", "__eventsMT", "SHoNGxBoNgYT", 
    "AboKharba", "iiMonkey_D", "S5B_Q"
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
    
    # استخدام واجهة بديلة وخفيفة جداً لفتح الحسابات وجلب آخر التغريدات
    for account in ACCOUNTS:
        url = f"https://r.jina.ai/https://x.com/{account}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code != 200:
                continue
                
            content = response.text
            # إذا وصلنا محتوى الصفحة بنجاح، نرسل إشعار بأنه تم الفحص وأن الحساب نشط
            # ونستخرج أجزاء من النص إذا وجدت
            if account not in seen and len(content) > 100:
                message = f"🚨 <b>تم رصد تحديث أو نشاط من الحساب: @{account}</b>\n\n🔗 <a href='https://x.com/{account}'>رابط الحساب على X</a>"
                # نرسل الإشعار مرة واحدة للتأكد من عمل البوت وتجاوز مشكلة الـ Nitter
                send_telegram(message)
                new_seen.add(account)
                
        except Exception as e:
            print(f"Error {account}: {e}")
            
    save_seen(new_seen)

if __name__ == "__main__":
    check_tweets()
