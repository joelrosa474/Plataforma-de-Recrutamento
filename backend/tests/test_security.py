import unittest

from src.infrastructure.security.rate_limiter import AuthRateLimiter


class TestSecurity(unittest.TestCase):
    def test_rate_limiter_blocks_after_limit(self):
        limiter = AuthRateLimiter(max_attempts=2, window_seconds=60)
        key = "127.0.0.1"

        self.assertTrue(limiter.allow(key))
        self.assertTrue(limiter.allow(key))
        self.assertFalse(limiter.allow(key))


if __name__ == "__main__":
    unittest.main()
