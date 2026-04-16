import os

REQUIRED = [
    "TELEGRAM_BOT_TOKEN",
    "WEBHOOK_URL",
    "DATABASE_URL",
    "REDIS_URL",
    "POSTGRES_PASSWORD",
    "REDIS_PASSWORD",
]


def main() -> int:
    missing = [name for name in REQUIRED if not os.getenv(name)]
    if missing:
        print("Missing required env vars:")
        for name in missing:
            print(f"- {name}")
        return 1
    print("Environment variables look good.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
