import argparse
import asyncio
import re
import sys
from price_alert.stream import BinanceStream
from price_alert.toast import display_toast

def main():
    parser = argparse.ArgumentParser(description="Binance Price Alert CLI")
    parser.add_argument("alerts", nargs="+", help="Alerts (e.g. BTCUSDT>60000)")
    args = parser.parse_args()

    symbols = []
    for arg in args.alerts:
        match = re.match(r"^([A-Z]+)([<>])([0-9.]+)$", arg.upper())
        if not match:
            print(f"Bad format: {arg}", file=sys.stderr)
            sys.exit(1)
        symbols.append(match.group(1))

    print(f"Monitoring {symbols}")

if __name__ == "__main__":
    main()
