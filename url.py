from operations import *

url_patterns = [
    ('/', login),
    ('/signUp', signup),
    ('/home', home),
    ('/home/profile', profile),
    ('/home/chat', chat),
    ('/pages/styling/main.css', mainCss),
    ('/pages/styling/auth.css', authCss),
    ('/pages/styling/main.js', mainJs),
    ('/pages/styling/404Error.css', notFoundCss),
    ('/pages/styling/boxicons.min.css', iconsCss),

]
