import hashlib

from peewee import JOIN
from sea.servicer import ServicerMeta

from app.extensions import pwdb

from app.decorators import unverified, verified
from protos.CommonResult_pb2 import CommonResult, ResultCode
from app.models import InquiryModel, User, PhoneAuthentication

import datetime

from protos.UserService_pb2 import LookUpAuthInfoResponse, AuthInfo, IsAuth, ChangePasswordResult, \
    ChangePasswordResponse, LookUpUserInfoResponse, Profile, UserState, Role
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

            if user is not None:
                is_phone_auth = IsAuth.TRUE_IS_AUTH if (user.is_phone_authentication == 1) else IsAuth.FALSE_IS_AUTH
                is_account_auth = IsAuth.TRUE_IS_AUTH if (user.is_account_authentication == 1) else IsAuth.FALSE_IS_AUTH
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

    @verified
    def LookUpUserInfo(self, request, context):

        # init
        result_code = ResultCode.UNKNOWN_RESULT_CODE
        message = "Unknown LookUpUserInfo Message"
        profile = Profile()
        res = None

        try:
            res = User.select(User.email, PhoneAuthentication.name, User.level, User.state, User.role, User.profile_photo_url) \
                .join(PhoneAuthentication, JOIN.LEFT_OUTER, on=(User.email == PhoneAuthentication.user_email)).where(User.email == context.login_email)

            res = res.get()

            result_code = ResultCode.SUCCESS
            result_message = "LookUpUserInfo OK"

        except Exception as e:
            result_code = ResultCode.ERROR
            message = str(e)


        # TODO Hardcoding change
        return LookUpUserInfoResponse(
            result=CommonResult(
                result_code=result_code,
                message=message,
            ),
            profile=Profile(
                email=res.email,
                level=res.level,
                state=UserState.NORMAL,
                role=Role.USER,
                profile_photo_url=res.profile_photo_url,
                name=res.phoneauthentication.name if hasattr(res, 'phoneauthentication') else "회원",
            ),
        )

    # def ChangePassword(self, request, context):
    #
    #     old_pw = hashlib.sha256(request.old_password.encode('utf-8')).hexdigest()
    #     new_pw = hashlib.sha256(request.new_password.encode('utf-8')).hexdigest()
    #
    #     # init
    #     result_code = ResultCode.UNKNOWN_RESULT_CODE
    #     message = "Unknown UserService Message"
    #     change_password_result = ChangePasswordResult.UNKNOWN_CHANGE_PASSWORD
    #
    #     db = pwdb.database
    #
    #     with db.atomic() as transaction:
    #         try:
    #             old_pw = User \
    #                 .select(User.password) \
    #                 .where(User.email == context.login_email)
    #
    #             # If old password is different from db
    #             for pw in old_pw:
    #                 if pw.password != old_pw:
    #                     message = "old password is different."
    #                     raise Exception
    #
    #             # Change Password (Update DB)
    #             res = User \
    #                 .update(password=new_pw) \
    #                 .where(User.email == context.login_email) \
    #                 .execute()
    #
    #             if res == 0:
    #                 message = "Password Update failed"
    #                 raise Exception
    #
    #             result_code = ResultCode.SUCCESS
    #             message = "Password Change OK"
    #             change_password_result = ChangePasswordResult.SUCCESS_CHANGE_PASSWORD
    #
    #         except Exception as e:
    #             transaction.rollback()
    #             result_code = ResultCode.ERROR
    #             change_password_result = ChangePasswordResult.FAIL_CHANGE_PASSWORD
    #             message = str(e)
    #
    #     return ChangePasswordResponse(
    #         result=CommonResult(
    #             result_code=result_code,
    #             message=message,
    #         ),
    #         change_password_result=change_password_result,
    #     )