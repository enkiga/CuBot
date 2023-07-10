import hashlib
import json
from urllib.parse import parse_qs
import mysql.connector
from datetime import date
import pickle
import random
import string
import nltk
import numpy as np
import tensorflow as tf
from nltk.stem import WordNetLemmatizer

from events_json_generator import generate_event_json
from timetable_json_generator import generate_timetable_json
from lecturer_json_generator import generate_lecturer_json
from bot_setup import train_bot

# Connect to Database try catch
try:
    mydb = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="K1pk0r1r!",
        database="cueabot"
    )
    mycursor = mydb.cursor()
except mysql.connector.Error as err:
    print("Error: ", err)

# session dictionary
session = {}

# load trained model and other requirements for chat page.
model = tf.keras.models.load_model('chatbot_model.h5')
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
lemmatizer = WordNetLemmatizer()


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
        user = mycursor.fetchone()
        if user:
            # Check if the user is already logged in
            if email in session.values():
                # Redirect to home page
                f = open('front_end/html/loading_homepage.html', 'rb')
                data = f.read()
                data += generate_js_warning("Already Logged In").encode('utf-8')
                data = data.decode('utf-8')
                return data.encode('utf-8')
            else:
                # Get the user role
                role = user[11]

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
            if role == 'student':
                f = open('front_end/html/loading_homepage.html', 'rb')
                data = f.read()
                data = data.decode('utf-8')
                return data.encode('utf-8')
            elif role == 'admin':
                f = open('front_end/html/loading_admin_page.html', 'rb')
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
def loading_admin_page(environ, request):
    with open('front_end/html/loading_admin_page.html', 'rb') as file:
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
            data = data.replace(b'{{lastname}}', b'')

        return data


@check_for_login
def admin_page(environ):
    # get conversation table count
    sql = "SELECT COUNT(*) FROM conversations"
    mycursor.execute(sql)
    conversations = mycursor.fetchone()[0]

    # get users table count
    sql = "SELECT COUNT(*) FROM users"
    mycursor.execute(sql)
    users = mycursor.fetchone()[0]

    # get timetable table count
    sql = "SELECT COUNT(*) FROM timetable"
    mycursor.execute(sql)
    timetable = mycursor.fetchone()[0]

    # get events table count
    sql = "SELECT COUNT(*) FROM events"
    mycursor.execute(sql)
    events = mycursor.fetchone()[0]

    # get lecturers table count
    sql = "SELECT COUNT(*) FROM lecturers"
    mycursor.execute(sql)
    lecturers = mycursor.fetchone()[0]

    # do a summation of all the counts
    total = timetable + events + lecturers

    # get the last five records from the conversations table
    sql = "SELECT * FROM conversations ORDER BY conversation_no DESC LIMIT 5"
    mycursor.execute(sql)
    conversations_data = mycursor.fetchall()

    # Generate HTML for table rows dynamically
    table_rows = ''
    for row in conversations_data:
        user = row[1]
        message = row[2]
        time = str(row[5])

        # show time in hh:mm format instead of the default hh:mm:ss
        time = time.split(':')[0] + ':' + time.split(':')[1]

        table_rows += f'''
            <tr>
                <td>
                <i class="bx bxs-user"></i>
                <p>{user}<p>
                </td>
                <td>{message}</td>
                <td>{time}</td>
            </tr>
        '''

    # replace all placeholders with the appropriate counts
    with open('front_end/html/admin_dashboard.html', 'rb') as file:
        data = file.read()
        data = data.replace(b'{{conversations}}', str(conversations).encode('utf-8'))
        data = data.replace(b'{{users}}', str(users).encode('utf-8'))
        data = data.replace(b'{{training_data}}', str(total).encode('utf-8'))
        data = data.replace(b'{table_rows}', table_rows.encode('utf-8'))

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
                     "date_joined, password, recovery_question, recovery_answer, role) " \
                     "VALUES( %(fullname)s, %(dob)s, %(mobileNo)s, %(campus)s, %(faculty)s, %(program)s, " \
                     "%(email)s, %(studentID)s, %(joinDate)s, %(hash_password)s, %(question)s, %(answer)s, %(role)s)"

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
            'answer': answer,
            'role': 'student'
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
            # Get the count of users table
            count_sql = "SELECT COUNT(*) FROM users"
            mycursor.execute(count_sql)
            count = mycursor.fetchone()[0]

            # Assign the role of admin for first user
            if count == 0:
                user_data['role'] = 'admin'

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


