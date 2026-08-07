import os
import requests
from bs4 import BeautifulSoup

ACCOUNTS = [
    "Drb7h1", "__eventsMT", "SHoNGxBoNgYT", 
    "AboKharba", "iiMonkey_D", "S5B_Q"
]

TELEGRAM_TOKEN = "8947309767:AAEIIbEOKRt9COi2x7rdkNKhewmymZrKPaI"
CHAT_ID = "8925137681"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error: {e}")

def check_tweets():
    # استخدام نسخة Nitter بديلة ومستقرة
    nitter_instance = "https://nitter.lucabased.xyz"
    headers = {"User-Agent": "Mozilla/5.0"}

    for account in ACCOUNTS:
        url = f"{nitter_instance}/{account}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            timeline = soup.find_all("div", class_="timeline-item")
            
            if not timeline:
                continue

            # فحص أحدث تغريدة فقط
            item = timeline[0]
            tweet_link = item.find("a", class_="tweet-link")
            if not tweet_link:
                continue
            
            tweet_url_path = tweet_link.get("href", "")
            tweet_id = tweet_url_path.split("/")[-1]
            
            tweet_content = item.find("div", class_="tweet-content")
            text = tweet_content.get_text(separator='\n') if tweet_content else "تغريدة جديدة"
            
            full_tweet_url = f"https://twitter.com{tweet_url_path}"
            
            message = f"🚨 <b>تغريدة جديدة من @{account}</b>\n\n{text}\n\n🔗 <a href='{full_tweet_url}'>رابط التغريدة</a>"
            
            # للإرسال المباشر
            send_telegram(message)
            break # يرسل أحدث تغريدة ويوقف حتى ما يكرر
                
        except Exception as e:
            print(f"Error {account}: {e}")

if __name__ == "__main__":
    check_tweets()
