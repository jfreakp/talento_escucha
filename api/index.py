import os
import sys
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "talento_escucha.settings")

try:
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
    application = app
except Exception as e:
    error_detail = traceback.format_exc()
    print(f"STARTUP ERROR: {e}\n{error_detail}", file=sys.stderr)

    def app(environ, start_response):
        status = "500 Internal Server Error"
        body = f"Startup error:\n{error_detail}".encode()
        start_response(status, [
            ("Content-Type", "text/plain"),
            ("Content-Length", str(len(body))),
        ])
        return [body]

    application = app
