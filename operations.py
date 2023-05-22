import hashlib
from urllib.parse import parse_qs
import mysql.connector
import re

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


def view_code(environ):
    userAgent = environ.get("HTTP_USER_AGENT")
    return userAgent.encode('utf-8')


def login(environ):
    f = open("pages/login.html", "rb")
    data = f.read()
    return data


def profile(environ):
    f = open("pages/profile.html", "rb")
    data = f.read()
    return data


def chat(environ):
    f = open("pages/chat.html", "rb")
    data = f.read()
    return data


# Process user input function
# Warning message function
def generate_js_warning(message):
    js_script = f"""
    <script>
    alert('{message}');
    window.history.back();
    </script>
    """
    return js_script


# check all fields
def isFieldEmpty(field_value):
    if field_value is None or field_value.strip() == "":
        return True
    return False


# signup function
def signup(request):
    # get user input from html form
    if request.get("REQUEST_METHOD") == "POST":
        try:
            length = int(request.get("CONTENT_LENGTH", 0))
        except ValueError:
            length = 0
        body = request.get("wsgi.input").read(length)
        data = parse_qs(body.decode("utf-8"))

        # users input
        username = data.get("username")[0].decode("utf-8")
        full_name = data.get("full-name")[0].decode("utf-8")
        dob = data.get("dob")[0].decode("utf-8")
        mobile_no = data.get("mobileNo")[0].decode("utf-8")
        campus = data.get("campus")[0].decode("utf-8")
        faculty = data.get("faculty")[0].decode("utf-8")
        program = data.get("program")[0].decode("utf-8")
        email = data.get("email")[0].decode("utf-8")
        school_id = data.get("schoolID")[0].decode("utf-8")
        date_joined = data.get("join-date")[0].decode("utf-8")
        recovery_question = data.get("question")[0].decode("utf-8")
        recovery_answer = data.get("answer")[0].decode("utf-8")
        password = data.get("password")[0].decode("utf-8")

        # process user input
        # check if any field is empty
        if isFieldEmpty(username) or isFieldEmpty(full_name) or isFieldEmpty(dob) or isFieldEmpty(mobile_no) or \
                isFieldEmpty(campus) or isFieldEmpty(faculty) or isFieldEmpty(program) or isFieldEmpty(email) or \
                isFieldEmpty(school_id) or isFieldEmpty(date_joined) or isFieldEmpty(recovery_question) or \
                isFieldEmpty(recovery_answer) or isFieldEmpty(password):
            return generate_js_warning("All fields are required")

        # check if username is valid
        if not re.match(r"^[a-zA-Z0-9_]{3,20}$", username):
            return generate_js_warning(
                "Username must be 3-20 characters long and can only contain letters, numbers and underscores")

        # check if username already exists
        mycursor.execute("SELECT * FROM users WHERE username = %(username)s", (username,))
        if mycursor.fetchone() is not None:
            return generate_js_warning("Username already exists")

        # check if email is valid
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$+@cuea.edu$", email):
            return generate_js_warning("Invalid email address format - Must end with @cuea.edu")

        # check if email already exists
        mycursor.execute("SELECT * FROM users WHERE email = %(email)s", (email,))
        if mycursor.fetchone() is not None:
            return generate_js_warning("Email already exists")

        # check if mobile number is valid
        if not re.match(r"^[0-9]{13}$", mobile_no):
            return generate_js_warning("Invalid mobile number")
        elif not mobile_no.startswith("+254"):
            return generate_js_warning("Mobile number must start with +254")

        # check if mobile number already exists
        mycursor.execute("SELECT * FROM users WHERE mobile_no = %(mobile_no)s", (mobile_no,))
        if mycursor.fetchone() is not None:
            return generate_js_warning("Mobile number already exists")

        # check if school id is valid
        if not re.match(r"^[0-9]{7}$", school_id):
            return generate_js_warning("Invalid school ID")

        # check if school id already exists
        mycursor.execute("SELECT * FROM users WHERE school_id = %(school_id)s", (school_id,))
        if mycursor.fetchone() is not None:
            return generate_js_warning("School ID already exists")

        # check if password is valid
        if not re.match(r"^[a-zA-Z0-9_!@#$%^&*()-+=]{8,20}$", password):
            return generate_js_warning(
                "Password must be 8-20 characters long and can only contain letters, numbers and special characters: "
                "!@#$%^&*()-+=")

        # hash password
        hashlib.md5(password).hexdigest()

        # insert user into database
        signUpSql = "INSERT INTO users (username, full_name, dob, mobile_no, campus, faculty, program, email, " \
                    "school_id, date_joined, recovery_question, recovery_answer, password) VALUES (username, " \
                    "full_name, dob, mobile_no, campus, faculty, program, email, school_id, date_joined, " \
                    "recovery_question, recovery_answer,hashlib.md5(password).hexdigest()) "

        mycursor.executemany(signUpSql)
        mydb.commit()
        mydb.close()
        while True:
            try:
                with open("temp.txt", "ab") as temp_store:
                    temp_store.write(f"\n {hashlib.md5(view_code(request)).hexdigest()}users".encode("utf-8"))
            except AssertionError:
                print("Error writing to file")
                pass

            f = open("pages/login.html", "rb")
            data = f.read()
            data = data.decode("utf-8")
            return data.encode("utf-8")
    else:
        f = open("pages/signUp.html", "rb")
        data = f.read()
        f.close()
        return data


def home(environ):
    f = open("pages/home.html", "rb")
    data = f.read()
    return data


def mainCss(environ):
    with open("pages/styling/main.css", "rb") as f:
        data = f.read()
    return data


def authCss(environ):
    with open("pages/styling/auth.css", "rb") as f:
        data = f.read()
    return data


def mainJs(environ):
    with open("pages/styling/main.js", "rb") as f:
        data = f.read()
    return data


def notFoundCss(environ):
    with open("pages/styling/404.css", "rb") as f:
        data = f.read()
    return data


def iconsCss(environ):
    with open("pages/styling/boxicons.min.css", "rb") as f:
        data = f.read()
    return data
