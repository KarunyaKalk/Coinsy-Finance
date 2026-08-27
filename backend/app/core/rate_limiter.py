import time
from typing import Dict, List
from fastapi import Request, HTTPException, status

class LLMRateLimiter:
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}

    def check_rate_limit(self, client_identifier: str):
        now = time.time()
        timestamps = self.requests.get(client_identifier, [])

        # Filter out timestamps older than window
        timestamps = [t for t in timestamps if now - t < self.window_seconds]

        if len(timestamps) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.max_requests} LLM requests per {self.window_seconds} seconds."
            )

        timestamps.append(now)
        self.requests[client_identifier] = timestamps


rate_limiter = LLMRateLimiter(max_requests=30, window_seconds=60)


def verify_llm_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    rate_limiter.check_rate_limit(client_ip)
