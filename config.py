import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Super-Secret-Ultra-Secure-MEGA-OVERDRIVE-OMEGA-STRING'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REMEMBER_COOKIE_DURATION = os.environ.get('REMEMBER_COOKIE_DURATION') or 30
    if REMEMBER_COOKIE_DURATION == 30:
        REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    print(f'SERVER: {os.environ.get("MAIL_SERVER")}, PORT: {os.environ.get("MAIL_PORT")}')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['chroniclewebapp@gmail.com']

    STRAINS_PER_PAGE = 2
    SEARCH_RESULTS = 5
