import os
import sys
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "talento_escucha.settings")

_error = None
_django_app = None
_steps = []

try:
    _steps.append("importing Django")
    import django
    _steps.append(f"Django {django.__version__} imported")

    _steps.append("loading settings")
    from django.conf import settings
    _ = settings.DEBUG  # force settings load
    _steps.append("settings loaded")

    _steps.append("calling get_wsgi_application")
    from django.core.wsgi import get_wsgi_application
    _django_app = get_wsgi_application()
    _steps.append("wsgi app ready")

except BaseException:
    _error = traceback.format_exc()


def app(environ, start_response):
    if _error or _django_app is None:
        info = "Steps completed:\n" + "\n".join(_steps) + "\n\nError:\n" + (_error or "no exception, but app is None")
        body = info.encode("utf-8")
        start_response("200 OK", [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ])
        return [body]
    return _django_app(environ, start_response)


application = app




