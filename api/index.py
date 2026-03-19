import os
import sys


def app(environ, start_response):
    """Minimal handler to verify Vercel Python runtime works."""
    body = b"Vercel Python runtime OK"
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(body))),
    ])
    return [body]


application = app


