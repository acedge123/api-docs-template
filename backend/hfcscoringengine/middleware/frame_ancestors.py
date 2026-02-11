"""CSP frame-ancestors middleware.

Goal: allow embedding (iframes) ONLY from https://www.vectorscore.io.

Notes:
- X-Frame-Options cannot express an allowlist beyond SAMEORIGIN, so we use CSP.
- We set X_FRAME_OPTIONS=None and remove XFrameOptionsMiddleware to avoid conflicting headers.
- This applies site-wide; scope to specific paths if you want (e.g. only /admin/).
"""

from __future__ import annotations


ALLOWED_FRAME_ANCESTORS = "'self' https://www.vectorscore.io"


class CSPFrameAncestorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Preserve an existing policy if present; just ensure frame-ancestors is set.
        existing = response.headers.get("Content-Security-Policy")
        if existing:
            # If a policy already sets frame-ancestors, leave it alone.
            if "frame-ancestors" in existing:
                return response
            response.headers[
                "Content-Security-Policy"
            ] = f"{existing.rstrip(';')}; frame-ancestors {ALLOWED_FRAME_ANCESTORS}"
            return response

        response.headers[
            "Content-Security-Policy"
        ] = f"frame-ancestors {ALLOWED_FRAME_ANCESTORS}"
        return response
