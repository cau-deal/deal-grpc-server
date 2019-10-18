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
        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown LookUpInquiry"

        db = pwdb.database
        with db.atomic as transaction:
            try:
                query = (Inquiry
                    .select()
                    .where(Inquiry.user_email == context.login_email))

                result_code = ResultCode.SUCCESS
                result_message = "Successful look up inquiry"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)

            inquiry_with_answer = []

            # Row = (id, user_email, title, contents, is_complete, category, created_at, answer_cont)
            for row in query:
                inquiry_with_answer.append(
                    inquiry = Inquiry(
                        title=row.title,
                        contents=row.contents,
                        is_complete=row.is_complete,
                        category=row.category,
                        created_at=row.created_at,
                        answer_content=answer_content,
                    ),
                    is_complete = row.is_complete,
                    created_at = row.created_at,
                    answer = row.answer_content,
                )

        return LookUpInquiryResponse(
            result = CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            inquiries = inquiry_with_answer,
        )

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


