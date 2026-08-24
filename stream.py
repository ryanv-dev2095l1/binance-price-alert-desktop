import asyncio
import json
import websockets

# FIXME: binance sometimes sends empty streams if symbol is misspelled. we don't validate symbols upfront.

class BinanceStream:
    def __init__(self, symbols):
        self.symbols = [s.lower() for s in symbols]
        self.url = self._build_url()

    def _build_url(self):
        streams = "/".join(f"{s}@ticker" for s in self.symbols)
        return f"wss://stream.binance.com:9443/stream?streams={streams}"

    async def listen(self, queue):
        """
        Connects to the Binance websocket endpoint and streams price ticks to our internal queue.
        Handles drops gracefully with a backoff delay.
        """
        backoff = 1
        while True:
            try:
                async with websockets.connect(self.url) as ws:
                    backoff = 1
                    while True:
                        message = await ws.recv()
                        # print(f"DEBUG: raw payload: {message}")
                        try:
                            data = json.loads(message)
                        except json.JSONDecodeError:
                            continue

                        if "data" in data:
                            payload = data["data"]
                            ticker = {
                                "symbol": payload["s"],
                                "price": float(payload["c"])
                            }
                            await queue.put(ticker)
            except (websockets.exceptions.ConnectionClosed, OSError):
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)
