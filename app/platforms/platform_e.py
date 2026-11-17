from datetime import datetime

import httpx

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class GitHubGistPlatform(BasePlatform):
    name = "GitHub Gist"

    async def post(self, message: str) -> PlatformResult:
        if not settings.github_token:
            raise ValueError("GITHUB_TOKEN is missing from .env.")

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {settings.github_token}",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "automated-multi-platform-posting",
        }
        gist_data = {
            "description": "Automated posting update",
            "public": True,
            "files": {
                "automated-post.md": {
                    "content": message,
                }
            },
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                "https://api.github.com/gists",
                headers=headers,
                json=gist_data,
            )

        if response.status_code >= 400:
            raise ValueError(
                f"GitHub returned HTTP {response.status_code}: "
                f"{response.text[:300]}"
            )

        gist = response.json()
        created_at = gist.get("created_at")
        post_date = None
        post_time = None

        if created_at:
            post_datetime = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            )
            post_date = post_datetime.date().isoformat()
            post_time = post_datetime.time().replace(
                microsecond=0
            ).isoformat()

        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=gist.get("html_url"),
            public_access=gist.get("public") is True,
            date=post_date,
            time=post_time,
            error=None,
        )
