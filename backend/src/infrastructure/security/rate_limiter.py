import time
from threading import Lock


class AuthRateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts = {}
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            bucket = self._attempts.setdefault(key, [])
            bucket[:] = [stamp for stamp in bucket if now - stamp < self.window_seconds]

            if len(bucket) >= self.max_attempts:
                return False

            bucket.append(now)
            return True
