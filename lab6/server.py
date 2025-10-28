from http.server import BaseHTTPRequestHandler, HTTPServer
import json, re

HOST='0.0.0.0'
PORT=8099

def process_text(s: str) -> str:
    if s is None:
        return ''
    s = re.sub(r"\s+,", ",", s)               # no spaces before comma
    s = re.sub(r",\s*,+", ",", s)             # collapse double commas
    s = re.sub(r",\s*", ", ", s)              # one space after comma
    s = re.sub(r",\s+$", ",", s)              # but not at end
    s = re.sub(r"^\s*,+", "", s)              # cannot start with comma
    return s

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/process':
            self.send_error(404); return
        length = int(self.headers.get('Content-Length', '0') or 0)
        body = self.rfile.read(length) if length else b''
        try:
            payload = json.loads(body.decode('utf-8'))
            result = process_text(payload.get('text',''))
            resp = json.dumps({'text': result}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
        except Exception as e:
            data = json.dumps({'error': str(e)}, ensure_ascii=False).encode('utf-8')
            self.send_response(400)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
    def log_message(self, fmt, *args): pass

def run():
    httpd = HTTPServer((HOST, PORT), Handler)
    print(f'Server running at http://{HOST}:{PORT}')
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass
    finally:
        httpd.server_close()
        print('Server stopped.')

if __name__=='__main__':
    run()
