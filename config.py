import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bike-garage-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://root:Rushi%40532@localhost/bikegarage'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE       = os.environ.get('TWILIO_PHONE')

    ANTHROPIC_API_KEY  = os.environ.get('ANTHROPIC_API_KEY')
    GROQ_API_KEY       = os.environ.get('GROQ_API_KEY')

    MAIL_SERVER        = 'smtp.gmail.com'
    MAIL_PORT          = 587
    MAIL_USE_TLS       = True
    MAIL_USERNAME      = os.environ.get('MAIL_EMAIL')
    MAIL_PASSWORD      = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_EMAIL')


# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'bike-garage-secret-key'
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
#         'mysql://root:Rushi%40532@localhost/bikegarage'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
    
#     TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
#     TWILIO_AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN')
#     TWILIO_PHONE       = os.environ.get('TWILIO_PHONE')
    
#     ANTHROPIC_API_KEY  = os.environ.get('ANTHROPIC_API_KEY')