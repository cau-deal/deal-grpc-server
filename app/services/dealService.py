from sea.servicer import ServicerMeta

from app.decorators import unverified, verified
from protos.DealService_pb2_grpc import DealServiceServicer


class DealServiceServicer(DealServiceServicer, metaclass=ServicerMeta):
    @unverified
    def stb(self, request, context):
        print("Hello SengHyeon")

    @verified
    def Inquiry(self, request, context):
        inquiry = request.inquiry
        title = inquiry.title
        contents = inquiry.contents
        return

    def LookUpInquiry(self, request, context):
        return

    def Accuse(self, request, context):
        return


