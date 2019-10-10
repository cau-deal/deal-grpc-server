import time

import jwt
import datetime


class JWT:

    def __init__(self):
        self.secret = 'secret'
        self.algorithm = 'HS256'
        self.iss = 'deal-server'
        self.lifetime_for_access = 2.0,  # hours
        self.lifetime_for_refresh = 14,  # days

        # TODO MAKE ENUM
        self.State = {
            'UNKNOWN': 0,
            'VALID': 1,
            'INVALID': 2,
        }

    def validate(self, token, email):
        payload = jwt.decode(token, self.secret, issuer=self.iss, audience=email, algorithms=self.algorithm)
        return True

    # token is access token
    def decode(self, token, email):
        return jwt.decode(token, self.secret, issuer=self.iss, audience=email, algorithms=self.algorithm)

    def get_access_token(self, email):
        return jwt.encode({
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
            'iat': time.time(),
            'aud': email, 'iss': self.iss
        }, self.secret, algorithm=self.algorithm)

    def get_refresh_token(self, email, token):
        return jwt.encode({
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=14)
        }, self.secret, algorithm=self.algorithm) if self.validate(token, email) else ""

