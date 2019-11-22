import datetime
from peewee import *
from playhouse.db_url import connect
import pymysql

DB_URL = 'mysql+pool://deal:deal1234@deal.ct7ygagy10fd.ap-northeast-2.rds.amazonaws.com:3306/deal'

db = connect(DB_URL)

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    email = CharField(primary_key=True)
    password = CharField()
    level = IntegerField(default=0)
    state = IntegerField(default=1)
    role = IntegerField(default=1)
    register_type = IntegerField(default=0)
    agree_with_terms = BooleanField(default=False)
    is_phone_authentication = IntegerField()
    is_account_authentication = IntegerField()
    profile_photo_url = IntegerField()
    last_login_datetime = DateTimeField(default=datetime.datetime.now())
    created_at = DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'user'

class MissionModel(BaseModel):
    id = IntegerField(primary_key=True)
    register_email = ForeignKeyField(User, column_name='register_email')
    title = CharField()
    contents = TextField()
    mission_type = IntegerField()
    data_type = IntegerField()
    state = IntegerField(default=1)
    unit_package = IntegerField()
    price_of_package = IntegerField()
    order_package_quantity = IntegerField()
    beginning = DateTimeField()
    deadline = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now())
    summary = CharField(null=True)
    contact_clause = TextField(null=True)
    specification = TextField(null=True)

    class Meta:
        db_table = 'mission'

class ConductMission(BaseModel):
    id = IntegerField(primary_key=True)
    worker_email = ForeignKeyField(User, column_name='worker_email')
    mission_id = ForeignKeyField(MissionModel, column_name='mission_id')
    state = IntegerField(default=1)
    deadline = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now())
    complete_datetime = DateTimeField(null=True)

    class Meta:
        db_table = 'conduct_mission'
        

missions = MissionModel.select(MissionModel.id, MissionModel.state, MissionModel.deadline)
conduct_missions = ConductMission.select(ConductMission.id, ConductMission.state, ConductMission.deadline)

now_time = datetime.datetime.now()

# Mission State Update
for row in missions.dicts():
    mission_id = row['id']
    mission_state = row['state']
    mission_deadline = row['deadline']
    with db.atomic() as transaction:
        try:
            if(mission_state==4):
                pass

            if now_time >= mission_deadline:
                MissionModel.update(state=4).where(MissionModel.id == mission_id).execute()
        except Exception as e:
            transaction.rollback()
            print("Mission ID "+str(mission_id)+" state update failed.")
            pass

print(str(now_time)+" Mission complete state update finished.")

for row in conduct_missions.dicts():
    mission_id = row['id']
    mission_state = row['state']
    mission_deadline = row['deadline']
    with db.atomic() as transaction:
        try:
            if(mission_state==4):
                pass

            if now_time >= mission_deadline:
                ConductMission.update(state=4).where(ConductMission.id == mission_id).execute()
        except Exception as e:
            transaction.rollback()
            print(e)
            print("Conduct Mission ID "+str(mission_id)+" state update failed.")
            pass

print(str(now_time)+" Conduct Mission complete state update finished.")