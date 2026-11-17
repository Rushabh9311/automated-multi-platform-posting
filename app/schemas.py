import re
from urllib.parse import urlsplit

from pydantic import BaseModel,field_validator

from typing import List,Literal,Optional

class PostingRequest(BaseModel):
    message:str

    @field_validator("message")
    @classmethod
    def validate_message(cls,message):
        if len(message)>200:
            raise ValueError("Message must be 200 characters or fewer.")

        links=re.findall(r"https?://\S+",message)

        if len(links)!=1:
            raise ValueError("Message must contain exactly one URL.")

        link=links[0].rstrip(".,!?;:)")
        parts=urlsplit(link)

        if parts.scheme not in ("http", "https") or not parts.hostname: raise ValueError("Please include a valid HTTP or HTTPS URL.")
        return message

class PlatformResult(BaseModel):
    platform:str
    status:Literal["success", "failed"]
    posted_url:Optional[str]=None
    public_access:bool
    date:Optional[str]=None
    time:Optional[str]=None
    error:Optional[str]=None

class PostingResponse(BaseModel):
    success:bool
    results:List[PlatformResult]
