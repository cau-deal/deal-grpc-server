from operator import itemgetter

from peewee import Database
from sea.servicer import ServicerMeta

from app.decorators import verified, unverified
from app.extensions import pwdb
from app.extensions_db import sPointServicer

from app.models import DepositPoint
from app.models import WithdrawPoint
from app.models import TransferPoint
from protos.Datetime_pb2 import Datetime

from protos.PointService_pb2 import *
from protos.PointService_pb2_grpc import *

from protos.Date_pb2 import *

from protos.CommonResult_pb2 import *

import datetime

class PointServiceServicer(PointServiceServicer, metaclass=ServicerMeta):
    @verified
    def LookUpBalance(self, request, context):
        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Look up balance Result"

        balance = 0

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                balance = sPointServicer.sLookUpBalance(context.login_email)

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
            balance=balance,
        )

    @verified
    def LookUpPlusPointHistory(self, request, context):
        last_days = request.last_days

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Look up plus history Result"

        POINT_ALTER_REASON = {
            PointAlterReason.UNKNOWN_POINT_ALTER_REASON: 0,
            PointAlterReason.DEPOSIT: 1,
            PointAlterReason.WITHDRAW: 2,
            PointAlterReason.COMPLETED_MISSION: 3,
            PointAlterReason.REQUEST_MISSION: 4,
            PointAlterReason.PLUS_EVENT: 5,
            PointAlterReason.MINUS_EVENT: 6,
        }

        tmp_point_histories = []
        point_histories = []

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                now = datetime.datetime.now()
                from_day = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour,
                                             minute=now.minute, second=now.second) - datetime.timedelta(days=last_days)

                query_deposit = (DepositPoint.select(DepositPoint.val, DepositPoint.created_at)
                         .where((DepositPoint.user_email == context.login_email) & (DepositPoint.created_at >= from_day)))

                query_get_work_point = (TransferPoint.select(TransferPoint.val, TransferPoint.created_at)
                         .where((TransferPoint.receiver_email == context.login_email)
                                & (TransferPoint.created_at >= from_day) & (TransferPoint.mission_id.is_null(False))))

                query_get_event_point = (TransferPoint.select(TransferPoint.val, TransferPoint.created_at)
                         .where((TransferPoint.receiver_email == context.login_email)
                                & (TransferPoint.created_at >= from_day) & (TransferPoint.mission_id.is_null(True))))

                for row in query_deposit:
                    tmp_point_histories.append(
                        {
                            'val': row.val,
                            'point_alter_reason': POINT_ALTER_REASON[PointAlterReason.DEPOSIT],
                            'created_at': row.created_at,
                            'reason_detail': '입금'
                        }
                    )

                for row in query_get_work_point:
                    tmp_point_histories.append(
                        {
                            'val': row.val,
                            'point_alter_reason': POINT_ALTER_REASON[PointAlterReason.COMPLETE_MISSION],
                            'created_at': row.created_at,
                            'reason_detail': '미션 완료'
                        }
                    )

                for row in query_get_event_point:
                    tmp_point_histories.append(
                        {
                            'val': row.val,
                            'point_alter_reason': POINT_ALTER_REASON[PointAlterReason.PLUS_EVENT],
                            'created_at': row.created_at,
                            'reason_detail': '이벤트(포인트 증가)'
                        }
                    )

                tmp_point_histories.sort(key=itemgetter('created_at'), reverse=True)

                s =""

                for row in tmp_point_histories:
                    c = row['created_at']
                    s += row['reason_detail']
                    point_histories.append(
                        PointHistory(
                            val=row['val'],
                            point_alter_reason=row['point_alter_reason'],
                            created_at=Datetime(year=c.year, month=c.month, day=c.day,
                                                hour=c.hour, min=c.minute, sec=c.second),
                            reason_detail=row['reason_detail']
                        )
                    )

                result_code = ResultCode.SUCCESS
                result_message = "Look up plus history success"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                print("EXCEPTION: " + str(e))

        return LookUpPointHistoryResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message + s,
            ),
            point_histories=point_histories,
        )

    @verified
    def LookUpMinusPointHistory(self, request, context):
        last_days = request.last_days

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Look up minus history Result"

        POINT_ALTER_REASON = {
            PointAlterReason.UNKNOWN_POINT_ALTER_REASON: 0,
            PointAlterReason.DEPOSIT: 1,
            PointAlterReason.WITHDRAW: 2,
            PointAlterReason.COMPLETED_MISSION: 3,
            PointAlterReason.REQUEST_MISSION: 4,
            PointAlterReason.PLUS_EVENT: 5,
            PointAlterReason.MINUS_EVENT: 6,
        }

        tmp_point_histories = []
        point_histories = []

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                now = datetime.datetime.now()
                from_day = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour,
                                             minute=now.minute, second=now.second) - datetime.timedelta(days=last_days)

                query_withdraw = (WithdrawPoint.select(WithdrawPoint.val, WithdrawPoint.created_at)
                        .where((WithdrawPoint.user_email == context.login_email) & (WithdrawPoint.created_at >= from_day)))

                query_cost_request_point = (TransferPoint.select(TransferPoint.val, TransferPoint.created_at)
                        .where((TransferPoint.sender_email == context.login_email)
                                & (TransferPoint.created_at >= from_day) & (TransferPoint.mission_id.is_null(False))))

                query_cost_event_point = (TransferPoint.select(TransferPoint.val, TransferPoint.created_at)
                        .where((TransferPoint.sender_email == context.login_email)
                                & (TransferPoint.created_at >= from_day) & (TransferPoint.mission_id.is_null(True))))

                for row in query_withdraw:
                    tmp_point_histories.append(
                        {
                            'val': row.val,
                            'point_alter_reason': POINT_ALTER_REASON[PointAlterReason.WITHDRAW],
                            'created_at': row.created_at,
                            'reason_detail': '출금'
                        }
                    )

                for row in query_cost_request_point:
                    tmp_point_histories.append(
                        {
                            'val': row.val,
                            'point_alter_reason': POINT_ALTER_REASON[PointAlterReason.REQUEST_MISSION],
                            'created_at': row.created_at,
                            'reason_detail': '미션 등록'
                        }
                    )

                for row in query_cost_event_point:
                    tmp_point_histories.append(
                        {
                            'val': row.val,
                            'point_alter_reason': POINT_ALTER_REASON[PointAlterReason.MINUS_EVENT],
                            'created_at': row.created_at,
                            'reason_detail': '이벤트(포인트 감소)'
                        }
                    )

                tmp_point_histories.sort(key=itemgetter('created_at'), reverse=True)

                for row in tmp_point_histories:
                    c = row['created_at']
                    point_histories.append(
                        PointHistory(
                            val=row['val'],
                            point_alter_reason=row['point_alter_reason'],
                            created_at=Datetime(year=c.year, month=c.month, day=c.day,
                                                hour=c.hour, min=c.minute, sec=c.second),
                            reason_detail=row['reason_detail']
                        )
                    )

                result_code = ResultCode.SUCCESS
                result_message = "Look up minus history success"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                print("EXCEPTION: " + str(e))

        return LookUpPointHistoryResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            point_histories=point_histories,
        )

    @verified
    def Deposit(self, request, context):
        deposit = request.deposit

        val = deposit.val
        deposit_type = deposit.deposit_type

        DEPOSIT_TYPE = {
            DepositType.UNKNOWN_DEPOSIT_TYPE: 0,
            DepositType.DEPOSIT_WITHOUT_BANKBOOK: 1,
            DepositType.KAKAO_PAY: 2,
        }

        DEPOSIT_RESULT = {
            DepositResult.UNKNOWN_DEPOSIT_RESULT: 0,
            DepositResult.SUCCESS_DEPOSIT_RESULT: 1,
            DepositResult.FAIL_DEPOSIT_RESULT: 2,
        }

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Deposit"
        deposit_result = DEPOSIT_RESULT[DepositResult.UNKNOWN_DEPOSIT_RESULT]

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                DepositPoint.create(
                    user_email=context.login_email,
                    val=val,
                    kind=DEPOSIT_TYPE[deposit_type],
                    created_at=datetime.datetime.now(),
                )

                result_code = ResultCode.SUCCESS
                result_message = "Deposit success"
                deposit_result = DEPOSIT_RESULT[DepositResult.SUCCESS_DEPOSIT_RESULT]

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                deposit_result = DEPOSIT_RESULT[DepositResult.FAIL_DEPOSIT_RESULT]

        return DepositResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            deposit_result=deposit_result,
        )

    @verified
    def Withdraw(self, request, context):
        withdraw = request.withdraw

        val = withdraw.val

        WITHDRAW_RESULT = {
            WithdrawResult.UNKNOWN_WITHDRAW_RESUTL: 0,
            WithdrawResult.SUCCESS_WITHDRAW_RESULT: 1,
            WithdrawResult.FAIL_WITHDRAW_RESULT: 2,
        }

        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Withdraw"
        withdraw_result = WITHDRAW_RESULT[WithdrawResult.UNKNOWN_WITHDRAW_RESUTL]

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                balance = sPointServicer.sLookUpBalance(context.login_email)

                if balance - val < 0:
                    raise Exception("Insufficiency point balance")

                WithdrawPoint.create(
                    user_email=context.login_email,
                    val=val,
                    created_at=datetime.datetime.now(),
                )

                result_code = ResultCode.SUCCESS
                result_message = "Withdraw success"
                withdraw_result = WITHDRAW_RESULT[WithdrawResult.SUCCESS_WITHDRAW_RESULT]

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                withdraw_result = WITHDRAW_RESULT[WithdrawResult.FAIL_WITHDRAW_RESULT]

        return WithdrawResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            withdraw_result=withdraw_result,
        )

    @verified
    def LookUpEarnForADay(self, request, context):
        result_code = ResultCode.UNKNOWN_RESULT_CODE
        result_message = "Unknown Look up Earn For A Day Result"

        val = 0

        db = pwdb.database

        with db.atomic() as transaction:
            try:
                val = sPointServicer.sLookUpBalanceForADay(context.login_email)

                result_code = ResultCode.SUCCESS
                result_message = "Look up Earn For A Day success"

            except Exception as e:
                transaction.rollback()
                result_code = ResultCode.ERROR
                result_message = str(e)
                print("EXCEPTION: " + str(e))

        return LookUpEarnForADayResponse(
            result=CommonResult(
                result_code=result_code,
                message=result_message,
            ),
            val=val,
        )

