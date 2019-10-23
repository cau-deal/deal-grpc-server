from google.auth.transport import grpc
from peewee import JOIN
from sea.servicer import ServicerMeta

from app.decorators import verified
from app.extensions import pwdb

from app.models import Mission
from app.models import ConductMission

from protos.CommonResult_pb2 import ResultCode, CommonResult

from protos.Data_pb2 import MissionExplanationImageType
from protos.Data_pb2 import MissionExplanationImage

from protos.MissionService_pb2 import *
from protos.MissionService_pb2_grpc import *


import datetime


class MissionServiceServicer(MissionServiceServicer, metaclass=ServicerMeta):
    @verified
    def RegisterMission(self, request, context):
        # Mission Obj
        ms = request.mission

        # Mission Obj parsing
        mission_id = 0
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

        # JWT.decode()

        with db.atomic() as transaction:
            try:
                query = Mission.create(
                    register_email=context.login_email,
                    title=title,
                    contents=contents,
                    mission_type=mission_type,
                    data_type=data_type,
                    unit_package=unit_package,
                    price_of_package=price_of_package,
                    deadline=deadline,
                    order_package_quantity=order_package_quantity,
                    summary=summary,
                    contact_clause=contact_clause,
                    specification=specification,
                    mission_explanation_images=mission_explanation_images,
                    mission_state=mission_state,
                    created_at=created_at,
                )
                
                # Registered Mission Tuple print
                print(query)

                for images in mission_explanation_images:
                    MissionExplanationImage.create(
                        image_type=MissionExplanationImageType.UNKNOWN_MISSION_EXPLANATION_IMAGE_TYPE,
                        url=images.url,
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
            register_mission_result=register_mission_result
        )

    @verified
    def SearchMission(self, request, context):
        mission_protoes = []

        # Mission Obj parsing
        mission_type = request.mission_type
        keyword = request.keyword
        mission_page = request.mission_page

        mission_page_mode = mission_page.mission_page
        _offset = mission_page._offset
        amount = mission_page.amount

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Search Mission"
        search_mission_result = SearchMissionResult.UNKNOWN_SEARCH_MISSION_RESULT

        NO_KEY_WORD = 1
        YES_KEY_WORD= 2

        if len(keyword) == 0:
            _query_type = NO_KEY_WORD
        else:
            _query_type = YES_KEY_WORD
            keyword = "%" + keyword + "%"

        if mission_page_mode == MissionPageMode.INITAILIZE_MISSION_PAGE:
            _offset = 0

        db = pwdb.database
        with db.atomic as transaction:
            try:
                MEI = MissionExplanationImage.alias()
                MEIT = MissionExplanationImageType.alias()
                # Keyword NOT Exist
                if _query_type == NO_KEY_WORD:
                    # mission type is not all
                    if mission_type != MissionType.ALL_MISSION_TYPE:
                        query = (Mission.select().join(MEI, JOIN.LEFT_OUTER, on=(Mission.id == MEI.mission_id))
                                .where(MEI.image_type == MEIT.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE
                                & Mission.id >= _offset & Mission.mission_type == mission_type)
                                .limit(amount))
                    # mission type is all
                    else:
                        query = (Mission.select().join(MEI, JOIN.LEFT_OUTER, on=(Mission.id == MEI.mission_id))
                                .where(MEI.image_type == MEIT.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE
                                & Mission.id >= _offset)
                                .limit(amount))
                # keyword exist
                else:
                    # mission type is not all
                    if mission_type != MissionType.ALL_MISSION_TYPE:
                        query = (Mission.select().join(MEI, JOIN.LEFT_OUTER, on=(Mission.id == MEI.mission_id))
                                .where(MEI.image_type == MEIT.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE
                                & Mission.id >= _offset & Mission.mission_type == mission_type
                                & (Mission.title ** keyword | Mission.contents ** keyword))
                                .limit(amount))
                    # mission type is all
                    else:
                        query = (Mission.select().join(MEI, JOIN.LEFT_OUTER, on=(Mission.id == MEI.mission_id))
                                .where(MEI.image_type == MEIT.THUMBNAIL_MISSION_EXPLANATION_IMAGE_TYPE
                                & Mission.id >= _offset & (Mission.title ** keyword | Mission.contents ** keyword))
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
    def SearchMissionWithId(self, request, context):
        mission_id = request.mission_id

        db = pwdb.database

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Search Mission With Id"
        search_mission_result = SearchMissionResult.UNKNOWN_SEARCH_MISSION_RESULT

        with db.atomic as transaction:
            try:
                query = Mission.select().where(Mission.id == mission_id)

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
            search_mission_result = search_mission_result,
            mission=query,
        )

    @verified
    def SearchMissionReleventMe(self, request, context):
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    @verified
    def GetAssignedMission(self, request, context):
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
