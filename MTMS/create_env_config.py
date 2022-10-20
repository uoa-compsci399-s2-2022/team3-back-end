import os


def create_env():
    if not os.path.exists('.env'):
        env = open('.env', 'w')
        env.write('''

PROJECT_DOMAIN='https://uoamtms.com/'

# Flask variables
# ---------------
FLASK_APP='wsgi.py'
DEBUG=True
FLASK_DEBUG=True
SECRET_KEY='13485912170539ae2d833f5d4837a9b1f8606e4caad25da506d3a8d2f106c134'         # Used to encrypt session data.

# WTForm variables
# ----------------
WTF_CSRF_SECRET_KEY='eaa20ae54efc612834fe728fccc76701ad1ca9f7f216a8f8132a374d2d827227'  # Needed by Flask WTForms to combat cross-site request forgery.

# Database variables
# ------------------
SQLALCHEMY_DATABASE_URI = 'sqlite:///MTMS.db'         # sqlite
SQLALCHEMY_ECHO=False               # echo SQL statements when working with database
#SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:Zhq5822??vk@localhost:3306/MTMS'         # Mysql



# Email
# ------------------
EMAIL_ACCOUNT=''
EMAIL_PASSWORD=''
EMAIL_SENDER_ADDRESS=''
EMAIL_SERVER_HOST=''
EMAIL_SERVER_PORT=587
EMAIL_SERVER_SSL_PORT=465
EMAIL_SENDER_NAME=""


# Auth
# ------------------
TOKEN_EXPIRATION=36000
VALIDATION_CODE_EXPIRATION=300


# Restful API
# ------------------
JSON_SORT_KEYS=False


# Flase APScheduler
# ------------------
SCHEDULER_API_ENABLED = True
''')
        env.close()
