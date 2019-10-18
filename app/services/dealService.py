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
                # mission_type, _offset, keyw, keyw
                query = (Inquiry
                    .select()
                    .where(Inquiry.user_email == context.login_email))

                result_code = ResultCode.SUCCESS
                result_message = "Successful look up inquiry"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)

            inquiry_protoes = []

            # id, title, ms_type, price_of_package, deadline, summary, url, created_at, state,
            for row in cursor:
                inquiry_protoes.append(
                    Inquiry(
                        mission_id=row[0],
                        title=row[1],
                        mission_type=row[2],
                        price_of_package=row[3],
                        deadline=row[4],
                        summary=row[5],
                        mission_state=row[8],
                        created_at=row[7],
                        thumbnail_url=row[6],
                    )
                )

        return SearchMissionResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message
            ),
            search_mission_result=search_mission_result,
            mission_protoes=mission_protoes,
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


