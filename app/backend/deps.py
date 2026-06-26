from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict

security = HTTPBearer(auto_error=False)

# Very small auth stub. For real apps replace this with your auth provider.
# Behavior:
# - If a valid Authorization header is provided (any value), current_user will contain that token as username.
# - Otherwise returns a default demo user for convenience in development.

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    if credentials and credentials.credentials:
        # Treat the token as a username for the stub
        return {"id": credentials.credentials, "username": credentials.credentials}
    # fallback demo user
    return {"id": "demo-user", "username": "demo"}
