from sea.servicer import ServicerMeta

from app.models import User, JWTToken
from protos.AuthService_pb2 import *
from protos.AuthService_pb2_grpc import *

from protos.CommonResult_pb2 import *

# Deal Servicer
from protos.DealService_pb2 import *
from protos.DealService_pb2_grpc import *

# Mission Servicer
from protos.MissionService_pb2 import *
from protos.MissionService_pb2_grpc import *
from app.models import Mission
from app.extensions import JWT

# peewee DB connect
from peewee import *
from app.extensions import pwdb


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
        # mysql_db = MySQLDatabase()
        Database.atomic()
        sign_in_request = request.credential
        google_profile = request.profile

        email = sign_in_request.email
        password = sign_in_request.password

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

        # todo server-side validation & hashing
        email = request.email
        password = request.password
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


#class AuthServiceServicer(AuthServiceServicer, metaclass=ServicerMeta):
class DealServiceServicer(DealServiceServicer, metaclass=ServicerMeta):
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


class MissionServiceServicer(MissionServiceServicer, metaclass=ServicerMeta):
    @verified
    def RegisterMission(self, request, context):
        # Mission Obj
        ms = request.mission

        # Mission Obj parsing
        mission_id = ms.mission_id
        title = ms.title
        contents = ms.contents
        mission_type = ms.mission_type
        data_type = ms.data_type
        unit_package = ms.unit_package
        price_of_package = ms.price_of_package
        deadline = ms.deadline
        order_package_quantity = ms.order_package_quantity
        summary = ms.summary
        contact_clause = ms.contact_clause
        specification = ms.specification
        mission_explanation_images = ms.mission_explanation_images
        mission_state = ms.mission_state
        created_at = ms.created_at

        # Database Obj
        db = pwdb.database

        # Return Mission Response default
        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown"
        register_mission_result = RegisterMissionResult.UNKNOWN_REGISTER_MISSION_RESULT
           
        # DB Transaction
        # table : mission

        # Extract Email
        metadata = dict(context.invocation_metadata())
        _email_addr = (metadata['aud']) if metadata['aud'] else ""

        JWT.decode()


        with db.atomic() as transaction:
            try: 
                Mission.create(
                    register_email = _email_addr,
                    mission_id = mission_id,
                    title = title,
                    contents = contetnts,
                    mission_type = mission_type,
                    data_type = data_type,
                    unit_package = unit_package,
                    price_of_package = price_of_package,
                    deadline = deadline,
                    order_package_quantity = order_package_quantity,
                    summary = summary,
                    contact_clause  = contact_clause,
                    specification = specification,
                    mission_explanation_images = mission_explanation_images,
                    mission_state = mission_state,
                    created_at = created_at,
                )

                result_code = ResultCode.SUCCESS
                result_message = "Register Mission Success"
                register_mission_result = RegisterMissionResult.SUCCESS_REGISTER_MISSION_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                register_mission_result = RegisterMissionResult.FAIL_REGISTER_MISSION_RESULT
            
        return RegisterMissionResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message
            ),
            register_mission_result = register_mission_result
        )

    @verified    
    def SearchMission(self, request, context):
        # Mission Obj
        ms = request

        # Mission Obj parsing
        mission_type = ms.mission_type
        keyword = ms.keyword
        mission_page = ms.mission_page
        
        mission_page_mode = mission_page.mission_page

        _offset = mission_page._offset
        amount = mission_page.amount

        Mission.select(Mission.mission_id)
               .where()
        )




    @verified
    def SearchMissionWithId(self, request, context):
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    @verified
    def SearchMissionReleventMe(self, request, context):
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    @verified
    def SearchMissionReleventMe(self, request, context):
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    @verified
    def GetAssignedMission(self, request, context):
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    @verified
    def SubmitCollectMissionOutput(self, request, context):
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    @verified
    def SubmitProcessMissionOutput(self, request, context):
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    