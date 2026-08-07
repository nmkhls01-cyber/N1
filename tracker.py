import os
import requests
from bs4نهارi import BeautifulSoup  # type: ignore
from bs4 import BeautifulSoup

# الحسابات اللي تريد تراقبها (تكدر تغيرها وتضيف أي حساب تريده)
ACCOUNTS = ["elonmusk", "__eventsMT"] 

# تم وضع معلومات البوت والآيدي مالك هنا مباشرة
TELEGRAM_TOKEN = "8947309767:AAEIIbEOKRt9COi2x7rdkNKhewmymZrKPaI"
CHAT_ID = "8925137681"
SEEN_FILE = "seen_tweets.txt"

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        for tweet_id in seen:
            f.write(f"{tweet_id}\n")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "disable_web_page_preview": False}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending telegram message: {e}")

def check_tweets():
    seen = load_seen()
    new_seen = set(seen)
    
    nitter_instance = "https://nitter.privacydev.net"

    for account in ACCOUNTS:
        url = f"{nitter_instance}/{account}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Could not reach account {account}")
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            timeline = soup.find_all("div", class_="timeline-item")
            
            for item in timeline[:3]:
                tweet_link = item.find("a", class_="tweet-link")
                if not tweet_link:
                    continue
                
                tweet_url_path = tweet_link.get("href", "")
                tweet_id = tweet_url_path.split("/")[-1]
                
                if tweet_id in seen:
                    continue
                
                tweet_content = item.find("div", class_="tweet-content")
                text = tweet_content.get_text() if tweet_content else "تغريدة جديدة بدون نص"
                
                full_tweet_url = f"https://twitter.com{tweet_url_path}"
                message = f"🚨 تغريدة جديدة من @{account}!\n\n{text}\n\n🔗 الرابط: {full_tweet_url}"
                
                send_telegram(message)
                new_seen.add(tweet_id)
                
        except Exception as e:
            print(f"Error checking {account}: {e}")
            
    save_seen(new_seen)

if __name__ == "__main__":
    check_tweets()
