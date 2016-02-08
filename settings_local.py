DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'demo_oscar',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',# Not used with sqlite3.
        'PASSWORD': '123456',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#STATIC_URL = 'http://oscar.dev:8080/'
STATIC_URL = '/static/'
WATERMARK_LOGO = STATIC_URL + 'images/uniweb_logo.png'
MY_WALL_POST_MESSAGE_PER_PAGE = 3
INSTAGRAM_APPS = {
    'CLIENT_ID': '7b671b66155d440cbd99b31f411b552e',
    'CLIENT_SECRET': 'b4bfe201940442c3b70488aace51008f'
}

TWITTER_API_KEY = 'apnHlhNqaLr3Rjmb8l9D2yGzU'
TWITTER_COMSUMER_KEY = 'apnHlhNqaLr3Rjmb8l9D2yGzU'
TWITTER_COMSUMER_SECRET = 'OUTzpVBA59i9x6lMJul5t16ZdAVQkK7Tvvcu7KRY2l9f2olFzA'
TWITTER_ACCESS_TOKEN = '260645246-XIa1SCCE1GYMAzawzGq4Ky4LFpFfdt28fmJaVouh'
TWITTER_ACCESS_TOKEN_SECRET = '7of2sE4a6VACoo6vCzJc0zUqPD8Q2zN2gA3sUxGyVTw2X'
REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authenticate'
SIGNIN_URL = 'https://api.twitter.com/oauth/authenticate'

CALLBACK_URL = ""

FACEBOOK_APPS = {
    'demo_oscar': {
        'ID': '131388503698398',
        'PATH': 'demo_oscar_testing:add',
        'SECRET': '77ae73481cfab11ef265c5da841fc295',
        'CANVAS-PAGE': 'https://www.facebook.com/appcenter/demo_oscar_testing?preview=1&locale=en_US',
        'CANVAS-URL': '',
        'SECURE-CANVAS-URL': '',
        'REDIRECT-URL': '',
        'DOMAIN': 'demo-oscar.dev',
    }
}
