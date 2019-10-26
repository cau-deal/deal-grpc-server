from peewee import fn
from sea.servicer import ServicerMeta

from app.decorators import verified
from app.extensions import pwdb
from app.models import NoticeModel, User, PushLog

from protos.CommonResult_pb2 import *
from protos.Datetime_pb2 import *
from protos.NotificationService_pb2 import *
from protos.NotificationService_pb2_grpc import *


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
                )

                user_query = User.select()

                # 모든 사용자에게 push를 보내는 부분(지금은 db 저장만 수행)
                for row in user_query:
                    PushLog.create(
                        receiver_email=row.email,
                        content=content,
                    )

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

