import datetime

from app.extensions import pwdb
import peewee


class User(pwdb.Model):
    email = peewee.CharField(primary_key=True)
    password = peewee.CharField()
    level = peewee.IntegerField(default=0)
    state = peewee.IntegerField(default=0)
    role = peewee.IntegerField(default=1)
    type = peewee.IntegerField(default=0)
    agree_with_terms = peewee.BooleanField(default=False)
    phone_authentication_id = peewee.IntegerField()
    account_authentication_id = peewee.IntegerField()
    profile_photo_url = peewee.IntegerField()
    last_login_datetime = peewee.DateTimeField(default=datetime.datetime.now())
    created_at = peewee.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'user'


class JWTToken(pwdb.Model):
    token_key = peewee.CharField(primary_key=True)
    user_email = peewee.CharField()
    created_at = peewee.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = "jwt_token"
