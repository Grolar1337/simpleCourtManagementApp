import re 
from functools import wraps
from sanic.response import json
from sanic import request
import jwt
from datetime import datetime, timedelta

secret_key='9-#O£yVt09O0J7P`S88"C£2`'

def encodeJWT(payload, expireDate):
    payload["exp"]=datetime.now() + timedelta( minutes=expireDate)
    encoded_token = jwt.encode(payload, secret_key, algorithm="HS512")
    return encoded_token

def decodeJWT(token):
    try:
        header_data = jwt.get_unverified_header(token)
        decoded_payload = jwt.decode(token, secret_key, algorithms=[header_data['alg'], ])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        return "expired"
    except jwt.DecodeError:
        return "corrupted"



def authorized(role):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):

            token = decodeJWT(request.cookies.get("jwt"))
            if token == "expired":
                return json({
                    "status": "error",
                    "message": "Verification token is expired"
                }, 403)
            
            elif token == "corrupted":
                return json({
                    "status": "error",
                    "message": "Verification token is corrupted"
                }, 403)
            
            elif token["admin"]==1 and role in ["admin","user"]:
                response = await f(request, token, *args, **kwargs)
                return response
            
            elif token["admin"]==0 and role=="user":
                response = await f(request, token, *args, **kwargs) 
                return response
            
            
            else:return json({"status": "not_authorized"}, 403)
        return decorated_function
    return decorator

class Validator:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def is_valid_username(self):
        # Username alfanumerik karakterlerden oluşmalı ve 3-30 karakter arasında olmalı
        if re.match(r'^[a-zA-Z0-9_]{3,30}$', self.username):
            return True
        return False

    def is_valid_email(self):
        # Basit bir email doğrulama regex'i kullanıyoruz
        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', self.email):
            return True
        return False

    def is_valid_password(self):
        # Şifre en az 8 karakter uzunluğunda olmalı ve en az bir harf ve bir rakam içermeli
        if len(self.password) >= 8 and re.search(r'[A-Za-z]', self.password) and re.search(r'\d', self.password):
            return True
        return False

    def validate(self):
        return {
            "username": self.is_valid_username(),
            "email": self.is_valid_email(),
            "password": self.is_valid_password()
        }
    

