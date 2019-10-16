from peewee import Database
from sea.servicer import ServicerMeta

from app.decorators import verified, unverified
from app.extensions import JWT, pwdb, EmailSender
from app.models import User, JWTToken

from protos.PhoneService_pb2 import *
from protos.PhoneService_pb2_grpc import *

from protos.CommonResult_pb2 import *

class PhoneServiceServicer(PhoneServiceServicer, metaclass=ServicerMeta):
    
    @verified
    def PhoneAuth(self, request, context):
        phone_num = request.phone_num
        name = request.name
        mobile_carrier = request.mobile_carrier
        is_native = request.is_native
        birthday = request. birthday
        sex = request.sex

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Phone Auth Result"
        phone_result = PhoneResult.UNKNOWN_PHONE_RESULT

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                res = (User
                .update(is_phone_authentication=True)
                .where(User.email == context.user_email)
                .execute())

                result_code = ResultCode.SUCCESS
                result_message = "Phone Auth success"
                phone_result = PhoneResult.SUCCESS_PHONE_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                phone_result = PhoneResult.FAIL_PHONE_RESULT

        return PhoneAuthResponse(
            result = CommonResult(
                result_code=result_code,
                result_message=result_message,
            ),
            phone_result= PhoneResult.SUCCESS_PHONE_RESULT,
        )