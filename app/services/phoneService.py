from peewee import Database
from sea.servicer import ServicerMeta

from app.decorators import verified, unverified
from app.extensions import JWT, pwdb, EmailSender

from app.models import User, JWTToken
from app.models import PhoneAuthentication

from protos.PhoneService_pb2 import *
from protos.PhoneService_pb2_grpc import *

from protos.Date_pb2 import *

from protos.CommonResult_pb2 import *

import datetime


class PhoneServiceServicer(PhoneServiceServicer, metaclass=ServicerMeta):

    @verified
    def PhoneAuth(self, request, context):
        phone_num = request.phone_num
        name = request.name
        mobile_carrier = request.mobile_carrier
        is_native = request.is_native
        birth = request.birthday
        sex = request.sex

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Phone Auth Result"
        phone_result = PhoneResult.UNKNOWN_PHONE_RESULT

        print(request)

        MOBILE_CARRIER = {
            MobileCarrier.UNKNOWN_MOBILE_CARRIER: "UNKNOWN",
            MobileCarrier.KTF: "KTF",
            MobileCarrier.SKT: "SKT",
            MobileCarrier.LGU: "LGU",
            MobileCarrier.KTR: "KTR",
            MobileCarrier.SKR: "SKR",
            MobileCarrier.LGR: "LGR",
        }

        SEX = {
            Sex.UNKNOWN_SEX: 0,
            Sex.MALE: 1,
            Sex.FEMALE: 2
        }

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                ins_res = PhoneAuthentication.create(
                    user_email=context.login_email,
                    phone_num=phone_num,
                    name=name,
                    mobile_carrier=MOBILE_CARRIER[mobile_carrier],
                    sex=SEX[sex],
                    is_native=is_native,
                    birth=datetime.date(year=birth.year, month=birth.month, day=birth.day),
                    created_at=datetime.datetime.now(),
                )

                if ins_res == 0:
                    raise Exception

                res = User \
                    .update(is_phone_authentication=True) \
                    .where(User.email == context.login_email) \
                    .execute()

                # level update(0 --> 1)
                res = (User.update(level=1)
                       .where(User.email == context.login_email)
                       .execute())

                result_code = ResultCode.SUCCESS
                result_message = "Phone Auth success"
                phone_result = PhoneResult.SUCCESS_PHONE_RESULT

                print(res)
                if res == 0:
                    raise Exception

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                print("EXCEPTION: " + str(e))
                phone_result = PhoneResult.FAIL_PHONE_RESULT

        return PhoneAuthResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            phone_result=PhoneResult.SUCCESS_PHONE_RESULT,
        )
