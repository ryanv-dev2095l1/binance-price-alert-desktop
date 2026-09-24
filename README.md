# binance-price-alert-desktop

I got tired of leaving heavy trading tabs or resource-heavy Electron apps open just to watch price levels. This tool runs in the background, connects directly to the Binance WebSocket stream, and pops up native Windows toast notifications the moment a target is hit.

It is written specifically for Windows and consumes minimal resources.

## Installation

Clone the repository and install the dependencies. I recommend using a virtual environment.

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

You can pass targets directly as command-line arguments. Each target is a ticker symbol followed by a comparison operator and the price.

```cmd
python alert.py BTCUSDT>96500 ETHUSDT<3120 SOLUSDT>=185.5
```

Alternatively, you can save your targets to a file if you have a long list. Create a plain text file, say `targets.txt`, with one rule per line:

```text
BTCUSDT > 96500
ETHUSDT <= 3120
SOLUSDT >= 185.5
```

Then run the script pointing to that file:

```cmd
python alert.py --config targets.txt
```

When an alert triggers, the Windows notification includes a direct link. Clicking it opens the pair's trading page in your default browser.

<!-- checked: 2026-09-24 -->
