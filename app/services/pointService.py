from peewee import Database
from sea.servicer import ServicerMeta

from app.decorators import verified, unverified
from app.extensions import JWT, pwdb, EmailSender

from app.models import DepositPoint
from app.models import WithdrawPoint
from app.models import TransferPoint

from protos.PointService_pb2 import *
from protos.PointService_pb2_grpc import *

from protos.Date_pb2 import *

from protos.CommonResult_pb2 import *

from peewee import fn

import datetime


class PointServiceServicer(PointServiceServicer, metaclass=ServicerMeta):

    @verified
    def LookUpBalance(self, request, context):
        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Look up balance Result"

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                total_deposit = (DepositPoint.select(fn.Sum(DepositPoint.val))
                                 .where(DepositPoint.user_email==context.login_email)).scalar()
                total_withdraw = (WithdrawPoint.select(fn.Sum(WithdrawPoint.val))
                                 .where(WithdrawPoint.user_email==context.login_email)).scalar()
                total_receive = (TransferPoint.select(fn.Sum(TransferPoint.val))
                                 .where(TransferPoint.receiver_email==context.login_email)).scalar()
                total_send = (TransferPoint.select(fn.Sum(TransferPoint.val))
                                 .where(TransferPoint.sender_email==context.login_email)).scalar()

                result_code = ResultCode.SUCCESS
                result_message = "Look up balance success"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                print("EXCEPTION: " + str(e))

        return LookUpBalanceResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            balance=total_deposit + total_receive - total_withdraw - total_send,
        )

    @verified
    def LookUpPlusPointHistory(self, request, context):
        last_days = request.last_days

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Look up plus history Result"

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                from_day = datetime.now() - datetime.timedelta(days=last_days)
                query_deposit = (DepositPoint.select(DepositPoint.val, DepositPoint.created_at)
                         .where(DepositPoint.user_email==context.login_email and DepositPoint.created_at >= from_day))
                query_get_work_point = (TransferPoint.select(TransferPoint.val, TransferPoint.created_at)
                         .where(TransferPoint.receiver_email==context.login_email
                                and TransferPoint.created_at >= from_day and TransferPoint.mission_id.is_null(False)))
                query_get_event_point = (TransferPoint.select(TransferPoint.val, TransferPoint.created_at)
                         .where(TransferPoint.receiver_email==context.login_email
                                and TransferPoint.created_at >= from_day and TransferPoint.mission_id.is_null(True)))

                result_code = ResultCode.SUCCESS
                result_message = "Look up plus history success"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                print("EXCEPTION: " + str(e))

            point_histories = []

            POINT_ALTER_REASON = {
                PointAlterReason.UNKNOWN_POINT: 0,
                PointAlterReason.DEPOSIT: 1,
                PointAlterReason.WITHDRAW: 2,
                PointAlterReason.COMPLETE_MISSION: 3,
                PointAlterReason.REQUEST_MISSION: 4,
                PointAlterReason.PLUS_EVENT: 5,
                PointAlterReason.MINUS_EVENT: 6,
            }

            for row in query_deposit:
                point_histories.append(
                    PointHistory(
                        val=row.val,
                        point_alter_reason=POINT_ALTER_REASON[PointAlterReason.DEPOSIT],
                        created_at=row.created_at,
                    )
                )

            for row in query_get_work_point:
                point_histories.append(
                    PointHistory(
                        val=row.val,
                        point_alter_reason=POINT_ALTER_REASON[PointAlterReason.COMPLETE_MISSION],
                        created_at=row.created_at,
                    )
                )

            for row in query_deposit:
                point_histories.append(
                    PointHistory(
                        val=row.val,
                        point_alter_reason=POINT_ALTER_REASON[PointAlterReason.PLUS_EVENT],
                        created_at=row.created_at,
                    )
                )

            # 버그 예상 지점
            point_histories.sort(key=PointHistory.created_at, reverse=True)

        return LookUpBalanceResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            point_histories=point_histories,
        )

    @verified
    def LookUpMinusPointHistory(self, request, context):
        last_days = request.last_days

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Look up plus history Result"

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                from_day = datetime.now() - datetime.timedelta(days=last_days)
                query_withdraw = (WithdrawPoint.select(WithdrawPoint.val, WithdrawPoint.created_at)
                         .where(WithdrawPoint.user_email==context.login_email and WithdrawPoint.created_at >= from_day))
                query_cost_request_point = (TransferPoint.select(TransferPoint.val, TransferPoint.created_at)
                         .where(TransferPoint.sender_email==context.login_email
                                and TransferPoint.created_at >= from_day and TransferPoint.mission_id.is_null(False)))
                query_cost_event_point = (TransferPoint.select(TransferPoint.val, TransferPoint.created_at)
                         .where(TransferPoint.sender_email==context.login_email
                                and TransferPoint.created_at >= from_day and TransferPoint.mission_id.is_null(True)))

                result_code = ResultCode.SUCCESS
                result_message = "Look up minus history success"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                print("EXCEPTION: " + str(e))

            point_histories = []

            POINT_ALTER_REASON = {
                PointAlterReason.UNKNOWN_POINT: 0,
                PointAlterReason.DEPOSIT: 1,
                PointAlterReason.WITHDRAW: 2,
                PointAlterReason.COMPLETE_MISSION: 3,
                PointAlterReason.REQUEST_MISSION: 4,
                PointAlterReason.PLUS_EVENT: 5,
                PointAlterReason.MINUS_EVENT: 6,
            }

            for row in query_withdraw:
                point_histories.append(
                    PointHistory(
                        val=row.val,
                        point_alter_reason=POINT_ALTER_REASON[PointAlterReason.DEPOSIT],
                        created_at=row.created_at,
                    )
                )

            for row in query_cost_request_point:
                point_histories.append(
                    PointHistory(
                        val=row.val,
                        point_alter_reason=POINT_ALTER_REASON[PointAlterReason.COMPLETE_MISSION],
                        created_at=row.created_at,
                    )
                )

            for row in query_cost_event_point:
                point_histories.append(
                    PointHistory(
                        val=row.val,
                        point_alter_reason=POINT_ALTER_REASON[PointAlterReason.PLUS_EVENT],
                        created_at=row.created_at,
                    )
                )

            # 버그 예상 지점
            point_histories.sort(key=PointHistory.created_at, reverse=True)

        return LookUpBalanceResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            point_histories=point_histories,
        )

    @verified
    def Deposit(self, request, context):
        return

    @verified
    def Withdraw(self, request, context):
        return
