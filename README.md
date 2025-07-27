# fastapi-login-shield

A simple FastAPI middleware to protect login endpoints from brute-force attacks.

## Features
- Exponential backoff delay on failed login attempts
- Ignores the first 3 failed attempts (no delay)
- Monitors only the specified login path
- No external dependencies or complex setup required

## Usage
```python
from fastapi import FastAPI
from your_module import LoginShieldMiddleware

app = FastAPI()
app.add_middleware(LoginShieldMiddleware, login_path="/login")
```
