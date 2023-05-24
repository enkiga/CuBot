import hashlib
from urllib.parse import parse_qs
import mysql.connector

# Connect to Database try catch
try:
    mydb = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="K1pk0r1r!",
        database="cueabot"
    )
    print("Connection Successful at Operations.py")
    mycursor = mydb.cursor()
except mysql.connector.Error as err:
    print("Error: ", err)


def isFieldEmpty(field_value):
    return field_value is None or field_value.strip() == ""


# Alert js script
def generate_js_warning(message):
    js_script = '''
        <script>
            setTimeout(function() {
                alert("''' + message + '''");
            }, 500); // Display the alert message after .5 seconds (500 milliseconds)
        </script>
        '''
    return js_script


def view_code(environ):
    userAgent = environ.get("HTTP_USER_AGENT")
    return userAgent.encode('utf-8')


def check_for_login(func):
    def wrapper(*args, **kwargs):
        temp_store = open("temp.txt", "r")
        count = 1
        hashes = temp_store.readlines()
        for i in hashes:
            hashU = i.split()
            if f"{hashlib.sha256(view_code(*args)).hexdigest()}user" in hashU:
                print("found", count, ":", i)
                return func(*args, **kwargs)
            count += 1
        else:
            with open("front_end/html/home_page.html", "rb") as f:
                data = f.read()
            return data

    return wrapper


def login_page(request):
    if request.get('REQUEST_METHOD') == 'POST':
        try:
            # Get the data from the request
            size = int(request.get('CONTENT_LENGTH', 0))
        except ValueError:
            size = 0
        data = request['wsgi.input'].read(size)
        data = parse_qs(data)

        # Get the username and password from the data
        email = data.get(b'email', [b''])[0].decode('utf-8')
        password = data.get(b'password', [b''])[0].decode('utf-8')

        # perform login authentication
        if isFieldEmpty(email) or isFieldEmpty(password):
            error = generate_js_warning("Please fill in all fields")
            data += error.encode('utf-8')
            return data

        # Reference the database using a parameterized query
        ref_sql = "SELECT * FROM users WHERE email = %s AND password = %s"
        mycursor.execute(ref_sql, (email, password))

        if mycursor.fetchone():
            try:
                with open("temp.txt", "ab") as logged_in:
                    logged_in.write(f"\n {hashlib.md5(view_code(request)).hexdigest()} user".encode('utf-8'))
            except AssertionError:
                pass

            # Redirect to home page
            f = open('front_end/html/home_page.html', 'rb')
            data = f.read()
            data += generate_js_warning("Login Successful").encode('utf-8')
            data = data.decode('utf-8')
            return data.encode('utf-8')
        else:
            with open('front_end/html/login_page.html', 'rb') as file:
                data = file.read()
            return data

    else:
        f = open('front_end/html/login_page.html', 'rb')
        data = f.read()
        f.close()
        return data


def home_page(environ):
    with open('front_end/html/home_page.html', 'rb') as file:
        data = file.read()
    return data


def signup_page(environ):
    with open('front_end/html/signup_page.html', 'rb') as file:
        data = file.read()
    return data


def root_css(environ):
    with open('front_end/root.css', 'rb') as file:
        data = file.read()
    return data


def login_css(environ):
    with open('front_end/login.css', 'rb') as file:
        data = file.read()
    return data


def box_icon_css(environ):
    with open('front_end/boxicons.min.css', 'rb') as file:
        data = file.read()
    return data


def root_js(environ):
    with open('front_end/root.js', 'rb') as file:
        data = file.read()
    return data
