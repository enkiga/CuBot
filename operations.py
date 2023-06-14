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
            data = data.replace(b'{{lastname}}', b'')

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
        tag = intents_list[0]['intent']
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
    if request.get('REQUEST_METHOD') == 'POST':
        try:
            # Get the data from the request
            size = int(request.get('CONTENT_LENGTH', 0))
        except ValueError:
            size = 0
        data = request['wsgi.input'].read(size)
        data = parse_qs(data)

        # Get the user input
        user_input = data.get(b'user_input', [b''])[0].decode('utf-8')
        print(user_input)

        # Process user text and get response
        ints = predict_class(user_input, words, classes)

        # get intents.json file
        with open('intents.json') as file:
            intent = json.load(file)

        bot_response = get_response(ints, intent)
        print(bot_response)

        # Prepare response data
        response_data = {
            'user_input': user_input,
            'bot_response': bot_response
        }
        response_body = json.dumps(response_data)

        # Send response
        return response_body.encode('utf-8')

    else:
        with open('front_end/html/chat_page.html', 'rb') as file:
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


def root_js(environ, request):
    with open('front_end/root.js', 'rb') as file:
        data = file.read()
    return data


def signup_js(environ, request):
    with open('front_end/signup.js', 'rb') as file:
        data = file.read()
    return data