def forgot_password_page(request):
    if request.get("REQUEST_METHOD") == "POST":
        try:
            # Get the data from the request
            size = int(request.get('CONTENT_LENGTH', 0))
        except ValueError:
            size = 0
        data = request['wsgi.input'].read(size)
        data = parse_qs(data)

        # Get the user input
        email = data.get(b'email', [b''])[0].decode('utf-8')

        # Check if the email exists in the database
        ref_sql = "SELECT * FROM users WHERE email = %s"
        mycursor.execute(ref_sql, (email,))
        user_data = mycursor.fetchone()

        if user_data:
            # generate an email session id
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

            # Redirect to recovery page
            f = open('front_end/html/loading_recovery_page.html', 'rb')
            data = f.read()
            data = data.decode('utf-8')
            return data.encode('utf-8')

        else:
            # Redirect to forget password page
            f = open('front_end/html/forgot_password_page_one.html', 'rb')
            data = f.read()
            data += generate_js_warning('Email does not exist! Create account!').encode('utf-8')
            data = data.decode('utf-8')
            return data.encode('utf-8')
    else:
        # Redirect to forget password page
        f = open('front_end/html/forgot_password_page_one.html', 'rb')
        data = f.read()
        data = data.decode('utf-8')
        return data.encode('utf-8')


def loading_recovery_page(environ, request):
    f = open('front_end/html/loading_recovery_page.html', 'rb')
    data = f.read()
    data = data.decode('utf-8')
    return data.encode('utf-8')


def check_recovery_question(func):
    def wrapper(*args, **kwargs):
        # Get the session ID from temp.txt
        with open('temp.txt', 'r') as file:
            session_id = file.read()

        # Get user email from session ID
        email = session[session_id]['username']

        # Get the user data from the database
        mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = mycursor.fetchone()

        if user_data:
            recovery_question = user_data[9]
            html_path = 'front_end/html/forgot_password_page_two.html'

            with open(html_path, 'rb') as file:
                data = file.read()

            # Replace the recovery_question placeholder with the user's recovery question
            data = data.decode('utf-8')
            data = data.replace('{{recovery_question}}', recovery_question)
            data = data.encode('utf-8')

            return func(*args, data=data, **kwargs)  # Pass email and data as keyword arguments
        else:
            # Redirect to forget password page
            f = open('front_end/html/forgot_password_page_one.html', 'rb')
            data = f.read()
            data += generate_js_warning('Email does not exist! Create account!').encode('utf-8')
            data = data.decode('utf-8')
            return data.encode('utf-8')

    return wrapper


@check_recovery_question
def recovery_page(request, data):
    if request.get("REQUEST_METHOD") == "POST":
        try:
            # Get the data from the request
            size = int(request.get('CONTENT_LENGTH', 0))
        except ValueError:
            size = 0
        data = request['wsgi.input'].read(size)
        data = parse_qs(data)

        # Get the user input
        answer = data.get(b'recovery_answer', [b''])[0].decode('utf-8')

        # Get session ID from temp.txt
        with open('temp.txt', 'r') as file:
            session_id = file.read()

        # Get email from session
        email = session[session_id]['username']

        # Reference the database using the email and answer
        ref_sql = "SELECT * FROM users WHERE email = %s AND recovery_answer = %s"
        mycursor.execute(ref_sql, (email, answer))

        # Check if the answer is correct
        user_data = mycursor.fetchone()
        if user_data:
            # Generate a recovery session ID
            session_id = hashlib.md5(email.encode('utf-8')).hexdigest()

            # Check if session ID exists in the dictionary
            if session_id not in session:
                # Add the session ID to the dictionary
                session[session_id] = {
                    'username': email,
                }

            # Set the session ID as a cookie
            response_headers = [('Content-Type', 'text/html'), ('Set-Cookie', f'session_id={session_id}; path=/')]

            # Store the session ID in temp.txt
            with open('temp.txt', 'w') as file:
                file.write(response_headers[1][1].split('=')[1].split(';')[0])

            # Redirect to change password page
            f = open('front_end/html/loading_reset_password_page.html', 'rb')
            data = f.read()
            data = data.decode('utf-8')
            return data.encode('utf-8')
        else:
            # redirect back to forget password page with warning
            f = open('front_end/html/loading_recovery_page.html', 'rb')
            data = f.read()
            data += generate_js_warning('Incorrect answer!').encode('utf-8')
            data = data.decode('utf-8')
            return data.encode('utf-8')
    else:
        return data  # Return the data from the decorator


