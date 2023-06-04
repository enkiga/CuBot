from operations import *

url_patterns = [
    ('/', login_page),
    ('/loading', loading_page),
    ('/home', home_page),
    ('/signup', signup_page),
    ('/forgot_password', forgot_password_page),
    ('/recovery', recovery_page),
    ('/reset_password', reset_password_page),
    ('/change_password', change_password_page),
    ('/chat', chat_page),
    ('/profile', profile_page),
    ('/logout', logout),
    ('loading_logout', loading_logout),
    ('/front_end/root.css', root_css),
    ('/front_end/login.css', login_css),
    ('/front_end/signup.css', signup_css),
    ('/front_end/root.js', root_js),
    ('/front_end/signup.js', signup_js),
]
