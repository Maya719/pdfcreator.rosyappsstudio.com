from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
import os

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Verify the API key provided in the request headers.
    """
    expected_api_key = os.getenv("API_KEY")

    # If no API_KEY is configured in .env, we might want to skip validation or fail
    if not expected_api_key:
        return None

    if api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key",
        )
    print("API Key verified successfully")
    return api_key