def loading_reset_page(environ, request):
    f = open('front_end/html/loading_reset_page.html', 'rb')
    data = f.read()
    data = data.decode('utf-8')
    return data.encode('utf-8')


def reset_password_page(request):
    if request.get('REQUEST_METHOD') == 'POST':
        try:
            # Get the data from the request
            size = int(request.get('CONTENT_LENGTH', 0))
        except ValueError:
            size = 0
        data = request['wsgi.input'].read(size)
        data = parse_qs(data)

        # Get the user input
        password = data.get(b'new_password', [b''])[0].decode('utf-8')
        confirm_password = data.get(b'confirm_new_password', [b''])[0].decode('utf-8')

        # Get session ID from temp.txt
        with open('temp.txt', 'r') as file:
            session_id = file.read()

        # Get email from session
        email = session[session_id]['username']

        # Reference the database using the email
        ref_sql = "SELECT * FROM users WHERE email = %s"
        mycursor.execute(ref_sql, (email,))

        # Check if the email exists
        user_data = mycursor.fetchone()
        if user_data:
            # Check if the passwords match
            if password == confirm_password:
                # Hash the password
                password = hashlib.md5(password.encode('utf-8')).hexdigest()

                # Update the database
                update_sql = "UPDATE users SET password = %s WHERE email = %s"
                mycursor.execute(update_sql, (password, email))
                mydb.commit()

                # Redirect to login page
                f = open('front_end/html/loading_login_page.html', 'rb')
                data = f.read()
                data += generate_js_warning('Password changed successfully!').encode('utf-8')
                data = data.decode('utf-8')
                return data.encode('utf-8')
            else:
                # Redirect to change password page with warning
                f = open('front_end/html/forgot_password_page_final.html', 'rb')
                data = f.read()
                data += generate_js_warning('Passwords do not match!').encode('utf-8')
                data = data.decode('utf-8')
                return data.encode('utf-8')
        else:
            # Redirect to login page
            f = open('front_end/html/login_page.html', 'rb')
            data = f.read()
            data += generate_js_warning('Email does not exist! Create account!').encode('utf-8')
            data = data.decode('utf-8')
            return data.encode('utf-8')
    else:
        with open('front_end/html/forgot_password_page_final.html', 'rb') as file:
            data = file.read()
        return data


def loading_login_page(environ, request):
    f = open('front_end/html/loading_login_page.html', 'rb')
    data = f.read()
    data = data.decode('utf-8')
    return data.encode('utf-8')


def change_password_page(request):
    if request.get('REQUEST_METHOD') == 'POST':
        try:
            # Get the data from the request
            size = int(request.get('CONTENT_LENGTH', 0))
        except ValueError:
            size = 0
        data = request['wsgi.input'].read(size)
        data = parse_qs(data)

        # Get the user input
        old_password = data.get(b'old_password', [b''])[0].decode('utf-8')
        new_password = data.get(b'new_password', [b''])[0].decode('utf-8')
        confirm_password = data.get(b'confirm_new_password', [b''])[0].decode('utf-8')

        # Get session ID from temp.txt
        with open('temp.txt', 'r') as file:
            session_id = file.read()

        # Get email from session
        email = session[session_id]['username']

        # Reference the database using the email
        ref_sql = "SELECT * FROM users WHERE email = %s"
        mycursor.execute(ref_sql, (email,))

        # Check if the email exists
        user_data = mycursor.fetchone()
        if user_data:
            # Check if the passwords match
            if user_data[11] == hashlib.md5(old_password.encode('utf-8')).hexdigest():
                # Check if the passwords match
                if new_password == confirm_password and new_password != old_password:
                    # Hash the password
                    new_password = hashlib.md5(new_password.encode('utf-8')).hexdigest()

                    # Update the database
                    update_sql = "UPDATE users SET password = %s WHERE email = %s"
                    mycursor.execute(update_sql, (new_password, email))
                    mydb.commit()

                    # Redirect to login page
                    f = open('front_end/html/loading_login_page.html', 'rb')
                    data = f.read()
                    data += generate_js_warning('Password changed successfully!').encode('utf-8')
                    data = data.decode('utf-8')
                    return data.encode('utf-8')
                else:
                    # Redirect to change password page with warning
                    f = open('front_end/html/change_password.html', 'rb')
                    data = f.read()
                    data += generate_js_warning('New and Confirm New Passwords do not match! or '
                                                'New password cannot be the same as Old Password').encode('utf-8')
                    data = data.decode('utf-8')
                    return data.encode('utf-8')
            else:
                # Redirect to change password page with warning
                f = open('front_end/html/change_password.html', 'rb')
                data = f.read()
                data += generate_js_warning('Old password is incorrect').encode('utf-8')
                data = data.decode('utf-8')
                return data.encode('utf-8')
    else:
        with open('front_end/html/change_password.html', 'rb') as file:
            data = file.read()
        return data


