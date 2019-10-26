from peewee import fn

from app.extensions import pwdb
from app.models import DepositPoint, WithdrawPoint, TransferPoint


class SPointerServicer():
    def __init__(self):
        pass

    def sLookUpBalance(self, email):
        balance = 0

        db = pwdb.database

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