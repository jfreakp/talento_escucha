import os
import sys
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "talento_escucha.settings")

_startup_error = None

try:
    from django.core.wsgi import get_wsgi_application
    _django_app = get_wsgi_application()
except Exception:
    _startup_error = traceback.format_exc()
    print("VERCEL_STARTUP_ERROR:\n" + _startup_error, file=sys.stderr, flush=True)
    _django_app = None


def app(environ, start_response):
    if _startup_error or _django_app is None:
        body = ("Django startup failed:\n" + (_startup_error or "unknown")).encode()
        start_response("200 OK", [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ])
        return [body]
    return _django_app(environ, start_response)


application = app

