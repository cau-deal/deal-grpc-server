import datetime
import hashlib

from peewee import Database
from sea.servicer import ServicerMeta

from app.decorators import verified, unverified
from app.extensions import JWT, pwdb, EmailSender
from app.models import User, JWTToken

from protos.AuthService_pb2 import *
from protos.AuthService_pb2_grpc import *

from protos.CommonResult_pb2 import *
from protos.Profile_pb2 import UserState


class AuthServiceServicer(AuthServiceServicer, metaclass=ServicerMeta):
    @verified
    def SignInWithToken(self, request, context):
        return SignInResponse(
            result=CommonResult(
                result_code=ResultCode.SUCCESS,
                message='SUCCESS'
            ),
            jwt=[]
        )

    @unverified
    def SignInWithCredential(self, request, context):

        email = request.email
        password = hashlib.sha256(request.password.encode('utf-8')).hexdigest()

        result_tokens = []

        db = pwdb.database
        with db.atomic() as transaction:
            try:
                user = User.select().where(
                    (User.email == email) &
                    (User.password == password)
                )

                if user.count() != 1:
                    raise Exception("User not found")
                else:
                    user = user.get()
                    user.last_login_datetime = datetime.datetime.now()
                    user.save()

                    if user.state == UserState.BANNED:
                        raise Exception("You are blocked.")

                access_token = JWT.get_access_token(email)
                refresh_token = JWTToken.get(JWTToken.user_email == email).token_key

                result_tokens = [
                    JWTResult(type=JWTType.ACCESS, token=access_token),
                    JWTResult(type=JWTType.REFRESH, token=refresh_token)
                ]

                result_code = ResultCode.SUCCESS
                result_message = 'SUCCESS'

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)

        return SignInResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message
            ),
            jwt=result_tokens
        )

    @unverified
    def SignInWithGoogle(self, request, context):

        sign_in_request = request.credential
        google_profile = request.profile

        email = sign_in_request.email
        password = hashlib.sha256(sign_in_request.password.encode('utf-8')).hexdigest()

        result_tokens = []

        db = pwdb.database
        with db.atomic() as transaction:
            try:
                user = User.select().where(
                    (User.email == email) &
                    (User.password == password)
                )

                access_token = JWT.get_access_token(email)

                if user.count() != 1:
                    User.create(
                        email=email,
                        password=password,
                        register_type=AccountType.GOOGLE,
                        profile_photo_url=google_profile.profile_image,
                        agree_with_terms=True,
                        last_login_datetime=datetime.datetime.now(),
                        created_at=datetime.datetime.now()
                    )
                    refresh_token = JWT.get_refresh_token(email, access_token)
                    JWTToken.create(
                        token_key=refresh_token,
                        user_email=email,
                        created_at=datetime.datetime.now()
                    )

                    result_tokens = [
                        JWTResult(type=JWTType.ACCESS, token=access_token),
                        JWTResult(type=JWTType.REFRESH, token=refresh_token)
                    ]

                else:
                    user = user.get()
                    user.last_login_datetime = datetime.datetime.now()
                    user.save()

                    if user.state == 1:
                        raise Exception("You are blocked.")

                    result_tokens = [
                        JWTResult(type=JWTType.ACCESS, token=access_token)
                    ]

                result_code = ResultCode.SUCCESS
                result_message = 'SUCCESS'

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)

        return SignInResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message
            ),
            jwt=result_tokens
        )

    @unverified
    def SignUp(self, request, context):

        # todo server-side validation
        email = request.email
        password = hashlib.sha256(request.password.encode('utf-8')).hexdigest()

        agree_with_terms = request.agree_with_terms
        account_type = request.type
        platform_type = request.platform

        result_tokens = []
        db = pwdb.database
        with db.atomic() as transaction:
            try:
                User.create(
                    email=email,
                    password=password,
                    register_type=account_type,
                    agree_with_terms=agree_with_terms,
                    last_login_datetime=datetime.datetime.now(),
                    created_at=datetime.datetime.now()
                )

                access_token = JWT.get_access_token(email)
                refresh_token = JWT.get_refresh_token(email, access_token)

                JWTToken.create(
                    token_key=refresh_token,
                    user_email=email,
                    created_at=datetime.datetime.now()
                )

                result_tokens = [
                    JWTResult(type=JWTType.ACCESS, token=access_token),
                    JWTResult(type=JWTType.REFRESH, token=refresh_token)
                ]

                result_code = ResultCode.SUCCESS
                result_message = "SUCCESS"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)

        return SignUpResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message
            ),
            jwt=result_tokens
        )

    @unverified
    def FindPassword(self, request, context):

        # todo send email.
        try:
            EmailSender.send(request.email)
        except:
            print("email 발송 에러남")

        return FindPasswordResponse(
            result=CommonResult(
                result_code=ResultCode.SUCCESS,
                message="SUCCESS"
            )
        )

    @unverified
    def CheckDuplicationEmail(self, request, context):
        email = request.email

        IS_DUPLICATION_EMAIL = {
            IsDuplicationEmail.UNKNOWN_IS_DUPLICATION_EMAIL: 0,
            IsDuplicationEmail.TRUE_IS_DUPLICATION_EMAIL: 1,
            IsDuplicationEmail.FALSE_IS_DUPLICATION_EMAIL: 2,
        }

        is_duplication_email = IS_DUPLICATION_EMAIL[IsDuplicationEmail.UNKNOWN_IS_DUPLICATION_EMAIL]

        db = pwdb.database
        with db.atomic() as transaction:
            try:
                user = User.select().where(
                    (User.email == email)
                )

                if user.count() == 0:
                    is_duplication_email = IS_DUPLICATION_EMAIL[IsDuplicationEmail.TRUE_IS_DUPLICATION_EMAIL]
                else:
                    is_duplication_email = IS_DUPLICATION_EMAIL[IsDuplicationEmail.FALSE_IS_DUPLICATION_EMAIL]

                result_code = ResultCode.SUCCESS
                result_message = 'SUCCESS'

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)

        return CheckDuplicationEmailResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message
            ),
            is_duplication_email=is_duplication_email,
        )