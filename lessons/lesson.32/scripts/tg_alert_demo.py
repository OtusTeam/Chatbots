import os

import httpx


def send_alert(text: str) -> dict:
    token = os.getenv("ALERT_BOT_TOKEN", "")
    chat_id = os.getenv("ALERT_CHAT_ID", "")
    if not token or not chat_id:
        raise RuntimeError("ALERT_BOT_TOKEN and ALERT_CHAT_ID are required")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = httpx.post(url, json=payload, timeout=10.0)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    data = send_alert("ALERT: bot latency is above threshold.")
    print(data.get("ok"), data.get("result", {}).get("message_id"))
