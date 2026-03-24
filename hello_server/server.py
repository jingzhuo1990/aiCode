from http.server import HTTPServer, BaseHTTPRequestHandler

class HelloRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"hello world")
    
    def log_message(self, format, *args):
        pass  # 抑制日志输出

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8000), HelloRequestHandler)
    print("服务器运行在 http://localhost:8000")
    server.serve_forever()