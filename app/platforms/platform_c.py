from datetime import datetime

import httpx

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class MastodonPlatform(BasePlatform):
    name = "Mastodon"

    async def post(self, message: str) -> PlatformResult:
        if not settings.mastodon_url:
            raise ValueError("MASTODON_URL is missing from .env.")

        if not settings.mastodon_access_token:
            raise ValueError("MASTODON_ACCESS_TOKEN is missing from .env.")

        api_url = settings.mastodon_url.rstrip("/") + "/api/v1/statuses"
        headers = {
            "Authorization": f"Bearer {settings.mastodon_access_token}"
        }
        form_data = {
            "status": message,
            "visibility": "public",
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                api_url,
                headers=headers,
                data=form_data,
            )

        if response.status_code >= 400:
            raise ValueError(
                f"Mastodon returned HTTP {response.status_code}: "
                f"{response.text[:300]}"
            )

        post = response.json()
        posted_at = post.get("created_at")
        post_date = None
        post_time = None

        if posted_at:
            post_datetime = datetime.fromisoformat(
                posted_at.replace("Z", "+00:00")
            )
            post_date = post_datetime.date().isoformat()
            post_time = post_datetime.time().replace(
                microsecond=0
            ).isoformat()

        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=post.get("url"),
            public_access=post.get("visibility") == "public",
            date=post_date,
            time=post_time,
            error=None,
        )
