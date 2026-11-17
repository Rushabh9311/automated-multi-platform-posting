from app.schemas import PlatformResult

class BasePlatform:
    name="Unnamed platform"

    async def post(self,message:str)-> PlatformResult:
         raise NotImplementedError("Each platform must implement post()")

