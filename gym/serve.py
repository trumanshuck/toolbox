import http.server
import os
import socket

PORT = 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".appcache": "text/cache-manifest"}

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"Open http://{socket.gethostname().removesuffix('.local')}.local:{PORT}/ on the iPad")
http.server.ThreadingHTTPServer(("", PORT), Handler).serve_forever()
