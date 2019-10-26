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
import random
import json

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

        BANK_STR = {
            BANK.UNKNOWN_BANK: "UNKNOWN",
            BANK.NH: "NH",
            BANK.IBK: "IBK",
            BANK.KB: "KB",
            BANK.KAKAO: "KAKAO",
            BANK.WOORI: "WOORI",
        }

        token_params = {
            'client_id' : 'l7xx8ca825b7e1f740ee8a3445df4dbb5a6a',
            'client_secret': '02c98c8dc8344477992e8de6686e9e46',
            'scope': 'oob',
            'grant_type' : 'client_credentials'
        }

        token_headers = {
            'Content-Type': 'application/json; charset=UTF-8'
        }

        token_responses = requests.post(
            url='https://testapi.open-platform.or.kr/oauth/2.0/token',
            params = token_params,
            headers = token_headers,
        ).json()

        access_token = token_responses['access_token']

        inq_headers = {
                    'Content-Type': 'application/json; charset=UTF-8',
                    "Authorization": "Bearer " + access_token,
        }

        # parameter data generate
        now_time = datetime.datetime.now()
        now_time_str = now_time.strftime("%Y%m%d%H%M%S")

        # bank_tran_id generate
        LENGTH = 9
        string_pool = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        tran_id = token_responses['client_use_code'] + "U"
        for i in range(LENGTH):
            tran_id += random.choice(string_pool)


        inq_params = {
            "bank_tran_id":tran_id,
            "bank_code_std": BANK_ENUM[bank],
            "account_num": account_num,
            "account_holder_info": account_holder_info,
            "account_holder_info_type":" ",
            "tran_dtime": now_time_str,
        }
        # Realname Inquiry Response
        real_name_response = requests.post(
            url='https://testapi.open-platform.or.kr/v2.0/inquiry/real_name',
            headers = inq_headers,
            data = json.dumps(inq_params)
        ).json()

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                ins_res = AccountAuthentication \
                    .create(
                    user_email=context.login_email,
                    account_num=account_num,
                    name=real_name_response['account_holder_name'],
                    bank=BANK_STR[bank],
                    created_at = datetime.datetime.now(),
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
