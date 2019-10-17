from sea.servicer import ServicerMeta

from app.extensions import pwdb

from app.decorators import unverified, verified
from protos.CommonResult_pb2 import CommonResult, ResultCode
from app.models import InquiryModel, User

import datetime

from protos.UserService_pb2 import LookUpAuthInfoResponse, AuthInfo, IsAuth
from protos.UserService_pb2_grpc import UserServiceServicer


class UserServiceServicer(UserServiceServicer, metaclass=ServicerMeta):

    @verified
    def LookUpAuthInfo(self, request, context):
        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown"
        is_phone_auth = IsAuth.UNKNOWN_IS_AUTH
        is_account_auth = IsAuth.UNKNOWN_IS_AUTH

        try:
            user = User.get(User.email == context.login_email)

            if user == 1:
                is_phone_auth = IsAuth.TRUE_IS_AUTH if(user.is_phone_authentication == 1) else IsAuth.FALSE_IS_AUTH
                is_account_auth = IsAuth.TRUE_IS_AUTH if(user.is_account_authentication == 1) else IsAuth.FALSE_IS_AUTH
                result_code = ResultCode.SUCCESS
                result_message = 'SUCCESS'
            else:
                raise Exception

        except Exception as e:
            result_code = ResultCode.ERROR
            result_message = str(e)

        return LookUpAuthInfoResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            auth_info=AuthInfo(
                is_phone_auth=is_phone_auth,
                is_account_auth=is_account_auth
            )
        )
