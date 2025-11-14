import os
import hmac
import hashlib



def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature"""
    secret = os.getenv("WEBHOOK_SECRET", "default_secret")
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


