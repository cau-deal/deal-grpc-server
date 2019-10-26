from sea.server import Server
from sea import create_app
from sea.cli import jobm, JobException


@jobm.job('server', aliases=['s'], help='Run Server')
def server():
    s = Server(create_app(root_path="/home/ubuntu/simple-grpc-server"))
    s.run()
    return 0

server()