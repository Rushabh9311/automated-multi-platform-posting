from datetime import datetime
import httpx

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class DevToPlatform(BasePlatform):
    name="DEV.to"

    async def post(self, message: str)->PlatformResult:
        if not settings.devto_api_key:
            raise ValueError("DEVTO_API_KEY is missing from .env.")

        headers={
            "api-key":settings.devto_api_key,
            "Accept":"application/vnd.forem.api-v1+json",
        }

        article_data={
            "article":{
                "title":"Automated posting update",
                "body_markdown":message,
                "published":True,
            }
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response=await client.post(
                "https://dev.to/api/articles",
                headers=headers,
                json=article_data,
            )

        if response.status_code>=400:
            raise ValueError(
                f"DEV.to returned HTTP {response.status_code}: "
                f"{response.text[:300]}"
            )

        article=response.json()
        posted_at=(
            article.get("published_at")
            or article.get("published_timestamp")
        )

        post_date=None
        post_time=None

        if posted_at:
            post_datetime=datetime.fromisoformat(
                posted_at.replace("Z", "+00:00")
            )
            post_date=post_datetime.date().isoformat()
            post_time=post_datetime.time().replace(
                microsecond=0
            ).isoformat()

        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=article.get("url"),
            public_access=True,
            date=post_date,
            time=post_time,
            error=None,
        )