# chat page
def clean_message(message):
    tokens = nltk.word_tokenize(message)
    tokens = [lemmatizer.lemmatize(word.lower()) for word in tokens if word not in string.punctuation]
    return tokens


def bag_of_words(message, vocab):
    tokens = clean_message(message)
    bag = [0] * len(vocab)
    for w in tokens:
        for i, word in enumerate(vocab):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(message, vocab, labels):
    bow = bag_of_words(message, vocab)
    result = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    result = [[i, r] for i, r in enumerate(result) if r > ERROR_THRESHOLD]

    result.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in result:
        return_list.append({'intent': labels[r[0]], 'probability': str(r[1])})
    return return_list


def get_response(intents_list, intents_json):
    result = ''
    if len(intents_list) == 0:
        result = 'Sorry, I do not understand!'
        return result
    else:
        tag = intents_list[0]['intent'].strip()
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if i['tag'] == tag:
                result = random.choice(i['responses'])
                break
    return result


def loading_chat_page(environ, request):
    f = open('front_end/html/loading_chat_page.html', 'rb')
    data = f.read()
    data = data.decode('utf-8')
    return data.encode('utf-8')


def chat_page(request):
    # get user session id
    if request.get('REQUEST_METHOD') == 'POST':
        try:
            # Get the data from the request
            size = int(request.get('CONTENT_LENGTH', 0))
        except ValueError:
            size = 0
        data = request['wsgi.input'].read(size)
        data = json.loads(data)

        message = data['message']
        time = data['time']
        chat_date = data['date']

        # format chat_date to fit sql format
        chat_date = chat_date.split('/')
        chat_date = chat_date[2] + '-' + chat_date[1] + '-' + chat_date[0]

        with open('intents.json') as file:
            intents_json = json.load(file)

        with open('timetable.json') as file:
            timetable_json = json.load(file)

        with open('event.json') as file:
            event_json = json.load(file)

        with open('lecturer.json') as file:
            lecturer_json = json.load(file)

        # combine timetable and intents
        intents_json['intents'] += timetable_json['intents']
        intents_json['intents'] += event_json['intents']
        intents_json['intents'] += lecturer_json['intents']

        intents = predict_class(message, words, classes)
        response = get_response(intents, intents_json)

        response_body = json.dumps({'response': response})

        print(message)
        print(time)
        print(chat_date)
        print(response)
        print('---------------------------------')

        # store the chat in the conversation table
        with open('temp.txt', 'r') as file:
            session_id = file.read()

        if session_id:
            # check if the session id exist in the session dictionary
            if session_id in session:
                session_data = session[session_id]

                # get user from database
                sql = "SELECT * FROM users WHERE email = %s"
                mycursor.execute(sql, (session_data['username'],))
                user = mycursor.fetchone()

                # get user student id
                user_id = user[7]
                print(user_id)

                # insert chat into database
                sql = "INSERT INTO conversations (conversation_no, user_id, message_sent, message_received, " \
                      "date_sent, time_sent) VALUES (NULL, %(user_id)s, %(message)s, %(response)s, %(chat_date)s, " \
                      "%(time)s)"
                val = {'user_id': user_id, 'message': message, 'response': response, 'chat_date': chat_date,
                       'time': time}

                try:
                    mycursor.execute(sql, val)
                    mydb.commit()
                except mysql.connector.Error as sql_err:
                    print("Error Inserting Data: {}".format(sql_err))

        return response_body.encode('utf-8')

    else:
        with open('front_end/html/chat_page.html', 'rb') as file:
            data = file.read()
        data = data.decode('utf-8')
        return data.encode('utf-8')


