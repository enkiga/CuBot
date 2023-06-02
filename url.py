from operations import *

url_patterns = [
    ('/', login_page),
    ('/loading', loading_page),
    ('/home', home_page),
    ('/signup', signup_page),
    ('/chat', chat_page),
    ('/profile', profile_page),
    ('/front_end/root.css', root_css),
    ('/front_end/login.css', login_css),
    ('/front_end/signup.css', signup_css),
    ('/front_end/root.js', root_js),
    ('/front_end/signup.js', signup_js),
]
