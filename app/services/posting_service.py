from typing import List

from app.platforms.base import BasePlatform
from app.schemas import PlatformResult, PostingResponse


class PostingService:
    def __init__(self, platforms:List[BasePlatform]):
        self.platforms=platforms

    async def post_message(self, message:str) -> PostingResponse:
        results=[]

        for platform in self.platforms:
            try:
                result=await platform.post(message)
            except Exception as error:
                result=PlatformResult(
                    platform=platform.name,
                    status="failed",
                    public_access=False,
                    error=str(error),
                )

            results.append(result)

        any_succeeded=any(
            result.status=="success"
            for result in results
        )

        return PostingResponse(
            success=any_succeeded,
            results=results,
        )