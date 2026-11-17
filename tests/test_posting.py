import unittest

from pydantic import ValidationError

from app.platforms.base import BasePlatform
from app.schemas import PlatformResult, PostingRequest
from app.services.posting_service import PostingService


class PostingRequestTests(unittest.TestCase):
    def test_accepts_one_valid_url(self):
        request = PostingRequest(
            message="Read about my project: https://example.com"
        )

        self.assertEqual(
            request.message,
            "Read about my project: https://example.com",
        )

    def test_rejects_message_longer_than_200_characters(self):
        with self.assertRaises(ValidationError):
            PostingRequest(message="a" * 201)

    def test_rejects_message_without_a_url(self):
        with self.assertRaises(ValidationError):
            PostingRequest(message="This message has no link.")

    def test_rejects_message_with_two_urls(self):
        with self.assertRaises(ValidationError):
            PostingRequest(
                message="First https://example.com, then https://example.org"
            )

    def test_rejects_malformed_url(self):
        with self.assertRaises(ValidationError):
            PostingRequest(message="This link is broken: https://")


class SuccessfulPlatform(BasePlatform):
    name = "Working example platform"

    async def post(self, message: str) -> PlatformResult:
        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url="https://example.com/post/1",
            public_access=True,
            date="2026-11-16",
            time="12:00:00",
        )


class FailingPlatform(BasePlatform):
    name = "Failing example platform"

    async def post(self, message: str) -> PlatformResult:
        raise RuntimeError("Example platform error")


class PostingServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_continues_after_a_platform_fails(self):
        service = PostingService(
            platforms=[FailingPlatform(), SuccessfulPlatform()]
        )

        response = await service.post_message(
            "Read about my project: https://example.com"
        )

        self.assertTrue(response.success)
        self.assertEqual(len(response.results), 2)
        self.assertEqual(response.results[0].status, "failed")
        self.assertEqual(response.results[0].error, "Example platform error")
        self.assertEqual(response.results[1].status, "success")

    async def test_overall_success_is_false_when_all_platforms_fail(self):
        service = PostingService(platforms=[FailingPlatform()])

        response = await service.post_message(
            "Read about my project: https://example.com"
        )

        self.assertFalse(response.success)
        self.assertEqual(response.results[0].status, "failed")


if __name__ == "__main__":
    unittest.main()
