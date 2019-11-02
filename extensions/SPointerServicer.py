import datetime

from peewee import fn

from app.extensions import pwdb
from app.models import DepositPoint, WithdrawPoint, TransferPoint


class SPointerServicer():
    def __init__(self):
        pass

    def sLookUpBalance(self, email):
        balance = 0

        total_deposit_query = (DepositPoint.select(fn.Sum(DepositPoint.val).alias('total'))
                                 .where(DepositPoint.user_email == email))
        total_withdraw_query = (WithdrawPoint.select(fn.Sum(WithdrawPoint.val).alias('total'))
                                 .where(WithdrawPoint.user_email == email))
        total_receive_query = (TransferPoint.select(fn.Sum(TransferPoint.val).alias('total'))
                                 .where(TransferPoint.receiver_email == email))
        total_send_query = (TransferPoint.select(fn.Sum(TransferPoint.val).alias('total'))
                                 .where(TransferPoint.sender_email == email))

        for row in total_deposit_query:
            if row.total is not None:
                balance += row.total
        for row in total_withdraw_query:
            if row.total is not None:
                balance -= row.total
        for row in total_receive_query:
            if row.total is not None:
                balance += row.total
        for row in total_send_query:
            if row.total is not None:
                balance -= row.total

        return int(balance)

    def sLookUpBalanceForADay(self, email):
        balance = 0

        now = datetime.datetime.now()
        from_day = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour,
                                    minute=now.minute, second=now.second) - datetime.timedelta(days=1)

        total_receive_query = (TransferPoint.select(fn.Sum(TransferPoint.val).alias('total'))
                                 .where((TransferPoint.receiver_email == email) & (TransferPoint.created_at >= from_day)))

        for row in total_receive_query:
            if row.total is not None:
                balance += row.total

        return int(balance)

    def givePoint(self, sender_email, receiver_email, val, mission_id=0):
        db = pwdb.database

        with db.atomic() as transaction:
            try:
                balance = self.sLookUpBalance(sender_email)

                if balance < val:
                    raise Exception('Insufficiency point')

                if mission_id == 0 or mission_id is None:
                    TransferPoint.create(
                        sender_email=sender_email,
                        receiver_email=receiver_email,
                        val=val,
                    )
                else:
                    TransferPoint.create(
                        sender_email=sender_email,
                        receiver_email=receiver_email,
                        val=val,
                        mission_id=mission_id,
                    )
            except Exception as e:
                transaction.rollback()
                raise Exception(str(e) + '   give point fail')
