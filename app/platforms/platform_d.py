from datetime import datetime, timezone
import re

import httpx

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class BlueskyPlatform(BasePlatform):
    name = "Bluesky"
    api_root = "https://bsky.social/xrpc"

    async def post(self, message: str) -> PlatformResult:
        if not settings.bluesky_handle:
            raise ValueError("BLUESKY_HANDLE is missing from .env.")

        if not settings.bluesky_app_password:
            raise ValueError("BLUESKY_APP_PASSWORD is missing from .env.")

        link_match = re.search(r"https?://\S+", message, re.IGNORECASE)
        if not link_match:
            raise ValueError("The message does not contain a link.")

        link = link_match.group(0).rstrip(".,!?;:)")
        link_start = message.find(link)
        byte_start = len(message[:link_start].encode("utf-8"))
        byte_end = byte_start + len(link.encode("utf-8"))

        async with httpx.AsyncClient(timeout=20.0) as client:
            session_response = await client.post(
                f"{self.api_root}/com.atproto.server.createSession",
                json={
                    "identifier": settings.bluesky_handle.lstrip("@"),
                    "password": settings.bluesky_app_password,
                },
            )

            if session_response.status_code >= 400:
                raise ValueError(
                    "Bluesky login failed. Check BLUESKY_HANDLE and "
                    "BLUESKY_APP_PASSWORD."
                )

            session = session_response.json()
            access_token = session["accessJwt"]
            account_did = session["did"]

            created_at = datetime.now(timezone.utc).isoformat().replace(
                "+00:00", "Z"
            )
            record_response = await client.post(
                f"{self.api_root}/com.atproto.repo.createRecord",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "repo": account_did,
                    "collection": "app.bsky.feed.post",
                    "record": {
                        "$type": "app.bsky.feed.post",
                        "text": message,
                        "createdAt": created_at,
                        "facets": [
                            {
                                "index": {
                                    "byteStart": byte_start,
                                    "byteEnd": byte_end,
                                },
                                "features": [
                                    {
                                        "$type": "app.bsky.richtext.facet#link",
                                        "uri": link,
                                    }
                                ],
                            }
                        ],
                    },
                },
            )

        if record_response.status_code >= 400:
            raise ValueError(
                f"Bluesky post failed with HTTP "
                f"{record_response.status_code}: "
                f"{record_response.text[:300]}"
            )

        post_record = record_response.json()
        post_key = post_record["uri"].rsplit("/", 1)[-1]
        handle = settings.bluesky_handle.lstrip("@")
        post_url = f"https://bsky.app/profile/{handle}/post/{post_key}"
        posted_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=post_url,
            public_access=True,
            date=posted_at.date().isoformat(),
            time=posted_at.time().replace(microsecond=0).isoformat(),
            error=None,
        )
