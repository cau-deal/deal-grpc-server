from google.auth.transport import grpc
from sea.servicer import ServicerMeta

from app.decorators import verified
from app.extensions import pwdb

from app.decorators import unverified, verified
from protos.DealService_pb2_grpc import *
from protos.DealService_pb2 import *
from app.models import InquiryModel

from protos.CommonResult_pb2 import *

import datetime


class DealServiceServicer(DealServiceServicer, metaclass=ServicerMeta):
    @verified
    def Inquiry(self, request, context):
        inquiry = request.inquiry

        title = inquiry.title
        contents = inquiry.contents
        category = inquiry.category

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Inquiry result"

        Category = {
            InquiryCategory.UNKNOWN_INQUIRY_CATEGORY: "UNKNOWN",
            InquiryCategory.POINT: "POINT",
            InquiryCategory.PROJECT: "PROJECT",
            InquiryCategory.REGISTER: "REGISTER",
            InquiryCategory.ETC_INQUIRY: "ETC",
        }

        db = pwdb.database
        with db.atomic() as transaction:
            try:
                InquiryModel.create(
                    user_email=context.login_email,
                    title=title,
                    contents=contents,
                    is_complete=False,
                    category=Category[category],
                    created_at=datetime.datetime.now(),
                    answer_content="",
                )
            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)

        return InquiryResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
        )

    @verified
    def LookUpInquiry(self, request, context):
        return

    @verified
    def Accuse(self, request, context):
        accuse = request.accuse

        mission_id = accuse.mission_id
        contents = accuse.contents
        category = accuse.category

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Accuse result"

        Category = {
            InquiryCategory.UNKNOWN_INQUIRY_CATEGORY: "UNKNOWN",
            InquiryCategory.POINT: "INSULT",
            InquiryCategory.PROJECT: "ADVERTIESMENT",
            InquiryCategory.REGISTER: "ADULT",
            InquiryCategory.ETC_INQUIRY: "ETC",
        }

        db = pwdb.database
        with db.atomic() as transaction:
            try:
                InquiryModel.create(
                    user_email=context.login_email,
                    mission_id=mission_id,
                    is_complete=False,
                    category=Category[category],
                    created_at=datetime.datetime.now(),
                    contents=contents,
                )
            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)

        return InquiryResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
        )


