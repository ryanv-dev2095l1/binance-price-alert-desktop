import asyncio
import json
import websockets

class BinanceStream:
    def __init__(self, symbols):
        self.symbols = [s.lower() for s in symbols]
        self.url = self._build_url()

    def _build_url(self):
        streams = "/".join(f"{s}@ticker" for s in self.symbols)
        return f"wss://stream.binance.com:9443/stream?streams={streams}"

    async def listen(self, queue):
        async with websockets.connect(self.url) as ws:
            while True:
                message = await ws.recv()
                data = json.loads(message)
                if "data" in data:
                    payload = data["data"]
                    ticker = {
                        "symbol": payload["s"],
                        "price": float(payload["c"])
                    }
                    await queue.put(ticker)
