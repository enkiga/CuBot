from waitress import serve
from model import createTables
from operations import login_page, signup_page, home_page, forgot_password_page, reset_password_page, recovery_page, \
    change_password_page
from url import url_patterns

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
            if environ.get('PATH_INFO') == '/':
                response = login_page(environ)
                response, headers = self.prevent_cache(response)
            elif environ.get('PATH_INFO') == '/signup':
                response = signup_page(environ)
                response, headers = self.prevent_cache(response)
            elif environ.get('PATH_INFO') == '/home':
                response = home_page(environ)
                response, headers = self.prevent_cache(response)
            elif environ.get('PATH_INFO') == '/forgot_password':
                response = forgot_password_page(environ)
                response, headers = self.prevent_cache(response)
            elif environ.get('PATH_INFO') == '/recovery':
                response = recovery_page(environ)
                response, headers = self.prevent_cache(response)
            elif environ.get('PATH_INFO') == '/reset_password':
                response = reset_password_page(environ)
                response, headers = self.prevent_cache(response)
            elif environ.get('PATH_INFO') == '/change_password':
                response = change_password_page(environ)
                response, headers = self.prevent_cache(response)
            else:
                response = func(environ, self.session)
                headers = []

            start_response('200 OK', [('Content-Type', content_type(environ.get('PATH_INFO')))] + headers)
            return [response]

        else:
            start_response('404 Not Found', [('Content-Type', content_type(environ.get('PATH_INFO')))])
            with open('front_end/html/404_error.html', 'rb') as file:
                data = file.read()
            return [data]

    @staticmethod
    def prevent_cache(response):
        headers = [('Cache-Control', 'no-cache, no-store, must-revalidate'),
                   ('Pragma', 'no-cache'),
                   ('Expires', '0')]
        return response, headers


app = WebApp()
createTables()

# Start the server
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
