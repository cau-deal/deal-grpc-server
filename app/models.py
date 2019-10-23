import datetime

from app.extensions import pwdb
import peewee


class User(pwdb.Model):
    email = peewee.CharField(primary_key=True)
    password = peewee.CharField()
    level = peewee.IntegerField(default=0)
    state = peewee.IntegerField(default=0)
    role = peewee.IntegerField(default=1)
    register_type = peewee.IntegerField(default=0)
    agree_with_terms = peewee.BooleanField(default=False)
    is_phone_authentication = peewee.IntegerField()
    is_account_authentication = peewee.IntegerField()
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


class Mission(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    register_email = peewee.ForeignKeyField(User, column_name='register_email')
    title = peewee.CharField(max_length=255, null=False)
    contents = peewee.TextField()
    mission_type = peewee.IntegerField()
    data_type = peewee.IntegerField()
    state = peewee.IntegerField(default=0)
    unit_package = peewee.IntegerField()
    price_of_package = peewee.IntegerField()
    order_package_quantitiy = peewee.IntegerField()
    deadline = peewee.DateTimeField()
    created_at = peewee.DateTimeField()
    summary = peewee.CharField(max_length=255, null=True)
    contact_clause = peewee.TextField(null=True)
    specification = peewee.TextField(null=True)

    class Meta:
        db_table = 'mission'


class ConductMission(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    worker_email = peewee.CharField()
    mission_id = peewee.IntegerField()
    state = peewee.IntegerField()
    deadline = peewee.DateTimeField()
    created_at = peewee.DateTimeField()
    complete_datetime = peewee.DateTimeField()

    class Meta:
        db_table = 'conduct_mission'


class MissionExplanationImage(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    mission_id = peewee.ForeignKeyField(Mission, column_name='mission_id')
    image_type = peewee.IntegerField()
    url = peewee.CharField()
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'mission_explanation_image'


# Deal Service

class InquiryModel(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    user_email = peewee.CharField()
    title = peewee.CharField()
    contents = peewee.TextField()
    is_complete = peewee.IntegerField()
    category = peewee.CharField()
    created_at = peewee.DateTimeField()
    answer_content = peewee.TextField()

    class Meta:
        db_table = 'inquiry'


# PhoneAuth
class PhoneAuthentication(pwdb.Model):
    user_email = peewee.ForeignKeyField(User, column_name='user_email')
    phone_num = peewee.CharField()
    name = peewee.CharField()
    mobile_carrier = peewee.CharField()
    sex = peewee.IntegerField()
    is_native = peewee.BooleanField()
    birth = peewee.DateField()
    created_at = peewee.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'phone_authentication'


# PhoneAuth
class AccountAuthentication(pwdb.Model):
    user_email = peewee.ForeignKeyField(User, column_name='user_email')
    account_num = peewee.CharField()
    name = peewee.CharField()
    bank = peewee.CharField()
    created_at = peewee.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'account_authentication'
