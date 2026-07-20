import hashlib
import hmac

from app.core.exceptions import InvalidSignatureError


def verify_github_signature(payload_body: bytes, signature_header: str | None, secret: str) -> None:
    """
    Raises InvalidSignatureError unless signature_header is a valid
    HMAC-SHA256 signature of payload_body under `secret`, matching what
    GitHub sends in the X-Hub-Signature-256 header.

    Must be checked against the raw request bytes, not the parsed JSON —
    re-serializing JSON can change whitespace/key order and break the
    signature even for a genuine request.
    """
    if not signature_header or not signature_header.startswith("sha256="):
        raise InvalidSignatureError()

    expected = hmac.new(secret.encode(), payload_body, hashlib.sha256).hexdigest()
    provided = signature_header.removeprefix("sha256=")

    # hmac.compare_digest instead of `==` — a naive string comparison leaks
    # timing information about how many leading bytes matched, which an
    # attacker can use to guess the correct signature byte by byte.
    if not hmac.compare_digest(expected, provided):
        raise InvalidSignatureError()
