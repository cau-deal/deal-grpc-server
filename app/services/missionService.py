import operator

from peewee import JOIN, fn
from sea.servicer import ServicerMeta

from app.decorators import verified
from app.extensions import pwdb, root_email
from app.extensions_db import sPointServicer

from app.models import MissionModel, User, PhoneAuthentication, ImageDataForRequestMission, ProcessedImageDataModel, \
    ImageDataModel, SoundDataModel, SurveyDataModel, LabelModel, RecommendMission
from app.models import ConductMission
from app.models import MissionExplanationImageModel

from protos.CommonResult_pb2 import ResultCode, CommonResult

from protos.Data_pb2 import MissionExplanationImageType
from protos.Data_pb2 import MissionExplanationImage

from protos.Datetime_pb2 import Datetime
from protos.Data_pb2 import *

from protos.MissionService_pb2 import *
from protos.MissionService_pb2_grpc import *


import datetime

from protos.Profile_pb2 import Profile

class MissionServiceServicer(MissionServiceServicer, metaclass=ServicerMeta):
    @verified
    def RegisterMission(self, request, context):
        # Mission Obj
        mission = request.mission

        datas = request.datas
        labels = request.labels

        # Mission Obj parsing
        title = mission.title
        contents = mission.contents
        mission_type = mission.mission_type
        data_type = mission.data_type
        unit_package = mission.unit_package
        price_of_package = mission.price_of_package
        order_package_quantity = mission.order_package_quantity
        deadline = mission.deadline
        beginning = mission.beginning
        deadline_datetime = datetime.datetime(year=deadline.year, month=deadline.month, day=deadline.day,
                                     hour=deadline.hour, minute=deadline.min, second=deadline.sec)
        beginning_datetime = datetime.datetime(year=beginning.year, month=beginning.month, day=beginning.day,
                                     hour=beginning.hour, minute=beginning.min, second=beginning.sec)
        summary = mission.summary
        contact_clause = mission.contact_clause
        specification = mission.specification
        mission_explanation_images = mission.mission_explanation_images

        # Database Obj
        db = pwdb.database

        # Return Mission Response default
        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Register Mission"
        register_mission_result = RegisterMissionResult.UNKNOWN_REGISTER_MISSION_RESULT

        #ENUM Mission Type
        MISSION_TYPE = {
            MissionType.UNKNOWN_MISSION_TYPE: 0,
            MissionType.ALL_MISSION_TYPE: 1,
            MissionType.COLLECT_MISSION_TYPE: 2,
            MissionType.PROCESS_MISSION_TYPE: 3,
        }

        #ENUM Data Type
        DATA_TYPE = {
            DataType.UNKNOWN_DATA_TYPE: 0,
            DataType.IMAGE: 1,
            DataType.SOUND: 2,
            DataType.SURVEY: 3,
        }

        #ENUM Mission State
        MISSION_STATE = {
            MissionState.UNKNOWN_MISSION_STATE: 0,
            MissionState.DURING_MISSION: 1,
            MissionState.SOLD_OUT: 2,
            MissionState.WATING_CONFIRM_PURCHASE: 3,
            MissionState.COMPLETE_MISSION: 4,
            MissionState.WAITING_REGISTER: 5,
        }

        #ENUM Mission Explanation Image Type
        MISSION_EXPLANATION_IMAGE_TYPE = {
            MissionExplanationImageType.UNKNOWN_MISSION_EXPLANATION_IMAGE_TYPE: 0,
            MissionExplanationImageType.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE: 1,
            MissionExplanationImageType.BACKGROUND_MISSION_EXPLANATION_IMAGE_TYPE: 2,
            MissionExplanationImageType.MAIN_TEXT_MISSION_EXPLANATION_IMAGE_TYPE: 3,
        }
        mission_id = 0

        now = datetime.datetime.now()
        today_register = False

        if now.year == beginning.year and now.month == beginning.month and now.day == beginning.day:
            today_register = True

        with db.atomic() as transaction:
            try:
                # 잔액 확인 후, 미션 등록 가능 여부 판단
                balance = sPointServicer.sLookUpBalance(context.login_email)
                val = price_of_package * order_package_quantity

                if balance < val:
                    result_code = ResultCode.ERROR
                    register_mission_result = RegisterMissionResult.FAIL_REGISTER_MISSION_RESULT
                    result_message = "Insufficiency balance"
                    raise Exception("Insufficiency balance")

                if today_register is False and (beginning_datetime < datetime.datetime.now()):
                    result_code = ResultCode.ERROR
                    register_mission_result = RegisterMissionResult.FAIL_REGISTER_MISSION_RESULT
                    result_message = "Invalid beginning"
                    raise Exception("Invalid beginning")

                if deadline_datetime < datetime.datetime.now():
                    result_code = ResultCode.ERROR
                    register_mission_result = RegisterMissionResult.FAIL_REGISTER_MISSION_RESULT
                    result_message = "Invalid deadline"
                    raise Exception("Invalid deadline")

                if price_of_package <= 0 or unit_package <= 0 or order_package_quantity <= 0:
                    result_code = ResultCode.ERROR
                    register_mission_result = RegisterMissionResult.FAIL_REGISTER_MISSION_RESULT
                    result_message = 'invalid price or unit or quantity'
                    raise Exception('invalid price or unit or quantity')

                if order_package_quantity % unit_package != 0:
                    result_code = ResultCode.ERROR
                    register_mission_result = RegisterMissionResult.FAIL_REGISTER_MISSION_RESULT
                    result_message = 'order_package_quantity must be multiple by unit_package'
                    raise Exception('order_package_quantity must be multiple by unit_package')

                if mission_type == PROCESS_MISSION_TYPE and len(datas) != order_package_quantity:
                    result_code = ResultCode.ERROR
                    register_mission_result = RegisterMissionResult.FAIL_REGISTER_MISSION_RESULT
                    result_message = 'Order quantity and number of images do not match'
                    raise Exception('Order quantity and number of images do not match')

                # 미션 시작 날짜가 오늘과 같으면 바로 진행 중으로 등록
                if today_register:
                    query = MissionModel.create(
                        register_email=context.login_email,
                        title=title,
                        contents=contents,
                        mission_type=MISSION_TYPE[mission_type],
                        data_type=DATA_TYPE[data_type],
                        state=MISSION_STATE[MissionState.DURING_MISSION],
                        unit_package=unit_package,
                        price_of_package=price_of_package,
                        order_package_quantity=order_package_quantity,
                        beginning=beginning_datetime,
                        deadline=deadline_datetime,
                        created_at=datetime.datetime.now(),
                        summary=summary,
                        contact_clause=contact_clause,
                        specification=specification,
                    )
                # 미션 시작 날짜가 오늘과 다르면 등록대기로 등록
                else:
                    query = MissionModel.create(
                        register_email=context.login_email,
                        title=title,
                        contents=contents,
                        mission_type=MISSION_TYPE[mission_type],
                        data_type=DATA_TYPE[data_type],
                        state=MISSION_STATE[MissionState.WAITING_REGISTER],
                        unit_package=unit_package,
                        price_of_package=price_of_package,
                        order_package_quantity=order_package_quantity,
                        beginning=beginning_datetime,
                        deadline=deadline_datetime,
                        created_at=datetime.datetime.now(),
                        summary=summary,
                        contact_clause=contact_clause,
                        specification=specification,
                    )

                mission_id = query.id

                # 잔액 차감(운영자에게 돈이 지불된다)
                sPointServicer.givePoint(context.login_email, root_email, val, 0)

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e) + " transaction1 error - mission_id :  " + str(mission_id)
                register_mission_result = RegisterMissionResult.FAIL_REGISTER_MISSION_RESULT

        if result_code == ResultCode.UNKNOWN_RESULT_CODE and mission_type == MISSION_TYPE[MissionType.PROCESS_MISSION_TYPE]:
            with db.atomic() as transaction:
                try:
                    for data in datas:
                        url = data.url

                        ImageDataForRequestMission.create(
                            url=url,
                            mission_id=mission_id,
                            state=WAITING__PROCESS,
                            created_at=datetime.datetime.now(),
                        )

                    result_code = ResultCode.SUCCESS
                    result_message = "Register Mission Success"
                    register_mission_result = RegisterMissionResult.SUCCESS_REGISTER_MISSION_RESULT

                    for label in labels:
                        created_at = datetime.datetime.now()
                        LabelModel.create(
                            mission_id=mission_id,
                            label=label,
                            created_at=created_at,
                        )

                except Exception as e:
                    transaction.rollback()
                    result_code = ResultCode.ERROR
                    result_message = str(e) + 'Fail create in ImageDataForRequestMission'
                    register_mission_result = RegisterMissionResult.FAIL_REGISTER_MISSION_RESULT

        if result_code == ResultCode.UNKNOWN_RESULT_CODE:
            with db.atomic() as transaction:
                try:
                    # 이미지가 있으면 저장
                    for mission_explanation_image in mission_explanation_images:
                        url = mission_explanation_image.url
                        image_type = mission_explanation_image.type

                        MissionExplanationImageModel.create(
                            mission_id=mission_id,
                            image_type=MISSION_EXPLANATION_IMAGE_TYPE[image_type],
                            url=url,
                            created_at=datetime.datetime.now()
                        )

                    result_code = ResultCode.SUCCESS
                    result_message = "Register Mission Success"
                    register_mission_result = RegisterMissionResult.SUCCESS_REGISTER_MISSION_RESULT

                except Exception as e:
                    transaction.rollback()
                    result_code = ResultCode.ERROR
                    result_message = str(e) + " transaction2 error - mission_id :  " + str(mission_id)
                    register_mission_result = RegisterMissionResult.FAIL_REGISTER_MISSION_RESULT

        return RegisterMissionResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message + " mission_id :  " + str(mission_id)
            ),
            register_mission_result=register_mission_result
        )

    @verified
    def SearchMission(self, request, context):
        mission_protoes = []

        # Mission Obj parsing
        mission_type = request.mission_type
        keyword = request.keyword
        mission_page = request.mission_page

        mission_page_mode = mission_page.mission_page_mode
        _offset = mission_page._offset
        amount = mission_page.amount

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Search Mission"
        search_mission_result = SearchMissionResult.UNKNOWN_SEARCH_MISSION_RESULT

        NO_KEY_WORD = 1
        YES_KEY_WORD = 2

        if len(keyword) == 0:
            _query_type = NO_KEY_WORD
        else:
            _query_type = YES_KEY_WORD
            keyword = "%" + keyword + "%"

        if mission_page_mode == MissionPageMode.INITIALIZE_MISSION_PAGE:
            _offset = 0

        #ENUM Mission Type
        MISSION_TYPE = {
            MissionType.UNKNOWN_MISSION_TYPE: 0,
            MissionType.ALL_MISSION_TYPE: 1,
            MissionType.COLLECT_MISSION_TYPE: 2,
            MissionType.PROCESS_MISSION_TYPE: 3,
        }

        db = pwdb.database

        query = MissionModel.select()

        with db.atomic() as transaction:
            try:
                MEI = MissionExplanationImageModel.alias()

                # Keyword NOT Exist
                if _query_type == NO_KEY_WORD:
                    # mission type is not all

                    if mission_type != MissionType.ALL_MISSION_TYPE:
                        query = (MissionModel.select(MissionModel, MEI.url.alias('url'))
                                 .join(MEI, JOIN.LEFT_OUTER, on=((MissionModel.id == MEI.mission_id) &
                                    (MEI.image_type == MissionExplanationImageType.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE)))
                                 .where((MissionModel.mission_type == MISSION_TYPE[mission_type])
                                        & (MissionModel.deadline > datetime.datetime.now()))
                                 .order_by((MissionModel.id).desc()).offset(_offset).limit(amount))
                    # mission type is all
                    else:
                        query = (MissionModel.select(MissionModel, MEI.url.alias('url'))
                                 .join(MEI, JOIN.LEFT_OUTER, on=((MissionModel.id == MEI.mission_id) &
                                (MEI.image_type == MissionExplanationImageType.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE)))
                                 .where(MissionModel.deadline > datetime.datetime.now())
                                 .order_by((MissionModel.id).desc()).offset(_offset).limit(amount))
                # keyword exist
                else:
                    # mission type is not all
                    if mission_type != MissionType.ALL_MISSION_TYPE:
                        query = (MissionModel.select(MissionModel, MEI.url.alias('url'))
                                 .join(MEI, JOIN.LEFT_OUTER, on=((MissionModel.id == MEI.mission_id) &
                                (MEI.image_type == MissionExplanationImageType.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE)))
                                 .where((MissionModel.mission_type == MISSION_TYPE[mission_type])
                                        & ((MissionModel.title ** keyword) | (MissionModel.contents ** keyword))
                                        & (MissionModel.deadline > datetime.datetime.now()))
                                 .order_by((MissionModel.id).desc()).offset(_offset).limit(amount))
                    # mission type is all
                    else:
                        query = (MissionModel.select(MissionModel, MEI.url.alias('url'))
                                 .join(MEI, JOIN.LEFT_OUTER, on=((MissionModel.id == MEI.mission_id) &
                                (MEI.image_type == MissionExplanationImageType.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE)))
                                 .where(((MissionModel.title ** keyword) | (MissionModel.contents ** keyword))
                                        & (MissionModel.deadline > datetime.datetime.now()))
                                 .order_by((MissionModel.id).desc()).offset(_offset).limit(amount))

                result_code = ResultCode.SUCCESS
                result_message = "Successful Search Mission"
                search_mission_result = SearchMissionResult.SUCCESS_SEARCH_MISSION_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                search_mission_result = SearchMissionResult.FAIL_SEARCH_MISSION_RESULT

            # id, title, mission_type, price_of_package, deadline, summary, state, created_at, url
            for row in query.dicts():
                b = row['beginning']
                c = row['created_at']
                d = row['deadline']
                mission_protoes.append(
                    MissionProto(
                        mission_id=row['id'],
                        title=row['title'],
                        mission_type=row['mission_type'],
                        price_of_package=row['price_of_package'],
                        deadline=Datetime(year=d.year, month=d.month, day=d.day, hour=d.hour, min=d.minute, sec=d.second),
                        summary=row['summary'],
                        mission_state=row['state'],
                        created_at=Datetime(year=c.year, month=c.month, day=c.day, hour=c.hour, min=c.minute, sec=c.second),
                        beginning=Datetime(year=b.year, month=b.month, day=b.day, hour=b.hour, min=b.minute, sec=b.second),
                        thumbnail_url=row['url'],
                    )
                )

        return SearchMissionResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message + str(query)
            ),
            search_mission_result=search_mission_result,
            mission_protoes=mission_protoes,
        )

    @verified
    def SearchMissionWithId(self, request, context):
        mission_id = request.mission_id

        db = pwdb.database

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Search Mission With Id"
        search_mission_result = SearchMissionResult.UNKNOWN_SEARCH_MISSION_RESULT

        mission = Mission()

        with db.atomic() as transaction:
            try:
                MEI = MissionExplanationImageModel.alias()
                query_mission = (MissionModel.select().where(MissionModel.id == mission_id))

                query_mission_explanation_image = (MEI.select().where(MEI.mission_id == mission_id))

                mission_explanation_images = []

                for row in query_mission_explanation_image:
                    mission_explanation_images.append(
                        MissionExplanationImage(
                            url=row.url,
                            mission_id=mission_id,
                            type=row.image_type,
                        )
                    )

                for row in query_mission:
                    b = row.beginning
                    c = row.created_at
                    d = row.deadline
                    mission = Mission(
                        mission_id=mission_id,
                        title=row.title,
                        contents=row.contents,
                        mission_type=row.mission_type,
                        data_type=row.data_type,
                        unit_package=row.unit_package,
                        price_of_package=row.price_of_package,
                        deadline=Datetime(year=d.year, month=d.month, day=d.day, hour=d.hour, min=d.minute, sec=d.second),
                        order_package_quantity=row.order_package_quantity,
                        summary=row.summary,
                        contact_clause=row.contact_clause,
                        specification=row.specification,
                        mission_explanation_images=mission_explanation_images,
                        mission_state=row.state,
                        created_at=Datetime(year=c.year, month=c.month, day=c.day, hour=c.hour, min=c.minute, sec=c.second),
                        beginning=Datetime(year=b.year, month=b.month, day=b.day, hour=b.hour, min=b.minute, sec=b.second),
                    )

                result_code = ResultCode.SUCCESS
                result_message = "Successful Search Mission With Id"
                search_mission_result = SearchMissionResult.SUCCESS_SEARCH_MISSION_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                search_mission_result = SearchMissionResult.FAIL_SEARCH_MISSION_RESULT

        return SearchMissionWithIdResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message
            ),
            search_mission_result=search_mission_result,
            mission=mission,
        )

    @verified
    def SearchRegisterMissionRelevantMe(self, request, context):
        mission_protoes = []

        mission_page = request.mission_page

        mission_page_mode = mission_page.mission_page_mode
        _offset = mission_page._offset
        amount = mission_page.amount

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Search Register Mission Relevant me"
        search_mission_result = SearchMissionResult.UNKNOWN_SEARCH_MISSION_RESULT

        if mission_page_mode == MissionPageMode.INITIALIZE_MISSION_PAGE:
            _offset = 0

        db = pwdb.database
        with db.atomic() as transaction:
            try:
                MEI = MissionExplanationImageModel.alias()

                query = (MissionModel.select(MissionModel, MEI.url.alias('url'))
                         .join(MEI, JOIN.LEFT_OUTER, on=((MissionModel.id == MEI.mission_id) &
                        (MEI.image_type == MissionExplanationImageType.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE)))
                         .where(MissionModel.register_email == context.login_email)
                         .order_by((MissionModel.id).desc()).offset(_offset).limit(amount))

                for row in query.dicts():
                    b = row['beginning']
                    c = row['created_at']
                    d = row['deadline']
                    mission_protoes.append(
                        MissionProto(
                            mission_id=row['id'],
                            title=row['title'],
                            mission_type=row['mission_type'],
                            price_of_package=row['price_of_package'],
                            deadline=Datetime(year=d.year, month=d.month, day=d.day, hour=d.hour, min=d.minute, sec=d.second),
                            summary=row['summary'],
                            mission_state=row['state'],
                            created_at=Datetime(year=c.year, month=c.month, day=c.day, hour=c.hour, min=c.minute, sec=c.second),
                            beginning=Datetime(year=b.year, month=b.month, day=b.day, hour=b.hour, min=b.minute, sec=b.second),
                            thumbnail_url=row['url'],
                        )
                    )

                result_code = ResultCode.SUCCESS
                result_message = "Successful Search Register Mission Relevant me"
                search_mission_result = SearchMissionResult.SUCCESS_SEARCH_MISSION_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                search_mission_result = SearchMissionResult.FAIL_SEARCH_MISSION_RESULT

        return SearchRegisterMissionRelevantMeResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message
            ),
            search_mission_result=search_mission_result,
            mission_protoes=mission_protoes,
        )

    @verified
    def SearchConductMissionRelevantMe(self, request, context):
        conduct_mission_protoes = []

        mission_page = request.mission_page

        mission_page_mode = mission_page.mission_page_mode
        _offset = mission_page._offset
        amount = mission_page.amount

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Search Conduct Mission Relevant me"
        search_mission_result = SearchMissionResult.UNKNOWN_SEARCH_MISSION_RESULT

        if mission_page_mode == MissionPageMode.INITIALIZE_MISSION_PAGE:
            _offset = 0

        db = pwdb.database
        with db.atomic() as transaction:
            try:
                mission_ids = (ConductMission.select(ConductMission.mission_id)
                               .where(ConductMission.worker_email == context.login_email))

                CM = ConductMission.alias()
                MEI = MissionExplanationImageModel.alias()

                query = (MissionModel.select(MissionModel, CM.state.alias('conduct_state'), MEI.url.alias('url'))
                         .join(MEI, JOIN.LEFT_OUTER, on=((MissionModel.id == MEI.mission_id) &
                        (MEI.image_type == MissionExplanationImageType.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE)))
                         .join(CM, on=((MissionModel.id == CM.mission_id) & (CM.worker_email == context.login_email)))
                         .where((MissionModel.id << mission_ids))
                         .order_by((MissionModel.id).desc()).offset(_offset).limit(amount))

                for row in query.dicts():
                    b = row['beginning']
                    c = row['created_at']
                    d = row['deadline']
                    conduct_mission_protoes.append(
                        ConductMissionProto(
                            mission_id=row['id'],
                            title=row['title'],
                            mission_type=row['mission_type'],
                            price_of_package=row['price_of_package'],
                            deadline=Datetime(year=d.year, month=d.month, day=d.day, hour=d.hour, min=d.minute,
                                              sec=d.second),
                            summary=row['summary'],
                            conduct_mission_state=row['conduct_state'],
                            created_at=Datetime(year=c.year, month=c.month, day=c.day, hour=c.hour, min=c.minute,
                                                sec=c.second),
                            beginning=Datetime(year=b.year, month=b.month, day=b.day, hour=b.hour, min=b.minute,
                                               sec=b.second),
                            thumbnail_url=row['url'],
                        )
                    )

                result_code = ResultCode.SUCCESS
                result_message = "Successful Search Conduct Mission Relevant me"
                search_mission_result = SearchMissionResult.SUCCESS_SEARCH_MISSION_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                search_mission_result = SearchMissionResult.FAIL_SEARCH_MISSION_RESULT

        return SearchConductMissionRelevantMeResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message
            ),
            search_mission_result=search_mission_result,
            conduct_mission_protoes=conduct_mission_protoes,
        )


    @verified
    def GetAssignedMission(self, request, context):
        mission_id = request.mission_id

        db = pwdb.database

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown get assigned mission"
        assign_mission_result = AssignMissionResult.UNKNOWN_ASSIGN_MISSION_RESULT

        MISSION_STATE_STR = {
            MissionState.UNKNOWN_MISSION_STATE: "UNKNOWN_MISSION_STATE",
            MissionState.DURING_MISSION: "DURING_MISSION",
            MissionState.SOLD_OUT: "SOLD_OUT",
            MissionState.WATING_CONFIRM_PURCHASE: "WATING_CONFIRM_PURCHASE",
            MissionState.COMPLETE_MISSION: "COMPLETE_MISSION",
            MissionState.WAITING_REGISTER: "WAITING_REGISTER",
        }

        conduct_mission_id = 0

        with db.atomic() as transaction:
            try:
                #할당 받을 수 있는 상태인지 확인
                query_mission = MissionModel.select().where(MissionModel.id == mission_id)

                if query_mission.count() == 0:
                    raise Exception('Not found mission')

                mission = query_mission.get()

                if mission.state != DURING_MISSION:
                    raise Exception('Mission state is not DURING_MISSION, now state : ' + MISSION_STATE_STR[mission.state])
                if mission.register_email.email == context.login_email:
                    raise Exception("Can't participate in self")
                if mission.deadline < datetime.datetime.now():
                    raise Exception("Expired deadline")

                query_conduct_mission = (ConductMission.select()
                         .where((ConductMission.worker_email == context.login_email) &
                                (ConductMission.mission_id == mission_id))
                         .order_by((ConductMission.id).desc()))

                if query_conduct_mission.count() > 0:
                    conduct_mission = query_conduct_mission.get()
                    conduct_mission_state = conduct_mission.state

                    if (conduct_mission_state == DURING_MISSION_CONDUCT_MISSION_STATE
                        or conduct_mission_state == WAITING_VERIFICATION_CONDUCT_MISSION_STATE
                            or conduct_mission_state == DURING_VERIFICATION_CONDUCT_MISSION_STATE):
                        raise Exception('Already assigned this mission, and not yet completed')

                # 할당 받을 수 있는 경우, 진행.
                query_conduct_mission = ConductMission.create(
                    worker_email=context.login_email,
                    mission_id=mission_id,
                    deadline=datetime.datetime.now() + datetime.timedelta(days=1),
                    created_at=datetime.datetime.now(),
                )

                conduct_mission_id = query_conduct_mission.id

                # 미션 받은 뒤, 후처리

                query_conduct_mission = (ConductMission.select()
                                         .where((ConductMission.mission_id == mission_id)
                                                & (ConductMission.state != RETURN_VERIFICATION_CONDUCT_MISSION_STATE)
                                                & (ConductMission.state != FAIL_MISSION_CONDUCT_MISSION_STATE)))

                cnt_conduct_mission = query_conduct_mission.count()

                if mission.order_package_quantity <= cnt_conduct_mission:
                    mission.state = SOLD_OUT
                    mission.save()

                if mission.mission_type != PROCESS_MISSION_TYPE:
                    result_code = ResultCode.SUCCESS
                    result_message = "Successful Get Assigned Mission"
                    assign_mission_result = AssignMissionResult.SUCCESS_ASSIGN_MISSION_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e) + ' problem1'
                assign_mission_result = AssignMissionResult.FAIL_ASSIGN_MISSION_RESULT

        if result_code == ResultCode.UNKNOWN_RESULT_CODE and mission.mission_type == PROCESS_MISSION_TYPE:
            with db.atomic() as transaction:
                try:
                    mission = MissionModel.select().where(MissionModel.id == mission_id).get()

                    IDF = ImageDataForRequestMission.alias()
                    query_idf = (IDF.select().where((IDF.mission_id == mission_id) &
                                                    IDF.state == WAITING__PROCESS).limit(mission.unit_package))

                    if query_idf.count() < mission.unit_package:
                        raise Exception('Not enough stock')

                    for row in query_idf:
                        ProcessedImageDataModel.create(
                            image_data_for_request_mission_url=row.url,
                            conduct_mission_id=conduct_mission_id,
                            created_at=datetime.datetime.now(),
                            labeling_result="",
                        )
                        
                        # state 변경
                        row.state = DURING_PROCESS
                        row.save()

                    result_code = ResultCode.SUCCESS
                    result_message = "Successful Get Assigned Mission"
                    assign_mission_result = AssignMissionResult.SUCCESS_ASSIGN_MISSION_RESULT

                except Exception as e:
                    transaction.rollback()
                    result_code = ResultCode.ERROR
                    result_message = str(e) + ' problem2'
                    assign_mission_result = AssignMissionResult.FAIL_ASSIGN_MISSION_RESULT

        return GetAssignedMissionResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            assign_mission_result=assign_mission_result,
        )

    @verified
    def SubmitCollectMissionOutput(self, request, context):
        mission_id = request.mission_id

        datas = request.datas

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown submit collect mission output"
        submit_result = SubmitResult.UNKNOWN_SUBMIT_RESULT

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                query_conduct_mission = (ConductMission.select().where(
                    (ConductMission.mission_id == mission_id) & (ConductMission.worker_email == context.login_email)
                    & (ConductMission.state == DURING_MISSION_CONDUCT_MISSION_STATE)))

                if query_conduct_mission.count() == 0:
                    raise Exception('Not found(valid conduct mission)')

                conduct_mission = query_conduct_mission.get()

                conduct_mission_id = conduct_mission.id

                mission = (MissionModel.select().where(MissionModel.id == mission_id)).get()

                data_type = mission.data_type

                target_model = MissionModel.alias()

                if data_type == IMAGE:
                    target_model = ImageDataModel.alias()
                elif data_type == SOUND:
                    target_model = SoundDataModel.alias()
                elif data_type == SURVEY:
                    target_model = SurveyDataModel.alias()
                else:
                    raise Exception('Unknown data type')

                for data in datas:
                    url = data.url
                    state = WAITING_VERIFICATION
                    created_at = datetime.datetime.now()

                    target_model.create(
                        url=url,
                        conduct_mission_id=conduct_mission_id,
                        state=state,
                        created_at=created_at,
                    )

                conduct_mission.state = WAITING_VERIFICATION
                conduct_mission.save()

                result_code = ResultCode.UNKNOWN_RESULT_CODE
                result_message = "Success submit collect mission output"
                submit_result = SubmitResult.SUCCESS_SUBMIT_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                submit_result = SubmitResult.FAIL_SUBMIT_RESUlT

        return SubmitCollectMissionOutputResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            submit_result=submit_result,
        )

    @verified
    def SubmitProcessMissionOutput(self, request, context):
        mission_id = request.mission_id

        datas = request.datas

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown submit process mission output"
        submit_result = SubmitResult.UNKNOWN_SUBMIT_RESULT

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                query_conduct_mission = (ConductMission.select().where(
                    (ConductMission.mission_id == mission_id) & (ConductMission.worker_email == context.login_email)
                    & (ConductMission.state == DURING_MISSION_CONDUCT_MISSION_STATE)))

                if query_conduct_mission.count() == 0:
                    raise Exception('Not found(valid conduct mission) : ' + query_conduct_mission)

                conduct_mission = query_conduct_mission.get()

                conduct_mission_id = conduct_mission.id

                mission = (MissionModel.select().where(MissionModel.id == mission_id)).get()

               #datas_dict = sorted(datas_dict.items(), key=operator.itemgetter(0))

                for data in datas:
                    processed_image_data = (ProcessedImageDataModel.select()
                                            .where(ProcessedImageDataModel.image_data_for_request_mission_url == data.data.url)).get()

                    processed_image_data.labeling_result = data.data.url
                    processed_image_data.save()

                    image_data_for_request_mission = (ImageDataForRequestMission.select()
                                                      .where(ImageDataForRequestMission.url == data.data.url)).get()
                    image_data_for_request_mission.state = WAITING_VERIFICATION
                    image_data_for_request_mission.save()

                conduct_mission.state = WAITING_VERIFICATION
                conduct_mission.save()

                result_code = ResultCode.UNKNOWN_RESULT_CODE
                result_message = "Success submit process mission output"
                submit_result = SubmitResult.SUCCESS_SUBMIT_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                submit_result = SubmitResult.FAIL_SUBMIT_RESUlT

        return SubmitProcessMissionOutputResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            submit_result=submit_result,
        )

    @verified
    def CountFetchMission(self, request, context):
        db = pwdb.database
        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Count Fetch mission"

        count = 0
        count1 = 0
        count2 = 0

        with db.atomic() as transaction:
            try:
                query_mission = (MissionModel.select(fn.count(MissionModel.id).alias('count'))
                                 .where(((MissionModel.state == DURING_MISSION) | (MissionModel.state == DURING_MISSION)
                                        | (MissionModel.state == WATING_CONFIRM_PURCHASE) | (MissionModel.state == WAITING_REGISTER))
                                        & (MissionModel.register_email == context.login_email)))

                for row in query_mission:
                    count1 = row.count
                    count += row.count

                query_conduct_mission = (ConductMission.select(fn.count(ConductMission.id).alias('count'))
                                         .where(((ConductMission.state == DURING_MISSION_CONDUCT_MISSION_STATE)
                                                | (ConductMission.state == WAITING_VERIFICATION_CONDUCT_MISSION_STATE)
                                                | (ConductMission.state == DURING_VERIFICATION_CONDUCT_MISSION_STATE))
                                                & (ConductMission.worker_email == context.login_email)))

                for row in query_conduct_mission:
                    count += row.count
                    count2 = row.count

                result_code = ResultCode.SUCCESS
                result_message = "Successful Count Fetch mission"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)

        return CountFetchMissionResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message + " register mission :  " + str(count1) + "  conduct mission : " + str(count2),
            ),
            val=count,
        )

    @verified
    def GetMissionOwnerInfo(self, request, context):
        mission_id = request.mission_id
        db = pwdb.database

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown get mission owner mission"

        profile = Profile()

        with db.atomic() as transaction:
            try:
                user_name = ""
                register_email = ""

                register_email_query = (MissionModel.select(MissionModel.register_email).where(MissionModel.id == mission_id))

                for row in register_email_query:
                    register_email = str(row.register_email)

                user_query = (User.select().where(User.email == register_email))

                user_name_query = (PhoneAuthentication.select(PhoneAuthentication.name.alias('name'))
                                   .where(PhoneAuthentication.user_email == register_email))

                for row in user_name_query.dicts():
                    user_name = row['name']
                
                for row in user_query:
                    profile = Profile(
                        email=register_email,
                        level=row.level,
                        state=row.state,
                        role=row.role,
                        profile_photo_url=row.profile_photo_url,
                        name=user_name,
                )

                result_code = ResultCode.SUCCESS
                result_message = "Successful get mission owner Mission"
                assign_mission_result = AssignMissionResult.SUCCESS_ASSIGN_MISSION_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e) + " "
                assign_mission_result = AssignMissionResult.FAIL_ASSIGN_MISSION_RESULT

        return GetMissionOwnerInfoResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            register_profile=profile,
        )

    @verified
    def GetParticipatedMissionState(self, request, context):
        mission_id = request.mission_id

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Get Participated Mission State"

        db = pwdb.database

        conduct_mission_state = INIT_CONDUCT_MISSION_STATE

        with db.atomic() as transaction:
            try:
                query = (ConductMission.select()
                         .where((ConductMission.worker_email == context.login_email) &
                                (ConductMission.mission_id == mission_id))
                         .order_by((ConductMission.id).desc()))

                if query.count() > 0:
                    conduct_mission = query.get()
                    conduct_mission_state = conduct_mission.state

                result_code = ResultCode.SUCCESS
                result_message = "Successful Get Participated Mission State"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e) + " "

        return GetParticipatedMissionStateResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            conduct_mission_state=conduct_mission_state,
        )

    @verified
    def GetLabels(self, request, context):
        mission_id = request.mission_id

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Get labels"

        labels = []

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                query = (LabelModel.select().where(LabelModel.mission_id == mission_id))

                for row in query:
                    labels.append(row.label)

                result_code = ResultCode.SUCCESS
                result_message = "Successful Get labels"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e) + " "

        return GetLabelsResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            labels=labels
        )

    @verified
    def GetLabelingResult(self, request, context):
        url = request.url

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Get label result"

        db = pwdb.database

        labeling_result = ''

        with db.atomic() as transaction:
            try:
                query = (ProcessedImageDataModel.select()
                             .where(ProcessedImageDataModel.image_data_for_request_mission_url == url))

                if query.count() == 0:
                    raise Exception("No exist such url")

                labeling_result = query.get().labeling_result
                result_code = ResultCode.SUCCESS
                result_message = "Successful Get label result"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)

        return GetLabelingResultResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            label_result=labeling_result
        )

    @verified
    def GetRecommendMissionImages(self, request, context):
        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Get Recommend Mission Images"

        db = pwdb.database

        mission_recommend_images = []
        s = ""

        with db.atomic() as transaction:
            try:
                query = (RecommendMission.select())

                for row in query:
                    s += row.url + "   " + str(row.mission_id)
                    mission_recommend_images.append(
                        MissionRecommendImage(
                            mission_id=row.mission_id,
                            recommend_image_url=row.url,
                        )
                    )
                    s += "xxx"

                result_code = ResultCode.SUCCESS
                result_message = "Successful Get Recommend Mission Images"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e) + s

        return GetRecommendMissionImagesResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            mission_recommend_images=mission_recommend_images
        )