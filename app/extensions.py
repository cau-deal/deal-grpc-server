import hashlib

import firebase_admin

# from sea.contrib.extensions.celery import AsyncTask
from peeweext.sea import Peeweext
from firebase_admin import credentials

from extensions.jwt import JWT
from extensions.emailSender import EmailSender
from extensions.KakaoPayUrlGet import KakaoPayUrl

root_email = 'grpc_test@test.com'

pwdb = Peeweext()

firebase_cred = credentials.Certificate("/home/ubuntu/simple-grpc-server/keys/firebase-service.json")
firebase = firebase_admin.initialize_app(firebase_cred)

JWT = JWT()
EmailSender = EmailSender()  # todo 계정정보 파일로 빼자
KakaoPayUrl = KakaoPayUrl()
