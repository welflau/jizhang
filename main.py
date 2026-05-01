from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
class H(SimpleHTTPRequestHandler):
  def do_GET(self):
    if self.path=="/api/health":self.send_response(200);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(json.dumps({"status":"ok"}).encode())
    else:super().do_GET()
if __name__=="__main__":HTTPServer(("0.0.0.0",8080),H).serve_forever()
