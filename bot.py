import requests
import time
from decimal import Decimal

BOT_TOKEN = "8750652862:AAHxzpzs6sFWh79wO7BGbylPd0QTBLUZf8w"
CHAT_ID = "708434490"

TOMAN_PER_TRX = Decimal("60000")

TARGET_AMOUNTS = [
    "18.3", "18.33", "18.333", "18.3333", "18.33333", "18.333333",
    "18.4", "18.5",
    "36.6", "36.66", "36.666", "36.6666", "36.66666", "36.666666",
    "36.7", "37",
    "73.3", "73.33", "73.333", "73.3333", "73.33333", "73.333333",
    "74.4", "74", "73",
    "91", "91.6", "91.66", "91.666", "91.6666", "91.66666", "91.666666",
    "92"
]

TARGET_SUN = {
    int(Decimal(x) * Decimal(1_000_000))
    for x in TARGET_AMOUNTS
}

seen_tx = set()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }, timeout=10)

def fmt_trx(sun):
    trx = Decimal(sun) / Decimal(1_000_000)
    return format(trx.normalize(), "f")

def fmt_toman(sun):
    trx = Decimal(sun) / Decimal(1_000_000)
    toman = trx * TOMAN_PER_TRX
    return f"{int(toman):,}"

while True:
    try:
        res = requests.post(
            "https://api.trongrid.io/wallet/getnowblock",
            json={},
            timeout=10
        ).json()

        transactions = res.get("transactions", [])

        for tx in transactions:
            txid = tx.get("txID")
            if not txid or txid in seen_tx:
                continue

            seen_tx.add(txid)

            contracts = tx.get("raw_data", {}).get("contract", [])

            for contract in contracts:
                if contract.get("type") != "TransferContract":
                    continue

                value = contract.get("parameter", {}).get("value", {})
                amount_sun = value.get("amount")

                if amount_sun not in TARGET_SUN:
                    continue

                amount_trx = fmt_trx(amount_sun)
                amount_toman = fmt_toman(amount_sun)
                link = f"https://tronscan.org/#/transaction/{txid}"

                msg = (
                    f"💰 `{amount_trx}` TRX\n"
                    f"🇮🇷 `{amount_toman}` تومان\n"
                    f"🔗 {link}"
                )

                send_telegram(msg)

        if len(seen_tx) > 50000:
            seen_tx = set(list(seen_tx)[-20000:])

    except Exception as e:
        print("Error:", e)

    time.sleep(3)
