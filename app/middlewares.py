import grpc

from sea.pb2 import default_pb2
from app.extensions import JWT
from sea.middleware import BaseMiddleware


class AccessTokenVerifyMiddleWare(BaseMiddleware):

    def before_handler(self, servicer, request, context):
        metadata = dict(context.invocation_metadata())

        try:
            ticket = (metadata['ticket']) if metadata['ticket'] else ""
            context._login_email = JWT.validate(ticket)
            context.verified = True
        except Exception as e:
            print(e)
            context._login_email = ""
            context.verified = False

        return request, context

    def __call__(self, servicer, request, context):
        request, context = self.before_handler(servicer, request, context)
        response = self.handler(servicer, request, context)

        if response is None:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('JWT AUTH FAILED!')
            return default_pb2.Empty()

        return self.after_handler(servicer, response)
