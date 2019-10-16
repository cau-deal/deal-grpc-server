from peewee import Database
from sea.servicer import ServicerMeta

from app.decorators import verified, unverified
from app.extensions import JWT, pwdb, EmailSender

from app.models import User, JWTToken
from app.models import AccountAuthentication

from protos.AccountService_pb2 import *
from protos.AccountService_pb2_grpc import *

from protos.CommonResult_pb2 import *

import datetime


class AccountServiceServicer(AccountServiceServicer, metaclass=ServicerMeta):

    @verified
    def AccountAuth(self, request, context):
        account_num = request.account_num
        name = request.name
        bank = request.bank

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Account Auth Result"
        account_result = AccountAuthResult.UNKNOWN_ACCOUNT_AUTH_RESULT

        print(request)
        BANK = [
            "UNKNOWN_BANK",
            "NH",
            "IBK",
            "KB",
            "KAKAO",
            "WOORI",
        ]

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                ins_res = AccountAuthentication \
                    .create(
                    user_eamil=context.login_email,
                    account_num=account_num,
                    name=name,
                    bank=BANK[bank],
                )

                if ins_res == 0:
                    print("INSERT ERROR")
                    raise Exception

                res = User \
                    .update(is_account_authentication=True) \
                    .where(User.email == context.login_email) \
                    .execute()

                print(ins_res)

                result_code = ResultCode.SUCCESS
                result_message = "Account Auth success"
                account_result = AccountAuthResult.SUCCESS_ACCOUNT_AUTH_RESULT

                print(res)
                if res == 0:
                    print("UPDATE ERROR")
                    raise Exception
            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                print("EXCEPTION: " + str(e))
                account_result = AccountAuthResult.FAIL_ACCOUNT_AUTH_RESULT

        return AccountAuthResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            account_auth_result=AccountAuthResult.SUCCESS_ACCOUNT_AUTH_RESULT,
        )
