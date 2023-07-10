# from wsgiref.simple_server import make_server
from waitress import serve
from url import url_patterns
from model import createTables

# Port & Thread Variable
HOST = 'localhost'
PORT = 3000


class WebApp:
    def __init__(self):
        self.session = {}

    def __call__(self, environ, start_response):
        def content_type(pathfile):
            if pathfile.endswith('.js'):
                return 'text/javascript'
            elif pathfile.endswith('.css'):
                return 'text/css'
            else:
                return 'text/html'

        func = None
        for items in url_patterns:
            if items[0] == environ.get('PATH_INFO'):
                func = items[1]
                break

        if func:
            start_response('200 OK', [('Content-Type', content_type(environ.get('PATH_INFO')))])
            data = func(environ)
            return [data]
        else:
            start_response('404 Not Found', [('Content-Type', content_type(environ.get('PATH_INFO')))])
            data = b''
            with open('front_end/html/404_error.html', 'rb') as f:
                data = f.read()
            return [data]


app = WebApp()
createTables()

if __name__ == '__main__':
    try:
        print(f'serving at http://{HOST}:{PORT}\nPress"ctrl+c" to stop serving')
        serve(app, port=PORT, threads=12)
        print("Server Stopped")
        with open('temp.txt', 'r+') as f:
            f.truncate(0)

    except OSError as e:
        print(f"Server failed to start due to an OS error: {e}")
    except Exception as e:
        print(f"Server failed to start, check your configurations: {e}")
