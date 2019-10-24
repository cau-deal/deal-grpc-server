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

# for bank auth rest api
import requests


class AccountServiceServicer(AccountServiceServicer, metaclass=ServicerMeta):

    @verified
    def AccountAuth(self, request, context):
        account = request.account

        account_num = account.account_num
        bank = account.bank
        account_holder_info = account.account_holder_info

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Account Auth Result"
        account_result = AccountAuthResult.UNKNOWN_ACCOUNT_AUTH_RESULT

        BANK_ENUM = {
            BANK.UNKNOWN_BANK: "UNKNOWN",
            BANK.NH: "011",
            BANK.IBK: "003",
            BANK.KB: "004",
            BANK.KAKAO: "090",
            BANK.WOORI: "020",
        }

        headers = {
                    'Content-Type': 'application/json; charset=UTF-8',
                    "Authorization": "Bearer 08e28d74-664a-4cd8-91da-4a1b38a9aaea"
                }
        now_time = datetime.datetime.now()
        now_time_str = now_time.strftime("%Y%m%d%H%M%S")
        params = {
            "bank_code_std": BANK_ENUM[bank],
            "account_num": account_num,
            "account_holder_info": account_holder_info,
            "tran_dtime": now_time_str,
        }

        response = requests.post(
            url='https://openapi.open-platform.or.kr/inquiry/real_name',
            headers = headers,
            params = params2,
        )

        print(params2)
        print(headers)

        print(response)


        db = pwdb.database

        with db.atomic() as transaction:
            try:
                ins_res = AccountAuthentication \
                    .create(
                    user_email=context.login_email,
                    account_num=account_num,
                    name=name,
                    bank=BANK_ENUM[bank],
                )

                if ins_res == 0:
                    print("INSERT ERROR")
                    raise Exception

                res = User \
                    .update(is_account_authentication=True) \
                    .where(User.email == context.login_email) \
                    .execute()

                result_code = ResultCode.SUCCESS
                result_message = "Account Auth success"
                account_result = AccountAuthResult.SUCCESS_ACCOUNT_AUTH_RESULT

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
            account_auth_result=account_result,
        )
