from peewee import JOIN
from sea.servicer import ServicerMeta

from app.decorators import verified
from app.extensions import pwdb

from app.models import MissionModel
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


class MissionServiceServicer(MissionServiceServicer, metaclass=ServicerMeta):
    @verified
    def RegisterMission(self, request, context):
        # Mission Obj
        mission = request.mission

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
        }

        with db.atomic() as transaction:
            try:
                MissionModel.create(
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

                # Registered Mission Tuple print
                result_code = ResultCode.SUCCESS
                result_message = "Register Mission Success"
                register_mission_result = RegisterMissionResult.SUCCESS_REGISTER_MISSION_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                #result_message = str(e)
                error_message = str(e) + "  " + context.login_email + "  " + title + "  " + contents + "  " + \
                                str(mission_type) + "  " + str(DATA_TYPE[data_type]) + "  " + str(unit_package) + "  "+\
                                str(price_of_package) + "  " + "  " + str(beginning) + "  " + str(deadline) + "  " + str(order_package_quantity) + "  " + summary + \
                                "  " + contact_clause + "  " + specification + "  " + "  " + str(datetime.datetime.now()) + "  "
                result_message = error_message
                register_mission_result = RegisterMissionResult.FAIL_REGISTER_MISSION_RESULT

        return RegisterMissionResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message
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

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                MEI = MissionExplanationImageModel.alias()

                # Keyword NOT Exist
                if _query_type == NO_KEY_WORD:
                    # mission type is not all

                    if mission_type != MissionType.ALL_MISSION_TYPE:
                        query = (MissionModel.select().join(MEI, JOIN.LEFT_OUTER, on=(MissionModel.id == MEI.mission_id))
                                .where(MEI.image_type == MissionExplanationImageType.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE
                                & MissionModel.id >= _offset & MissionModel.mission_type == mission_type)
                                .limit(amount))
                    # mission type is all
                    else:
                        query = (MissionModel.select().join(MEI, JOIN.LEFT_OUTER, on=(MissionModel.id == MEI.mission_id))
                                .where(MEI.image_type == MissionExplanationImageType.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE
                                & MissionModel.id >= _offset)
                                .limit(amount))
                # keyword exist
                else:
                    # mission type is not all
                    if mission_type != MissionType.ALL_MISSION_TYPE:
                        query = (MissionModel.select().join(MEI, JOIN.LEFT_OUTER, on=(MissionModel.id == MEI.mission_id))
                                .where(MEI.image_type == MissionExplanationImageType.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE
                                & MissionModel.id >= _offset & MissionModel.mission_type == mission_type
                                & (MissionModel.title ** keyword | MissionModel.contents ** keyword))
                                .limit(amount))
                    # mission type is all
                    else:
                        query = (MissionModel.select().join(MEI, JOIN.LEFT_OUTER, on=(MissionModel.id == MEI.mission_id))
                                .where(MEI.image_type == MissionExplanationImageType.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE
                                & MissionModel.id >= _offset & (MissionModel.title ** keyword | MissionModel.contents ** keyword))
                                .limit(amount))

                result_code = ResultCode.SUCCESS
                result_message = "Successful Search Mission"
                search_mission_result = SearchMissionResult.SUCCESS_SEARCH_MISSION_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                search_mission_result = SearchMissionResult.FAIL_SEARCH_MISSION_RESULT

            # id, title, mission_type, price_of_package, deadline, summary, state, created_at, url

            for row in query:
                d = row.created_at
                mission_protoes.append(
                    MissionProto(
                        mission_id=row.id,
                        title=row.title,
                        mission_type=row.mission_type,
                        price_of_package=row.price_of_package,
                        deadline=row.deadline,
                        summary=row.summary,
                        mission_state=row.state,
                        created_at=Datetime(year=d.year, month=d.month, day=d.day, hour=d.hour, min=d.minute, sec=d.second),
                        #thumbnail_url=row.url,
                    )
                )


        return SearchMissionResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message
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

        with db.atomic() as transaction:
            try:
                query = MissionModel.select().where(MissionModel.id == mission_id)

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
            mission=query,
        )

    @verified
    def SearchMissionRelevantMe(self, request, context):
        mission_protoes = []

        relevant_type = request.relevant_type
        mission_page = request.mission_page

        mission_page_mode = mission_page.mission_page_mode
        _offset = mission_page._offset
        amount = mission_page.amount

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Search Mission Relevant me"
        search_mission_result = SearchMissionResult.UNKNOWN_SEARCH_MISSION_RESULT

        if mission_page_mode == MissionPageMode.INITIALIZE_MISSION_PAGE:
            _offset = 0

        db = pwdb.database
        with db.atomic() as transaction:
            try:
                MEI = MissionExplanationImage.alias()
                MEIT = MissionExplanationImageType.alias()

                # work mission
                if relevant_type == RelevantType.REGISTER_RELEVANT_TYPE:
                    query = (MissionModel.select().join(MEI, JOIN.LEFT_OUTER, on=(MissionModel.id == MEI.mission_id))
                            .where(MEI.image_type == MEIT.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE
                                & MissionModel.id >= _offset & MissionModel.register_email == context.login_email)
                            .limit(amount))

                # register mission
                else:
                    mission_ids = (ConductMission.select(ConductMission.mission_id)
                                   .where(ConductMission.worker_email == context.login_email))
                    # WHERE value 'In' clause
                    query = (MissionModel.select().join(MEI, JOIN.LEFT_OUTER, on=(MissionModel.id == MEI.mission_id))
                            .where(MEI.image_type == MEIT.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE
                                & MissionModel.id >= _offset & MissionModel.id << mission_ids)
                            .limit(amount))

                result_code = ResultCode.SUCCESS
                result_message = "Successful Search Mission"
                search_mission_result = SearchMissionResult.SUCCESS_SEARCH_MISSION_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                search_mission_result = SearchMissionResult.FAIL_SEARCH_MISSION_RESULT

            # id, title, mission_type, price_of_package, deadline, summary, state, created_at, url
            for row in query:
                mission_protoes.append(
                    MissionProto(
                        mission_id=row.id,
                        title=row.title,
                        mission_type=row.mission_type,
                        price_of_package=row.price_of_package,
                        deadline=row.deadline,
                        summary=row.summary,
                        mission_state=row.mission_state,
                        created_at=row.created_at,
                        thumbnail_url=row.url,
                    )
                )

        return SearchMissionResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message
            ),
            search_mission_result=search_mission_result,
            mission_protoes=mission_protoes,
        )

    @verified
    def GetAssignedMission(self, request, context):
        # 아직 구현 완료 아님

        mission_id = request.mission_id

        db = pwdb.database

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown"
        assign_mission_result = AssignMissionResult.UNKNOWN_ASSIGN_MISSION_RESULT

        with db.atomic() as transaction:
            try:
                # TODO 유효한 상태인지 확인할것

                ConductMission.create(
                    worker_email = context.login_email,
                    mission_id = mission_id,
                    state = ConductMissionState.UNKNOWN_CONDUCT_MISSION_STATE,
                    deadline = datetime.datetime.now() + datetime.timedelta(days=1.0),
                    created_at = datetime.datetime.now(),
                    complete_datetime = datetime.datetime.now() + datetime.timedelta(days=1.0),
                )

                #GetAssignedMission-2
                cntval = ConductMission.select().count().where(
                    (ConductMission.mission_id == mission_id)
                    & (ConductMission.state <=4)
                )

                ms = Mission.select().where(
                    mission_id == Mission.id
                )

                if ms.order_package_quantity >= cntval:
                    Mission.update(state=MissionState.SOLD_OUT).where(Mission.id == mission_id).execute()

                result_code = ResultCode.SUCCESS
                result_message = "GetAssigned Mission Complete"
                assign_mission_result = AssignMissionResult.SUCCESS_ASSIGN_MISSION_RESULT

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                assign_mission_result = AssignMissionResult.FAIL_ASSIGN_MISSION_RESULT

            return GetAssignedMissionResponse(
                result=CommonResult(
                    result_code=result_code,
                    message = result_message,
                ),
                assign_mission_result=assign_mission_result,
            )

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
