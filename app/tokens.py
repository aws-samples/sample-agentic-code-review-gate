"""API token handling.

Tokens are compared in constant time and never written to logs in full. The
``describe_token`` helper is the only sanctioned way to put a token into a log
line or an error message.
"""

from __future__ import annotations

import hmac
import logging

log = logging.getLogger(__name__)

_VISIBLE_PREFIX = 4


def describe_token(token: str) -> str:
    """Return a log-safe description of ``token``: prefix plus length only."""
    if not token:
        return "<empty token>"
    return f"{token[:_VISIBLE_PREFIX]}…(len={len(token)})"


def verify_token(presented: str, expected: str) -> bool:
    """Constant-time comparison; logs only the redacted form on failure."""
    ok = hmac.compare_digest(presented.encode("utf-8"), expected.encode("utf-8"))
    if not ok:
        log.warning("token rejected: %s", describe_token(presented))
    return ok
