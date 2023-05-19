import http.server
import socketserver


# Set up the server host and port
HOST = 'localhost'
PORT = 8000

# Set up the request handler
Handler = http.server.SimpleHTTPRequestHandler

# Set the default filename to "page.html"
Handler.default_filename = 'Pages/Login.html'


# Create custom handler by subclassing BaseHTTPRequestHandler
class CustomHandler(http.server.BaseHTTPRequestHandler):
    def __call__(self, environ, start_response):
        def content_type(pathfile):
            if pathfile.endswith('.js'):
                return 'text/javascript'
            elif pathfile.endswith('.css'):
                return 'text/css'
            else:
                return 'text/html'

        func = None
        for items in HTML_PAGES:
            if items[0] == environ.get('PATH_INFO'):
                func = items[1]
                break

        if func:
            start_response('200 OK', [('Content-Type', content_type(environ.get('PATH_INFO')))])
            data = func(environ)
            return [data]

            # self.send_response(200)
            # self.send_header('Content-Type', content_type(self.path))
            # self.end_headers()
            # data = func(self)
            # self.wfile.write(data.encode('utf-8'))
        else:
            start_response('404 Not Found', [('Content-Type', content_type(environ.get('PATH_INFO')))])
            data = b''
            with open('Pages/404Error.html', 'rb') as file:
                data = file.read()
            return [data]

            # self.send_response(404)
            # self.send_header('Content-Type', content_type(self.path))
            # self.end_headers()
            # with open('Pages/404Error.html', 'rb') as file:
            #     data = file.read()
            #     self.wfile.write(data)


app = CustomHandler
createTable()

# Start the server
if __name__ == '__main__':
    try:
        print(f'Server started at http://{HOST}:{PORT} \nPress Ctrl + C to exit')
        httpd = socketserver.TCPServer((HOST, PORT), app)
        print("Server started")
        with open('temp.txt', 'r+') as f:
            f.truncate(0)
        httpd.serve_forever()
    except OSError as e:
        print(f"Server failed to start due to an OS error: {e}")
    except Exception as e:
        print(f"Server failed to start, check your configurations: {e}")
