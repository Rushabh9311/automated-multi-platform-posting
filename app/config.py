import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    mastodon_url=os.getenv("MASTODON_URL")
    mastodon_access_token=os.getenv("MASTODON_ACCESS_TOKEN")

    bluesky_handle=os.getenv("BLUESKY_HANDLE")
    bluesky_app_password=os.getenv("BLUESKY_APP_PASSWORD")

    devto_api_key=os.getenv("DEVTO_API_KEY")

    github_token=os.getenv("GITHUB_TOKEN")

    telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_channel=os.getenv("TELEGRAM_CHANNEL")


settings = Settings()
