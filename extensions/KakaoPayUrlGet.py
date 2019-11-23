import requests
import json
import os

class KakaoPayUrl:
    def __init__(self):
        self.secret = 'secret'

    def getTidAndUrl(self, email, amount):
        kko_pay_key = open(os.getcwd()+'/extensions/kakaopay_key.json')
        key_data = json.load(kko_pay_key)

        header = {
            'Authorization':str(key_data['kakao_auth']),
        }
        params ={
            'cid':'TC0ONETIME',
            'item_name':'포인트',
            'quantity':str(1),
            'total_amount':str(amount),
            'vat_amount':str(0),
            'approval_url':str(key_data['approval_url']),
            'fail_url':str(key_data['fail_url']),
            'cancel_url':str(key_data['cancel_url']),
            'partner_order_id':'partner_order_id',
            'partner_user_id':email,
            'tax_free_amount':str(0)
        }

        res = requests.post('https://kapi.kakao.com/v1/payment/ready', headers=header, data=params).json()
        return res['tid'], res['next_redirect_mobile_url']

