import os
import sys
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "talento_escucha.settings")

_error = None
_django_app = None

try:
    from django.core.wsgi import get_wsgi_application
    _django_app = get_wsgi_application()
except BaseException:
    _error = traceback.format_exc()


def app(environ, start_response):
    if _error or _django_app is None:
        body = ("DJANGO ERROR:\n" + (_error or "unknown")).encode("utf-8")
        start_response("200 OK", [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ])
        return [body]
    return _django_app(environ, start_response)


application = app



