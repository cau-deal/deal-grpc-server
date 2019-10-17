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
    def ChangePassword(self, request, context):
        
        old_pw = hashlib.sha256(request.old_password.encode('utf-8')).hexdigest()
        new_pw = hashlib.sha256(request.new_password.encode('utf-8')).hexdigest()

        #init
        result_code = ResultCode.UNKNOWN_RESULT_CODE
        message = "Unknown UserService Message"
        change_password_result = ChangePasswordResult.UNKNOWN_CHANGE_PASSWORD

        db = pwdb.database

        with db.atomic() as transaction:
            try: 
                old_pw = User\
                .select(User.password)\
                .where(User.email == context.login_email)

                # If old password is different from db
                for pw in old_pw:
                    if pw.password != old_pw:
                        message = "old password is different."
                        raise Exception
                
                # Change Password (Update DB)
                res = User\
                .update(password=new_pw)\
                .where(User.email == context.login_email)\
                .execute()

                if res == 0:
                        message = "Password Update failed"
                        raise Exception

                result_code = ResultCode.SUCCESS
                message = "Password Change OK"
                change_password_result = ChangePasswordResult.SUCCESS_CHANGE_PASSWORD
            
            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                change_password_result = ChangePasswordResult.FAIL_CHANGE_PASSWORD
                message = str(e)

        return ChangePasswordResponse(
            result = CommonResult(
                result_code = result_code,
                message = message,
            ),
            change_password_result = change_password_result,
        )

    def LookUpUserInfo(self, request, context):
        
        #init
        result_code = ResultCode.UNKNOWN_RESULT_CODE
        message = "Unknown LookUpUserInfo Message"
        
        db = pwdb.database
        with db.atomic() as transaction:
            try: 
                q = User\
                .select(User.email, User.level, User.state, User.role, User.profile_photo_url)\
                .where(User.email == context.login_email)

                nq = PhoneAuthentication\
                    .select(PhoneAuthentication.name)\
                    .where(PhoneAuthentication.user_email == context.login_email)
                
                for _ in q:
                    query = _
                
                for _ in nq:
                    name_query = _

                if len(name_query) == 0:
                    message = "phone auth name not exist"
                    raise Exception

                result_code = ResultCode.SUCCESS
                result_message = "LookUpUserInfo OK"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                message = str(e)

        # TODO Hardcoding change
        return LookUpUserInfoResponse(
            result = CommonResult(
                result_code=result_code,
                message=message,
            ),
            profile = Profile(
                email=query.email,
                level=query.level,
                state=UserState.NORMAL,
                role=UserState.USER,
                profile_photo_url=query.profile_photo_url,
                name=name_query.name,
            ),
        )
    
