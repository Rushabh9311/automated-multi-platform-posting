from datetime import datetime, timezone

import httpx

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class TelegramPlatform(BasePlatform):
    name="Telegram"

    async def post(self, message: str)->PlatformResult:
        if not settings.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is missing from .env.")

        channel=settings.telegram_channel

        if not channel or not channel.startswith("@"):
            raise ValueError(
                "TELEGRAM_CHANNEL must be a public channel name, "
                "for example @mychannel."
            )

        api_url=(
            "https://api.telegram.org/bot"
            f"{settings.telegram_bot_token}/sendMessage"
        )

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response=await client.post(
                    api_url,
                    json={"chat_id": channel, "text": message},
                )
                result=response.json()
        except httpx.HTTPError as error:
            raise ValueError("Could not connect to Telegram.") from error

        if not result.get("ok"):
            raise ValueError(
                f"Telegram error:{result.get('description', 'Unknown error')}"
            )

        sent_message=result["result"]
        message_id=sent_message["message_id"]

        channel_name=channel.lstrip("@")
        posted_url=f"https://t.me/{channel_name}/{message_id}"

        posted_at=datetime.fromtimestamp(
            sent_message["date"],
            tz=timezone.utc,
        )

        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=True,
            date=posted_at.date().isoformat(),
            time=posted_at.time().replace(microsecond=0).isoformat(),
            error=None,
        )