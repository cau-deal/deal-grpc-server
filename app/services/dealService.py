from google.auth.transport import grpc
from sea.servicer import ServicerMeta

from app.decorators import verified
from app.extensions import pwdb

from app.decorators import unverified, verified
from protos.DealService_pb2_grpc import *
from protos.DealService_pb2 import *
from app.models import InquiryModel

import datetime


class DealServiceServicer(DealServiceServicer, metaclass=ServicerMeta):
    @verified
    def Inquiry(self, request, context):
        inquiry = request.inquiry

        title = inquiry.title
        contents = inquiry.contents
        user_email = context.user_email

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown"

        db = pwdb.database
        with db.atomic() as transaction:
            try:
                InquiryModel.create(
                    user_email = user_email,
                    title = title,
                    contents = contents,
                    is_complete = 0,
                    category = "Unknown Value",
                    created_at = datetime.datetime.now(),
                    answer_content = "",
                )
            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)

        return InquiryResponse(
            result = CommonResult(
                result_code = result_code,
                message = result_message,
            ),
        )

    @verified
    def LookUpInquiry(self, request, context):
        return

    @verified
    def Accuse(self, request, context):
        return


