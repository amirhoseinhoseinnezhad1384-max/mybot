import requests
import time
from decimal import Decimal

BOT_TOKEN = "توکن قبلی خودت"

CHAT_IDS = [
    "708434490",
    "5249213540",
    "539669812"
]

TOMAN_PER_TRX = Decimal("60000")

TARGET_AMOUNTS = [
    "18.3",
    "18.33",
    "18.333",
    "18.3333",
    "18.33333",
    "18.333333",
    "18.4",
    "18.5",

    "36.6",
    "36.66",
    "36.666",
    "36.6666",
    "36.66666",
    "36.666666",
    "36.7",
    "37",

    "73.3",
    "73.33",
    "73.333",
    "73.3333",
    "73.33333",
    "73.333333",
    "74.4",
    "74",
    "73",

    "91",
    "91.6",
    "91.66",
    "91.666",
    "91.6666",
    "91.66666",
    "91.666666",
    "92"
]

TARGET_SUN = {
    int(Decimal(x) * Decimal("1000000"))
    for x in TARGET_AMOUNTS
}

seen_tx = set()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    for chat_id in CHAT_IDS:
        try:
            requests.post(
                url,
                data={
                    "chat_id": chat_id,
                    "text": msg,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True
                },
                timeout=10
            )

        except Exception as e:
            print("Telegram Error:", e)

def get_latest_block_number():
    res = requests.get(
        "https://api.trongrid.io/wallet/getnowblock",
        timeout=10
    ).json()

    return res["block_header"]["raw_data"]["number"]

def get_block_by_number(block_number):
    res = requests.post(
        "https://api.trongrid.io/wallet/getblockbynum",
        json={"num": block_number},
        timeout=10
    ).json()

    return res

def fmt_trx(amount_sun):
    trx = Decimal(amount_sun) / Decimal("1000000")
    return format(trx.normalize(), "f")

def fmt_toman(amount_sun):
    trx = Decimal(amount_sun) / Decimal("1000000")
    toman = trx * TOMAN_PER_TRX
    return f"{int(toman):,}"

def process_transaction(tx, block_number):
    txid = tx.get("txID")

    if not txid or txid in seen_tx:
        return

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
            f"🚨 تراکنش پیدا شد\n\n"
            f"💰 `{amount_trx}` TRX\n"
            f"🇮🇷 `{amount_toman}` تومان\n"
            f"🧱 Block: `{block_number}`\n"
            f"🔗 {link}"
        )

        print("FOUND:", amount_trx, "TRX")

        send_telegram(msg)

def main():

    latest = get_latest_block_number()
    current_block = latest

    print("Start from block:", current_block)

    while True:

        try:

            latest_block = get_latest_block_number()

            while current_block <= latest_block:

                while True:
                    try:
                        block = get_block_by_number(current_block)
                        break

                    except Exception as e:
                        print("Retry block:", current_block, e)
                        time.sleep(2)

                transactions = block.get("transactions", [])

                for tx in transactions:
                    process_transaction(tx, current_block)

                print("Checked block:", current_block)

                current_block += 1

                time.sleep(0.2)

            if len(seen_tx) > 100000:
                seen_tx.clear()

            time.sleep(1)

        except Exception as e:

            print("Main Error:", e)

            time.sleep(5)

main()
