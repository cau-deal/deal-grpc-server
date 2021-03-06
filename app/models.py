import datetime

from app.extensions import pwdb
import peewee


class User(pwdb.Model):
    email = peewee.CharField(primary_key=True)
    password = peewee.CharField()
    level = peewee.IntegerField(default=0)
    state = peewee.IntegerField(default=1)
    role = peewee.IntegerField(default=1)
    register_type = peewee.IntegerField(default=0)
    agree_with_terms = peewee.BooleanField(default=False)
    is_phone_authentication = peewee.IntegerField()
    is_account_authentication = peewee.IntegerField()
    profile_photo_url = peewee.CharField()
    last_login_datetime = peewee.DateTimeField()
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'user'


class JWTToken(pwdb.Model):
    token_key = peewee.CharField(primary_key=True)
    user_email = peewee.CharField()
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = "jwt_token"


class MissionModel(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    register_email = peewee.ForeignKeyField(User, column_name='register_email')
    title = peewee.CharField()
    contents = peewee.TextField()
    mission_type = peewee.IntegerField()
    data_type = peewee.IntegerField()
    state = peewee.IntegerField(default=1)
    unit_package = peewee.IntegerField()
    price_of_package = peewee.IntegerField()
    order_package_quantity = peewee.IntegerField()
    beginning = peewee.DateTimeField()
    deadline = peewee.DateTimeField()
    created_at = peewee.DateTimeField()
    summary = peewee.CharField(null=True)
    contact_clause = peewee.TextField(null=True)
    specification = peewee.TextField(null=True)

    class Meta:
        db_table = 'mission'


class ConductMission(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    worker_email = peewee.ForeignKeyField(User, column_name='worker_email')
    mission_id = peewee.ForeignKeyField(MissionModel, column_name='mission_id')
    state = peewee.IntegerField(default=1)
    deadline = peewee.DateTimeField()
    created_at = peewee.DateTimeField()
    complete_datetime = peewee.DateTimeField(null=True)

    class Meta:
        db_table = 'conduct_mission'


class MissionExplanationImageModel(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    mission_id = peewee.ForeignKeyField(MissionModel, column_name='mission_id')
    image_type = peewee.IntegerField()
    url = peewee.CharField()
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'mission_explanation_image'

class ImageDataForRequestMission(pwdb.Model):
    url = peewee.CharField(primary_key=True)
    mission_id = peewee.ForeignKeyField(MissionModel, column_name='mission_id')
    state = peewee.IntegerField(default=1)
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'image_data_for_request_mission'

class ProcessedImageDataModel(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    image_data_for_request_mission_url = peewee.ForeignKeyField(ImageDataForRequestMission,
                                                                column_name='image_data_for_request_mission_url')
    conduct_mission_id = peewee.ForeignKeyField(ConductMission, column_name='conduct_mission_id')
    created_at = peewee.DateTimeField()
    labeling_result = peewee.TextField(null=True)

    class Meta:
        db_table = 'processed_image_data'

class ImageDataModel(pwdb.Model):
    url = peewee.CharField(primary_key=True)
    conduct_mission_id = peewee.ForeignKeyField(ConductMission, column_name='conduct_mission_id')
    state = peewee.IntegerField(default=3)
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'image_data'

class SoundDataModel(pwdb.Model):
    url = peewee.CharField(primary_key=True)
    conduct_mission_id = peewee.ForeignKeyField(ConductMission, column_name='conduct_mission_id')
    state = peewee.IntegerField(default=3)
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'sound_data'

class SurveyDataModel(pwdb.Model):
    url = peewee.CharField(primary_key=True)
    conduct_mission_id = peewee.ForeignKeyField(ConductMission, column_name='conduct_mission_id')
    state = peewee.IntegerField(default=3)
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'survey_data'

class LabelModel(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    mission_id = peewee.ForeignKeyField(MissionModel, column_name='mission_id')
    label = peewee.CharField()
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'label'

# Deal Service

class InquiryModel(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    user_email = peewee.ForeignKeyField(User, column_name='user_email')
    title = peewee.CharField()
    contents = peewee.TextField()
    is_complete = peewee.BooleanField()
    category = peewee.CharField()
    created_at = peewee.DateTimeField()
    answer_content = peewee.TextField()

    class Meta:
        db_table = 'inquiry'

class AccuseModel(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    user_email = peewee.ForeignKeyField(User, column_name='user_email')
    mission_id = peewee.ForeignKeyField(MissionModel, column_name='mission_id')
    is_complete = peewee.BooleanField()
    category = peewee.CharField()
    created_at = peewee.DateTimeField()
    contents = peewee.TextField()

    class Meta:
        db_table = 'accuse'

# PhoneAuth
class PhoneAuthentication(pwdb.Model):
    user_email = peewee.ForeignKeyField(User, column_name='user_email')
    phone_num = peewee.CharField()
    name = peewee.CharField()
    mobile_carrier = peewee.CharField()
    sex = peewee.IntegerField()
    is_native = peewee.BooleanField()
    birth = peewee.DateField()
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'phone_authentication'

# PhoneAuth
class AccountAuthentication(pwdb.Model):
    user_email = peewee.ForeignKeyField(User, column_name='user_email')
    account_num = peewee.CharField()
    name = peewee.CharField()
    bank = peewee.CharField()
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'account_authentication'

# Point
class WithdrawPoint(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    user_email = peewee.ForeignKeyField(User, column_name='user_email')
    val = peewee.IntegerField()
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'withdraw_point'

class DepositPoint(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    user_email = peewee.ForeignKeyField(User, column_name='user_email')
    val = peewee.IntegerField()
    kind = peewee.IntegerField()
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'deposit_point'

class TransferPoint(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    sender_email = peewee.ForeignKeyField(User, column_name='sender_email')
    receiver_email = peewee.ForeignKeyField(User, column_name='receiver_email')
    val = peewee.IntegerField()
    created_at = peewee.DateTimeField()
    mission_id = peewee.ForeignKeyField(MissionModel, column_name='mission_id', null=True)

    class Meta:
        db_table = 'transfer_point'

class NoticeModel(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    title = peewee.CharField()
    content = peewee.TextField()
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'notice'

class PushLog(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    receiver_email = peewee.ForeignKeyField(User, column_name='receiver_email')
    content = peewee.TextField()
    is_read = peewee.BooleanField(default=False)
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'push_log'

class FCMModel(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    user_email = peewee.ForeignKeyField(User, column_name='user_email')
    fcm_key = peewee.CharField()
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'fcm'

class KakaoPayModel(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    user_email = user_email = peewee.ForeignKeyField(User, column_name='user_email')
    tid = peewee.CharField()
    state = peewee.IntegerField()
    val = peewee.IntegerField()
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'kakaopay'

class RecommendMission(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    mission_id = peewee.ForeignKeyField(MissionModel, column_name='mission_id')
    url = peewee.CharField()
    created_at = peewee.DateTimeField()

    class Meta:
        db_table = 'recommend_mission'

class MissionSurveyMap(pwdb.Model):
    id = peewee.IntegerField(primary_key=True)
    mission_id = peewee.ForeignKeyField(MissionModel, column_name='mission_id')
    surveys_id = peewee.IntegerField()

    class Meta:
        db_table = 'mission_survey_map'

