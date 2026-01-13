#!/usr/bin/env python3
"""
Quick connectivity test for Ortensia central server.

- Connects to ws://172.25.32.1:8765
- Sends a REGISTER message
- Waits for REGISTER_ACK
"""

import asyncio
import json
import os
import time
import sys


DEFAULT_URI = "ws://172.25.32.1:8765"


async def main() -> int:
    uri = os.environ.get("ORTENSIA_SERVER", DEFAULT_URI)
    client_id = f"debug-connect-{int(time.time())}"

    try:
        import websockets  # type: ignore
    except Exception as e:
        print("❌ Python 缺少 websockets 库，无法测试。")
        print("   解决：pip install websockets")
        print(f"   详细错误: {e}")
        return 2

    print(f"🔗 Connecting: {uri}")
    t0 = time.time()

    try:
        async with websockets.connect(uri, open_timeout=3, close_timeout=1) as ws:
            t1 = time.time()
            print(f"✅ Connected in {int((t1 - t0) * 1000)} ms")

            register_msg = {
                "type": "register",
                "from": client_id,
                "to": "server",
                "timestamp": int(time.time()),
                "payload": {
                    "client_types": ["command_client"],
                    "platform": sys.platform,
                    "pid": os.getpid(),
                },
            }
            await ws.send(json.dumps(register_msg, ensure_ascii=False))
            print("📤 Sent REGISTER")

            ack = await asyncio.wait_for(ws.recv(), timeout=3)
            dt = int((time.time() - t1) * 1000)
            print(f"📨 Received in {dt} ms: {ack}")

            # minimal validation
            try:
                data = json.loads(ack)
                ok = data.get("type") == "register_ack" and data.get("payload", {}).get("success") is True
                print("✅ REGISTER_ACK OK" if ok else "⚠️ Unexpected ACK payload")
            except Exception:
                print("⚠️ ACK is not JSON")

            return 0

    except Exception as e:
        dt = int((time.time() - t0) * 1000)
        print(f"❌ Failed after {dt} ms: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