def users_page(environ, request):
    # get values of the users from the database
    sql = "SELECT * FROM users"
    mycursor.execute(sql)
    users = mycursor.fetchall()

    # Generate HTML for table rows dynamically
    table_rows = ''
    for row in users:
        user_id = row[7]
        user_name = row[0]
        user_email = row[6]
        user_phone = row[2]
        user_campus = row[3]
        user_faculty = row[4]
        user_program = row[5]

        table_rows += f'''
                    <tr>
                        <td>{user_id}</td>
                        <td>{user_name}</td>
                        <td>{user_email}</td>
                        <td>{user_phone}</td>
                        <td>{user_campus}</td>
                        <td>{user_faculty}</td>
                        <td>{user_program}</td>
                        <td>
                            <button class="view"><i class='bx bx-show'></i></button>
                            <button class="delete"><i class='bx bx-trash'></i></button>
                        </td>
                    </tr>
                '''

    with open('front_end/html/admin_users.html', 'rb') as file:
        data = file.read()
        data = data.replace(b'{table_rows}', table_rows.encode('utf-8'))
    return data


def timetable_page(environ, request):
    # get values of the timetable from the database in descending order
    sql = "SELECT * FROM timetable ORDER BY timetable_no DESC"
    mycursor.execute(sql)
    timetable = mycursor.fetchall()

    # Generate HTML for table rows dynamically
    table_rows = ''
    for row in timetable:
        course_code = row[1]
        course_title = row[2]
        course_lecturer = row[3]
        course_venue = row[4]
        course_day = row[5]
        course_time = row[6]

        table_rows += f'''
                    <tr>
                        <td>{course_code}</td>
                        <td>{course_title}</td>
                        <td>{course_lecturer}</td>
                        <td>{course_venue}</td>
                        <td>{course_day}</td>
                        <td>{course_time}</td>
                        <td>
                            <button class="view"><i class='bx bx-show'></i></button>
                            <button class="delete"><i class='bx bx-trash'></i></button>
                        </td>
                    </tr>
                '''

    with open('front_end/html/admin_timetables.html', 'rb') as file:
        data = file.read()

        data = data.replace(b'{table_rows}', table_rows.encode('utf-8'))

    return data


def conversation_page(environ, request):
    # get values of the conversations from the database in descending order
    sql = "SELECT * FROM conversations ORDER BY conversation_no DESC"
    mycursor.execute(sql)
    conversations = mycursor.fetchall()

    # Generate HTML for table rows dynamically
    table_rows = ''
    for row in conversations:
        user = row[1]
        message_sent = row[2]
        message_received = row[3]
        date_sent = row[4]
        time_sent = row[5]

        table_rows += f'''
                    <tr>
                        <td>{user}</td>
                        <td>{message_sent}</td>
                        <td>{message_received}</td>
                        <td>{date_sent}</td>
                        <td>{time_sent}</td>
                        <td>
                            <button class="view"><i class='bx bx-show'></i></button>
                        </td>
                    </tr>
                '''
    with open('front_end/html/admin_conversations.html', 'rb') as file:
        data = file.read()
        data = data.replace(b'{table_rows}', table_rows.encode('utf-8'))

    return data


def event_page(environ, request):
    # get values of the events from the database in descending order
    sql = "SELECT * FROM events ORDER BY event_date DESC"
    mycursor.execute(sql)
    events = mycursor.fetchall()

    # Generate HTML for table rows dynamically
    table_rows = ''
    for row in events:
        name = row[1]
        campus = row[2]
        venue = row[3]
        date = row[4]
        time = row[5]
        description = row[6]

        table_rows += f'''
                    <tr>
                        <td>{name}</td>
                        <td>{campus}</td>
                        <td>{venue}</td>
                        <td>{date}</td>
                        <td>{time}</td>
                        <td>{description}</td>
                        <td>
                            <button class="view"><i class='bx bx-show'></i></button>
                            <button class="delete"><i class='bx bx-trash'></i></button>
                        </td>
                    </tr>
                '''

    with open('front_end/html/admin_events.html', 'rb') as file:
        data = file.read()
        data = data.replace(b'{table_rows}', table_rows.encode('utf-8'))

    return data


