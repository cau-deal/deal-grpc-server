import time

import jwt
import datetime


class JWT:

    def __init__(self):
        self.secret = 'secret'
        self.algorithm = 'HS256'
        self.iss = 'deal-server'
        self.aud = 'deal-grpc'
        self.lifetime_for_access = 2.0,  # hours
        self.lifetime_for_refresh = 14,  # days

        # TODO MAKE ENUM
        self.State = {
            'UNKNOWN': 0,
            'VALID': 1,
            'INVALID': 2,
        }

    def validate(self, token):
        payload = jwt.decode(token, self.secret, issuer=self.iss, audience=self.aud, algorithms=self.algorithm)
        return payload['sub']

    # token is access token
    def decode(self, token):
        return jwt.decode(token, self.secret, issuer=self.iss, audience=self.aud, algorithms=self.algorithm)

    def get_access_token(self, email):
        return jwt.encode({
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
            'iat': time.time(),
            'sub': email,
            'aud': self.aud,
            'iss': self.iss
        }, self.secret, algorithm=self.algorithm)

    def get_refresh_token(self, email, access_token):
        return jwt.encode({
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=14),
            'iat': time.time(),
            'aud': self.aud,
            'iss': self.iss,
            'sub': email
        }, self.secret, algorithm=self.algorithm) if self.validate(access_token) else ""

