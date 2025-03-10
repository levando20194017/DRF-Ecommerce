# accounts.utils
import datetime
import jwt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_access_token(user):

    access_token_payload = {
        'email': user.email,
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=500),
        'iat': datetime.datetime.utcnow(),
    }
    access_token = jwt.encode(access_token_payload,
                              os.getenv('SECRET_KEY'), algorithm='HS256')
    return access_token


def generate_refresh_token(user):
    refresh_token_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    refresh_token = jwt.encode(
        refresh_token_payload, os.getenv('SECRET_KEY'), algorithm='HS256')

    return refresh_token