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

        # Hash the password
        hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()

        # perform login authentication
        if isFieldEmpty(email) or isFieldEmpty(password):
            f = open('front_end/html/login_page.html', 'rb')
            data = f.read()
            data += generate_js_warning("Please fill in all fields").encode('utf-8')
            data = data.decode('utf-8')
            return data.encode('utf-8')

        # Reference the database using a parameterized query
        ref_sql = "SELECT * FROM users WHERE email = %s AND password = %s"
        mycursor.execute(ref_sql, (email, hashed_password))

        # Check if the user exists
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
            f = open('front_end/html/login_page.html', 'rb')
            data = f.read()
            data += generate_js_warning("Invalid Login Credentials").encode('utf-8')
            data = data.decode('utf-8')
            return data.encode('utf-8')

    else:
        f = open('front_end/html/login_page.html', 'rb')
        data = f.read()
        f.close()
        return data


@check_for_login
def home_page(environ):
    with open('front_end/html/home_page.html', 'rb') as file:
        data = file.read()
    return data


def signup_page(request):
    if request.get("REQUEST_METHOD") == "POST":
        try:
            # Get the data from the request
            size = int(request.get('CONTENT_LENGTH', 0))
        except ValueError:
            size = 0
        data = request['wsgi.input'].read(size)
        data = parse_qs(data)

        # Get user input data
        # Personal Details
        fullname = data.get(b'full-name', [b''])[0].decode('utf-8')
        dob = data.get(b'dob', [b''])[0].decode('utf-8')
        mobileNo = data.get(b'mobileNo', [b''])[0].decode('utf-8')

        # Education Details
        campus = data.get(b'campus', [b''])[0].decode('utf-8')
        faculty = data.get(b'faculty', [b''])[0].decode('utf-8')
        program = data.get(b'program', [b''])[0].decode('utf-8')
        email = data.get(b'email', [b''])[0].decode('utf-8')
        studentID = data.get(b'studentID', [b''])[0].decode('utf-8')
        joinDate = data.get(b'join-date', [b''])[0].decode('utf-8')

        # Authentication Details
        password = data.get(b'password', [b''])[0].decode('utf-8')

        # Recovery Details
        question = data.get(b'question', [b''])[0].decode('utf-8')
        answer = data.get(b'answer', [b''])[0].decode('utf-8')

        # Hash the password
        hash_password = hashlib.md5(password.encode('utf-8')).hexdigest()

        # store user data in the database
        signup_sql = "INSERT INTO users (full_name, dob, mobile_no, campus, faculty, program, email, school_id, " \
                     "date_joined, password, recovery_question, recovery_answer) " \
                     "VALUES( %(fullname)s, %(dob)s, %(mobileNo)s, %(campus)s, %(faculty)s, %(program)s, " \
                     "%(email)s, %(studentID)s, %(joinDate)s, %(hash_password)s, %(question)s, %(answer)s)"

        # create a dictionary of the user data
        user_data = {
            'fullname': fullname,
            'dob': dob,
            'mobileNo': mobileNo,
            'campus': campus,
            'faculty': faculty,
            'program': program,
            'email': email,
            'studentID': studentID,
            'joinDate': joinDate,
            'hash_password': hash_password,
            'question': question,
            'answer': answer
        }

        # check if user data is already in the database
        ref_sql = "SELECT * FROM users WHERE email = %s AND school_id = %s AND mobile_no = %s"
        mycursor.execute(ref_sql, (email, studentID, mobileNo))

        if mycursor.fetchone():
            f = open('front_end/html/signup_page.html', 'rb')
            data = f.read()
            data += generate_js_warning("User already exists").encode('utf-8')
            data = data.decode('utf-8')
            return data.encode('utf-8')
        else:
            mycursor.execute(signup_sql, user_data)
            mydb.commit()

        while True:
            try:
                with open("temp.txt", "ab") as logged_in:
                    logged_in.write(f"\n {hashlib.md5(view_code(request)).hexdigest()} user".encode('utf-8'))
            except AssertionError:
                pass

            # Redirect to home page
            f = open('front_end/html/home_page.html', 'rb')
            data = f.read()
            data += generate_js_warning("Signup Successful").encode('utf-8')
            data = data.decode('utf-8')
            return data.encode('utf-8')

    else:
        f = open('front_end/html/signup_page.html', 'rb')
        data = f.read()
        f.close()
        return data


def profile_page(environ):
    with open('front_end/html/profile_page.html', 'rb') as file:
        data = file.read()
    return data


def chat_page(environ):
    with open('front_end/html/chat_page.html', 'rb') as file:
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


def signup_css(environ):
    with open('front_end/signup.css', 'rb') as file:
        data = file.read()
    return data


def root_js(environ):
    with open('front_end/root.js', 'rb') as file:
        data = file.read()
    return data


def signup_js(environ):
    with open('front_end/signup.js', 'rb') as file:
        data = file.read()
    return data
