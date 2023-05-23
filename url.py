from operations import *

url_patterns = [
    ('/', login),
    ('/signUp', signup),
    ('/home', home),
    ('/home/profile', profile),
    ('/home/chat', chat),
    ('/pages/styling/main.css', mainCss),
    ('/pages/styling/signUp.css', signUpCss),
    ('/pages/styling/main.js', mainJs),
    ('/pages/styling/404Error.css', notFoundCss),
    ('/pages/styling/boxicons.min.css', iconsCss),

]
