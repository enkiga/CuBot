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


def signup(request):
    f = open("pages/signup.html", "rb")
    data = f.read()
    return data


def home(environ):
    f = open("pages/home.html", "rb")
    data = f.read()
    return data


def mainCss(environ):
    with open("pages/styling/main.css", "rb") as f:
        data = f.read()
    return data


def signUpCss(environ):
    with open("pages/styling/signUp.css", "rb") as f:
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