def lecturer_page(environ, request):
    # get values of the lecturers from the database
    sql = "SELECT * FROM lecturers"
    mycursor.execute(sql)
    lecturers = mycursor.fetchall()

    # Generate HTML for table rows dynamically
    table_rows = ''
    for row in lecturers:
        name = row[1]
        email = row[2]
        phone = row[3]
        campus = row[4]
        office = row[5]
        department = row[6]
        faculty = row[7]

        table_rows += f'''
                    <tr>
                        <td>{name}</td>
                        <td>{email}</td>
                        <td>{phone}</td>
                        <td>{campus}</td>
                        <td>{office}</td>
                        <td>{department}</td>
                        <td>{faculty}</td>
                        <td>
                            <button class="view"><i class='bx bx-show'></i></button>
                            <button class="delete"><i class='bx bx-trash'></i></button>
                        </td>
                        
                    </tr>
                '''

    with open('front_end/html/admin_lecturers.html', 'rb') as file:
        data = file.read()
        data = data.replace(b'{table_rows}', table_rows.encode('utf-8'))

    return data


def add_lecturer_page(environ, request):
    with open('front_end/html/add_lecturer.html', 'rb') as file:
        data = file.read()
    return data


def add_event_page(request):
    if request.get('REQUEST_METHOD') == 'POST':
        try:
            # Get the data from the request
            size = int(request.get('CONTENT_LENGTH', 0))
        except ValueError:
            size = 0
        data = request['wsgi.input'].read(size)
        data = parse_qs(data)

        # Get the values from the data
        name = data.get(b'event-name', [b''])[0].decode('utf-8')
        campus = data.get(b'campus', [b''])[0].decode('utf-8')
        venue = data.get(b'venue', [b''])[0].decode('utf-8')
        date = data.get(b'event-date', [b''])[0].decode('utf-8')
        startTime = data.get(b'start-time', [b''])[0].decode('utf-8')
        stopTime = data.get(b'stop-time', [b''])[0].decode('utf-8')
        description = data.get(b'event-description', [b''])[0].decode('utf-8')

        # Join the start and stop time to a single string time
        time = startTime + '-' + stopTime

        # Insert the values into the database
        sql = "INSERT INTO events (event_no, event_name, event_campus, event_venue, event_date, event_time," \
              " event_description) VALUES (NULL, %(event_name)s, %(event_campus)s, %(event_venue)s, %(event_date)s, " \
              "%(event_time)s,%(event_description)s)"

        # create dictionary of event details
        event_details = {
            'event_name': name,
            'event_campus': campus,
            'event_venue': venue,
            'event_date': date,
            'event_time': time,
            'event_description': description
        }

        # check if a similar event exists
        ref_sql = "SELECT * FROM events WHERE event_name = %(event_name)s AND event_campus = %(event_campus)s AND " \
                  "event_venue = %(event_venue)s AND event_date = %(event_date)s AND event_time = %(event_time)s AND " \
                  "event_description = %(event_description)s"
        mycursor.execute(ref_sql, event_details)
        event = mycursor.fetchone()

        # if event exists, return error message
        if event:
            # Redirect to forget password page
            f = open('front_end/html/add_event.html', 'rb')
            data = f.read()
            data += generate_js_warning('Event already exist!').encode('utf-8')
            data = data.decode('utf-8')
            return data.encode('utf-8')
        else:
            # execute the sql query
            mycursor.execute(sql, event_details)
            mydb.commit()

            # Run event_json_generator.py
            generate_event_json()

            # Redirect to admin_events page
            f = open('front_end/html/loading_event_page.html', 'rb')
            data = f.read()
            data += generate_js_warning('Event added successfully!').encode('utf-8')
            data = data.decode('utf-8')
            return data.encode('utf-8')

    else:
        with open('front_end/html/add_event.html', 'rb') as file:
            data = file.read()
        return data


def loading_event_page(environ, request):
    with open('front_end/html/loading_event_page.html', 'rb') as file:
        data = file.read()
        train_bot()
    return data


def loading_timetable_page(environ, request):
    with open('front_end/html/loading_timetable_page.html', 'rb') as file:
        data = file.read()
        train_bot()
    return data


def loading_lecturer_page(environ, request):
    with open('front_end/html/loading_lecturer_page.html', 'rb') as file:
        data = file.read()
        train_bot()
    return data


def add_timetable_page(environ, request):
    with open('front_end/html/add_timetable.html', 'rb') as file:
        data = file.read()
    return data


# CSS and JS files

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


def admin_css(environ, request):
    with open('front_end/admin.css', 'rb') as file:
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


def admin_js(environ, request):
    with open('front_end/admin.js', 'rb') as file:
        data = file.read()
    return data
