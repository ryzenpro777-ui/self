import os
import asyncio
import json
import platform
import websockets

token = os.getenv("TOKEN")
seq = None
heartbeat_task = None


async def heartbeat(ws, interval):
    while True:
        await asyncio.sleep(interval / 1000)
        await ws.send(json.dumps({"op": 1, "d": seq}))


async def run():
    global seq, heartbeat_task

    uri = "wss://gateway.discord.gg/?v=10&encoding=json"

    async with websockets.connect(uri) as ws:
        hello = json.loads(await ws.recv())

        if hello["op"] == 10:
            heartbeat_task = asyncio.create_task(
                heartbeat(ws, hello["d"]["heartbeat_interval"])
            )

        await ws.send(json.dumps({
            "op": 2,
            "d": {
                "token": token,
                "properties": {
                    "os": platform.system().lower(),
                    "browser": "Discord VR",
                    "device": "Discord VR"
                },
                "presence": {
                    "status": "online",
                    "afk": False
                }
            }
        }))

        async for raw in ws:
            p = json.loads(raw)
            if p.get("s"):
                seq = p["s"]


async def main():
    while True:
        try:
            await run()
        except Exception:
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
