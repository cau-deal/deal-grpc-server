from sea.servicer import ServicerMeta

from app.models import User, JWTToken
from protos.AuthService_pb2 import *
from protos.AuthService_pb2_grpc import *
from protos.CommonResult_pb2 import *

# Deal Servicer
from protos.DealService_pb2 import *

from app.extensions import firebase, JWT, EmailSender

from firebase_admin import messaging
from firebase_admin import datetime
from app.decorators import verified, unverified


# message = messaging.Message(
#     android=messaging.AndroidConfig(
#         ttl=datetime.timedelta(seconds=3600),
#         priority='normal',
#         notification=messaging.AndroidNotification(
#             title='알림인데',
#             body='백그라운드 자비 좀',
#             icon='',
#             color='#f45342',
#             sound='default'
#         ),
#     ),
#     data={
#         'score': '850',
#         'time': '2:45',
#     },
#     topic="all"
#     # token=registration_token
# )

# response = messaging.send(message)
# print(response)


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
        password = request.password

        result_tokens = []

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

                if user.state == 1:
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

        # todo transaction 처리

        sign_in_request = request.credential
        google_profile = request.profile

        email = sign_in_request.email
        password = sign_in_request.password

        result_tokens = []

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
                    type=AccountType.GOOGLE,
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

        # todo server-side validation & hashing
        email = request.email
        password = request.password
        agree_with_terms = request.agree_with_terms
        account_type = request.type
        platform_type = request.platform

        result_tokens = []

        try:
            User.create(
                email=email,
                password=password,
                type=account_type,
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


#class AuthServiceServicer(AuthServiceServicer, metaclass=ServicerMeta):
class DealServicer(DealServicer, metaclass=ServicerMeta):
    @unverified
    def stb(self, request, context):
        print("Hello SengHyeon")

    @verified
    def Inquiry(self, request, context):
        inquiry = request.inquiry
        title = inquiry.title
        contents = inquiry.contents 

        return

    def LookUpInquiry(self, request, context):
        return

    def Accuse(self, request, context):
        return
