
from .async_task import *


TESTING = False
DEBUG = True

TIMEZONE = "Asia/Seoul"

GRPC_HOST = "0.0.0.0"
GRPC_PORT = 9091

GRPC_PRIVATE_KEY_PATH = '/home/ubuntu/newdocker/server.key'
GRPC_CERT_CHAIN_PATH = '/home/ubuntu/newdocker/server.crt'


MIDDLEWARES = [
    'sea.middleware.ServiceLogMiddleware',
    'sea.middleware.RpcErrorMiddleware',
    'peeweext.sea.PeeweextMiddleware',
    'app.middlewares.AccessTokenVerifyMiddleWare',
]

PW_MODEL = 'peewee.Model'
PW_DB_URL = 'mysql+pool://deal:deal1234@deal.ct7ygagy10fd.ap-northeast-2.rds.amazonaws.com:3306/deal'
PW_CONN_PARAMS = {'max_connections':5} 
