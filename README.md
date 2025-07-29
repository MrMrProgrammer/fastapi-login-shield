# fastapi-login-shield

A simple and lightweight middleware to protect your FastAPI login endpoints from brute-force attacks using per-IP rate limiting with exponential backoff.

## Features

- Per-IP login attempt tracking
- Exponential backoff for repeated failed attempts
- Auto-expiry of old IP data (default: 15 minutes)
- Non-intrusive integration via Starlette middleware
- Customizable login path and expiration timeout

## Installation

```bash
pip install fastapi-login-shield
```

## Usage

### 1. Add the middleware to your FastAPI app

```python
from fastapi import FastAPI
from fastapi_login_shield.middleware import LoginShieldMiddleware

app = FastAPI()

# Add the middleware
app.add_middleware(LoginShieldMiddleware, login_path="/login")
```

### 2. Example login endpoint

```python
from fastapi import HTTPException, Request

@app.post("/login")
async def login(request: Request):
    # Simulate authentication logic
    form = await request.json()
    username = form.get("username")
    password = form.get("password")

    if username != "admin" or password != "secret":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful!"}
```

## How It Works

- The middleware intercepts all requests to the specified login path.
- If the response is a failed login (`401` or `403`), it increments the attempt counter for the client IP.
- If the count exceeds a threshold (e.g., 3), it applies an exponential delay (`2^count` seconds, up to 10 minutes).
- If a login succeeds (`2xx` response), the counter for that IP is reset.
- IPs are automatically cleaned from memory if inactive for a configurable duration (default: 900 seconds).

## Configuration

You can customize the login path and expiration time like this:

```python
app.add_middleware(
    LoginShieldMiddleware,
    login_path="/auth/login",
    expire_seconds=600  # expire IP data after 10 minutes
)
```

## Security Notes

- This middleware does not block login attempts permanently, it only applies temporary delays.

## License

MIT License

## Author

[Developed by MrMrProgrammer (Seyed Mohammadreza Hashemi)](https://mrmrprogrammer.ir)
