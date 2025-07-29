import asyncio
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.client.host
    return ip


class LoginShieldMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        login_path: str = "/login",
        expire_seconds: int = 900
    ):
        super().__init__(app)
        self.login_path = login_path
        self.expire_seconds = expire_seconds
        self.ip_attempts = {}
        self.ip_attempts_lock = asyncio.Lock()

    def get_delay(self, count: int) -> int:
        return min(2 ** count, 600)

    async def dispatch(self, request: Request, call_next):
        if request.url.path != self.login_path:
            return await call_next(request)

        ip = get_client_ip(request)
        now = time.time()

        async with self.ip_attempts_lock:
            self.ip_attempts = {
                ip_key: info
                for ip_key, info in self.ip_attempts.items()
                if now - info["last_ts"] < self.expire_seconds
            }

            info = self.ip_attempts.get(ip, {"count": 0, "last_ts": 0})

            if info["count"] >= 3:
                delay = self.get_delay(info["count"])
                remaining_delay = delay - (now - info["last_ts"])
                if remaining_delay > 0:
                    retry_after = max(1, int(remaining_delay))
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": (
                                "Too many login attempts. Try again in "
                                f"{retry_after} seconds."
                            )
                        },
                        headers={"Retry-After": str(retry_after)},
                    )

        response = await call_next(request)

        async with self.ip_attempts_lock:
            if 200 <= response.status_code < 300:
                self.ip_attempts.pop(ip, None)
            elif response.status_code in (401, 403):
                info = self.ip_attempts.setdefault(
                    ip,
                    {
                        "count": 0,
                        "last_ts": 0
                    }
                )
                info["count"] += 1
                info["last_ts"] = time.time()

        return response
