from firebase_admin import messaging
from app.extensions import pwdb
from protos.NotificationService_pb2 import *
from protos.NotificationService_pb2_grpc import *
from app.models import PushLog, FCMModel

import datetime

def verified(func):
    # args[0] => self, args[1] => request, args[2] => context
    def wrapper(*args, **kw):
        return func(*args, **kw) if args[2].verified else None

    return wrapper


def unverified(func):
    # args[0] => self, args[1] => request, args[2] => context
    def wrapper(*args, **kw):
        return func(*args, **kw)

    return wrapper


def silent_notification(func):
    # args[0] => self, args[1] => request, args[2] => context
    def wrapper(*args, **kw):
        result = func(*args, **kw)
        req = args[1]
        fcm_query = FCMModel.select(FCMModel.fcm_key).where(FCMModel.user_email == args[2].login_email)
        for row in fcm_query:
            message = messaging.Message(
            android=messaging.AndroidConfig(
                ttl=datetime.timedelta(seconds=3600),
                priority='normal',
                ),
                data={
                    'score': '850',
                    'time': '2:45',
                },
                token=row.fcm_key,
            )

            try:
                response = messaging.send(message)
            except Exception as ee:
                print("key is not valid.")
                pass

            PushLog.create(
                receiver_email=args[2].login_email,
                content="이거 바꿔야해 승현아",
            )

        return result

    return wrapper




def notification(func):
    # args[0] => self, args[1] => request, args[2] => context
    def wrapper(*args, **kw):
        result = func(*args, **kw)
        req = args[1]
        fcm_query = FCMModel.select(FCMModel.fcm_key).where(FCMModel.user_email == args[2].login_email)
        for row in fcm_query:
            message = messaging.Message(
            android=messaging.AndroidConfig(
                ttl=datetime.timedelta(seconds=3600),
                priority='normal',
                notification=messaging.AndroidNotification(
                    title='제목',
                    body='내용',
                    icon='',
                    color='#f45342',
                    sound='default'
                ),
                ),
                data={
                    'score': '850',
                    'time': '2:45',
                },
                token=row.fcm_key,
            )

            try:
                response = messaging.send(message)
            except Exception as ee:
                print("key is not valid.")
                pass

            PushLog.create(
                receiver_email=args[2].login_email,
                content="이거 바꿔야해 승현아",
            )

        return result

    return wrapper
