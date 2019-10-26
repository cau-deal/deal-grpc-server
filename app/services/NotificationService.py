from peewee import fn
from sea.servicer import ServicerMeta

from app.decorators import verified
from app.extensions import pwdb
from app.models import NoticeModel, User, PushLog
from protos.CommonResult_pb2 import ResultCode, CommonResult
from protos.NotificationService_pb2 import PostNoticeResponse
from protos.NotificationService_pb2_grpc import NotificationServiceServicer


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
                         .where((PushLog.receiver_email == context.login_email) & PushLog.is_read))

                for row in query:
                    count = row.count

                result_code = ResultCode.SUCCESS
                result_message = "count no read success"

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
    def GetPushList(self, request, context):
        pass

    @verified
    def ReadPush(self, request, context):
        pass

