from operations import *

url_patterns = [
    ('/', login_page),
    ('/home', home_page),
    ('/signup', signup_page),
    ('/front_end/root.css', root_css),
    ('/front_end/root.js', root_js),
]
