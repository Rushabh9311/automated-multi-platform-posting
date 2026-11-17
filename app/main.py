from fastapi import FastAPI

from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import PostingService
from app.platforms.platform_a import DevToPlatform
from app.platforms.platform_b import TelegramPlatform
from app.platforms.platform_c import MastodonPlatform
from app.platforms.platform_d import BlueskyPlatform
from app.platforms.platform_e import GitHubGistPlatform

app = FastAPI(title="Automated Posting API")
posting_service = PostingService(
    platforms=[
        DevToPlatform(),
        TelegramPlatform(),
        MastodonPlatform(),
        BlueskyPlatform(),
        GitHubGistPlatform(),
    ]
)


@app.get("/")
async def home():
    return {"message": "Automated Posting API is running"}


@app.post("/posting", response_model=PostingResponse)
async def create_posting(request: PostingRequest):
    return await posting_service.post_message(request.message)
