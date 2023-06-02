import hashlib
from urllib.parse import parse_qs
import mysql.connector
from datetime import date

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

# session dictionary
session = {}


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


def view_code(environ, request):
    userAgent = environ.get("HTTP_USER_AGENT")
    return userAgent.encode('utf-8')


def check_for_login(func):
    def wrapper(*args, **kwargs):
        # check if the user is logged in from temp.txt
        with open('temp.txt', 'r') as f:
            email = f.read()
        if email:
            # user is logged in
            return func(*args, **kwargs)
        else:
            return login_page(*args, **kwargs)

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
            # Check if the user is already logged in
            if email in session.values():
                # Redirect to home page
                f = open('front_end/html/loading_homepage.html', 'rb')
                data = f.read()
                data += generate_js_warning("Already Logged In").encode('utf-8')
                data = data.decode('utf-8')
                return data.encode('utf-8')
            else:
                # Generate a session ID
                session_id = hashlib.md5(email.encode('utf-8')).hexdigest()

                # Store session data
                session[session_id] = {
                    'username': email,
                }

                # Set the session ID as a cookie
                response_headers = [('Content-Type', 'text/html'), ('Set-Cookie', f'session_id={session_id}; path=/')]

                # store the session ID in temp.txt
                with open('temp.txt', 'w') as file:
                    file.write(response_headers[1][1].split('=')[1].split(';')[0])

            # Redirect to loading page
            f = open('front_end/html/loading_homepage.html', 'rb')
            data = f.read()
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
def loading_page(environ, request):
    with open('front_end/html/loading_page.html', 'rb') as file:
        data = file.read()
    return data


@check_for_login
def home_page(environ):
    # Get the session ID from temp.txt
    data = b''
    with open('temp.txt', 'r') as file:
        session_id = file.read()

    if session_id:
        # check if session id exists in the session dictionary
        if session_id in session:
            session_data = session[session_id]

            # get user from database
            sql = "SELECT * FROM users WHERE email = %s"
            mycursor.execute(sql, (session_data['username'],))
            user = mycursor.fetchone()

            # get user lastname
            lastname = user[0].split(' ')[-1]

            # open the home page
            with open('front_end/html/home_page.html', 'rb') as file:
                data = file.read()

            # replace the username with the last name
            data = data.replace(b'{{lastname}}', lastname.encode('utf-8'))

        return data

    else:
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
        # make answer lowercase
        answer = answer.lower()

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

            # Generate a session ID
            session_id = hashlib.md5(email.encode('utf-8')).hexdigest()
            # check if session id exists in the dictionary
            if session_id not in session:
                # add the session id to the dictionary
                session[session_id] = {
                    'username': email,
                }
            # Set the session ID as a cookie
            response_headers = [('Content-Type', 'text/html'), ('Set-Cookie', f'session_id={session_id}; path=/')]

            # store the session ID in temp.txt
            with open('temp.txt', 'w') as file:
                file.write(response_headers[1][1].split('=')[1].split(';')[0])

            # Redirect to home page
            f = open('front_end/html/loading_homepage.html', 'rb')
            data = f.read()
            data = data.decode('utf-8')
            return data.encode('utf-8')

    else:
        f = open('front_end/html/signup_page.html', 'rb')
        data = f.read()
        f.close()
        return data


def profile_page(environ, request):
    # get session id from temp.txt
    with open('temp.txt', 'r') as file:
        session_id = file.read()

    if session_id:
        # check if session id exists in the dictionary
        if session_id in session:
            session_data = session[session_id]

            # get user data from the database
            mycursor.execute("SELECT * FROM users WHERE email = %s", (session_data['username'],))
            user_data = mycursor.fetchone()

            # personalize the profile page
            with open('front_end/html/profile_page.html', 'r') as file:
                data = file.read()

                # convert the date to string
                user_data = list(user_data)
                if isinstance(user_data[2], date):
                    user_data[2] = user_data[2].strftime('%d/%m/%Y')
                if isinstance(user_data[9], date):
                    user_data[9] = user_data[9].strftime('%d/%m/%Y')

                # personal details
                data = data.replace('{{fullname}}', str(user_data[0]))
                data = data.replace('{{dob}}', str(user_data[1]))
                data = data.replace('{{mobileNo}}', str(user_data[2]))

                # education details
                data = data.replace('{{campus}}', str(user_data[3]))
                data = data.replace('{{faculty}}', str(user_data[4]))
                data = data.replace('{{program}}', str(user_data[5]))
                data = data.replace('{{email}}', str(user_data[6]))
                data = data.replace('{{studentID}}', str(user_data[7]))
                data = data.replace('{{joinDate}}', str(user_data[8]))

            # return the profile page
            return data.encode('utf-8')

    # if session id does not exist or user is not authenticated
    with open('front_end/html/profile_page.html', 'rb') as file:
        data = file.read()
    return data


def logout(environ, request):
    # get session id from temp.txt
    with open('temp.txt', 'r') as file:
        session_id = file.read()

    # check if session id exists in the dictionary
    if session_id in session:
        # remove the session id from the dictionary
        session.pop(session_id)

    # clear the session id from the cookie
    response_headers = [('Content-Type', 'text/html'), ('Set-Cookie', f'session_id=; path=/')]

    # store the session ID in temp.txt
    with open('temp.txt', 'w') as file:
        file.write('')

    # Redirect to login page
    f = open('front_end/html/loading_logout.html', 'rb')
    data = f.read()
    data = data.decode('utf-8')
    return data.encode('utf-8')


def loading_logout(environ, request):
    f = open('front_end/html/loading_logout.html', 'rb')
    data = f.read()
    data = data.decode('utf-8')
    return data.encode('utf-8')


def chat_page(environ, request):
    with open('front_end/html/chat_page.html', 'rb') as file:
        data = file.read()
    return data


def root_css(environ, request):
    with open('front_end/root.css', 'rb') as file:
        data = file.read()
    return data


def login_css(environ, request):
    with open('front_end/login.css', 'rb') as file:
        data = file.read()
    return data


def signup_css(environ, request):
    with open('front_end/signup.css', 'rb') as file:
        data = file.read()
    return data


def root_js(environ, request):
    with open('front_end/root.js', 'rb') as file:
        data = file.read()
    return data


def signup_js(environ, request):
    with open('front_end/signup.js', 'rb') as file:
        data = file.read()
    return data
