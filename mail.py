import requests
from bs4 import BeautifulSoup
from telegram import Bot
import time
from datetime import datetime

# Telegraminställningar
bot = Bot(token="8272597801:AAHn4BwQAs4NML9mghMi0-PGISZ74aN8f7A")
chat_id = 7303573292  # Ditt privata Telegram-ID

# Wallets att tracka
wallets = {
    "Cupseyy": "https://pump.fun/profile/suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK?tab=balances",
    "Cya": "https://pump.fun/profile/CyaE1VxvBrahnPWkqm5VsdCvyS2QmNht2UFrKJHga54o?tab=balances",
    "7VBT": "https://pump.fun/profile/7VBTpiiEjkwRbRGHJFUz6o5fWuhPFtAmy8JGhNqwHNnn?tab=balances",
    "BNahnx": "https://pump.fun/profile/BNahnx13rLru9zxuWNGBD7vVv1pGQXB11Q7qeTyupdWf?tab=balances"
}

wallet_history = {name: set() for name in wallets}

def log_to_file(wallet_name, message):
    filename = f"{wallet_name.lower()}_logg.txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def get_coin_creation_date(coin_name):
    search_url = f"https://pump.fun/search?q={coin_name}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")
    date_tag = soup.find(string=lambda t: t and "Created" in t)
    if date_tag:
        return date_tag.strip()
    return "okänd tidpunkt"

def check_wallet(wallet_name, wallet_url):
    print(f"🔄 Kollar {wallet_name}...")

    response = requests.get(wallet_url)
    if response.status_code != 200:
        print(f"❌ Kunde inte hämta {wallet_name}. Statuskod: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    coin_blocks = soup.find_all("div", string=lambda text: text and " " in text and text.strip().isupper())

    new_coins = []

    for block in coin_blocks:
        coin_name = block.text.strip()
        parent = block.find_parent()
        if not parent:
            continue

        mc_tag = parent.find_next(string=lambda t: t and "MC $" in t)
        change_tag = parent.find_next(string=lambda t: t and "%" in t)

        market_cap = mc_tag.strip().replace("MC $", "") if mc_tag else "okänd"
        change = change_tag.strip() if change_tag else "?"

        if coin_name not in wallet_history[wallet_name]:
            wallet_history[wallet_name].add(coin_name)
            creation_date = get_coin_creation_date(coin_name)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            message = (
                f"🛒 {wallet_name} köpte nytt coin: {coin_name}\n"
                f"💰 Marknadsvärde: ${market_cap}\n"
                f"📈 Prisändring: {change}\n"
                f"🕒 Upptäckt: {timestamp}\n"
                f"🧬 Skapades: {creation_date}\n"
                f"🔗 [Se på Pump.fun](https://pump.fun/search?q={coin_name})"
            )
            bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
            print(f"✅ {wallet_name}: skickade notis för {coin_name}")
            log_to_file(wallet_name, f"{coin_name} | MC ${market_cap} | Ändring: {change} | Skapades: {creation_date} | Upptäckt: {timestamp}")
    else:
        print(f"📭 {wallet_name}: inga nya coins hittades.")

# Starta loopen
print("✅ Scriptet är igång och trackar alla wallets!")

while True:
    for name, url in wallets.items():
        check_wallet(name, url)
    time.sleep(30)
