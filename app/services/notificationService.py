from peewee import fn
from sea.servicer import ServicerMeta

from app.decorators import verified
from app.extensions import pwdb
from app.models import NoticeModel, User, PushLog, FCMModel

from protos.CommonResult_pb2 import *
from protos.Datetime_pb2 import *
from protos.NotificationService_pb2 import *
from protos.NotificationService_pb2_grpc import *

import datetime
from firebase_admin import messaging

class NotificationServiceServicer(NotificationServiceServicer, metaclass=ServicerMeta):
    @verified
    def PostNotice(self, request, context):
        notice = request.notice

        title = notice.title
        content = notice.content

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown post notice Result"

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                # notice를 작성
                NoticeModel.create(
                    title=title,
                    content=content,
                    created_at=datetime.datetime.now(),
                )

                user_query = (FCMModel
                .select(FCMModel.user_email, FCMModel.fcm_key))

                # 모든 사용자에게 push를 보내는 부분
                for row in user_query:
                    message = messaging.Message(
                    android=messaging.AndroidConfig(
                        ttl=datetime.timedelta(seconds=3600),
                        priority='normal',
                        notification=messaging.AndroidNotification(
                            title='알림인데',
                            body='백그라운드 자비 좀',
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

                        PushLog.create(
                            receiver_email=row.user_email,
                            content=content,
                            created_at=datetime.datetime.now()
                        )

                    except Exception as ee:
                        print(str(row.user_email)+"'s key is not valid.")
                        pass

                result_code = ResultCode.SUCCESS
                result_message = "post notice success"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                print("EXCEPTION: " + str(e))

        return PostNoticeResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
        )

    @verified
    def CountNoReadPush(self, request, context):
        count = 0

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown count no read push Result"

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                query = (PushLog.select(fn.count(PushLog.id).alias('count'))
                         .where((PushLog.receiver_email == context.login_email) & (PushLog.is_read == False)))

                for row in query:
                    count = row.count

                result_code = ResultCode.SUCCESS
                result_message = "count no read success"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                print("EXCEPTION: " + str(e))

        return CountNoReadPushResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            count=count,
        )

    @verified
    def GetPushList(self, request, context):
        push_lists = []

        is_read_push_type = request.is_read_push_type

        IS_READ_PUSH_TYPE = {
            IsReadPushType.UNKNOWN_IS_READ_PUSH_TYPE: 0,
            IsReadPushType.NOT_READ_IS_READ_PUSH_TYPE: 1,
            IsReadPushType.READ_IS_READ_PUSH_TYPE: 2,
            IsReadPushType.ALL_IS_READ_PUSH_TYPE: 3,
        }

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown get push list Result"

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                if is_read_push_type == IS_READ_PUSH_TYPE[IsReadPushType.NOT_READ_IS_READ_PUSH_TYPE]:
                    query = (PushLog.select().where((PushLog.receiver_email == context.login_email) &
                                                    (PushLog.is_read == False)))
                elif is_read_push_type == IS_READ_PUSH_TYPE[IsReadPushType.READ_IS_READ_PUSH_TYPE]:
                    query = (PushLog.select().where((PushLog.receiver_email == context.login_email) &
                                                    (PushLog.is_read == True)))
                elif is_read_push_type == IS_READ_PUSH_TYPE[IsReadPushType.ALL_IS_READ_PUSH_TYPE]:
                    query = (PushLog.select().where((PushLog.receiver_email == context.login_email)))
                else:
                    raise Exception("UNKNOWN_IS_READ_PUSH_TYPE")

                result_code = ResultCode.SUCCESS
                result_message = "get push list success"

                for row in query:
                    c = row.created_at
                    push_lists.append(
                        Push(
                            id=row.id,
                            content=row.content,
                            is_read=row.is_read,
                            created_at=Datetime(year=c.year, month=c.month, day=c.day,
                                                hour=c.hour, min=c.minute, sec=c.second)
                        )
                    )

                push_lists.reverse()

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                print("EXCEPTION: " + str(e))

        return GetPushListResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            push_list=push_lists,
        )

    @verified
    def ReadPush(self, request, context):
        push_id = request.push_id

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown read push Result"

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                query = (PushLog.update(is_read=True).where(PushLog.id == push_id).execute())

                if query == 0:
                    print("UPDATE ERROR")
                    raise Exception("read push UPDATE ERROR")

                result_code = ResultCode.SUCCESS
                result_message = "read push success"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                print("EXCEPTION: " + str(e))

        return ReadPushResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
        )

    @verified
    def TransmitFCM(self, request, context):
        fcm_key = request.fcm.fcm_key

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown read push Result"

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                isFCMExist = (FCMModel.select(fn.Count(FCMModel.user_email).alias('isExist'))
                                 .where(FCMModel.user_email == context.login_email))

                email_number_cnt=0

                for row in isFCMExist:
                    if row.isExist is not None:
                        email_number_cnt += row.isExist

                print(context.login_email, email_number_cnt)

                if(email_number_cnt >= 1):
                    FCMModel\
                    .update(fcm_key = fcm_key, created_at = datetime.datetime.now())\
                    .where(FCMModel.user_email == context.login_email).execute()
                    result_code = ResultCode.SUCCESS
                    result_message = "FCM Key update success"
                else:
                    FCMModel.create(
                        fcm_key = fcm_key,
                        user_email=context.login_email,
                        created_at=datetime.datetime.now(),
                    )
                    result_code = ResultCode.SUCCESS
                    result_message = "FCM Key create success"


            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                print("EXCEPTION: " + str(e))

        return TransmitFCMResponse(
            result = CommonResult(
                result_code = result_code,
                message = result_message,
            ),
        )