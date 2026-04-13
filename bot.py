import requests
import time

BOT_TOKEN = "8750652862:AAHxzpzs6sFWh79wO7BGbylPd0QTBLUZf8w"
CHAT_IDS = ["708434490", "539669812", "5249213540"]
ADDRESS = "TFYRnxcDAtVQgUjtbZQHGSLP2qgbkt2Zg1"

seen_tx = set()

TOMAN_PER_TRX = 1_000_000 / 19.6

def round_toman(amount):
    s = f"{amount:.0f}"
    digits = len(s)
    if digits == 7:
        return s[:2] + "0" * 5
    elif digits == 8:
        return s[:3] + "0" * 5
    else:
        return s

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        requests.post(url, data={
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "Markdown"
        })

while True:
    url = f"https://api.trongrid.io/v1/accounts/{ADDRESS}/transactions"
    res = requests.get(url).json()
    for tx in res.get("data", []):
        txid = tx["txID"]
        if txid not in seen_tx:
            try:
                contract = tx["raw_data"]["contract"][0]
                contract_type = contract["type"]
                if contract_type != "TransferContract":
                    continue
                seen_tx.add(txid)
                value = contract["parameter"]["value"]["amount"]
                amount_trx = value / 1_000_000
                amount_toman = amount_trx * TOMAN_PER_TRX
                toman_str = round_toman(amount_toman)
                link = f"https://tronscan.org/#/transaction/{txid}"
                msg = (
                    f"💰 {amount_trx:.2f} TRX\n"
                    f"🇮🇷 `{toman_str}` تومان\n"
                    f"🔗 {link}"
                )
                send_telegram(msg)
            except:
                pass
    time.sleep(4)
