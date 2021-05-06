# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import customers_pb2 as customers__pb2


class BranchStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Propagate_Deposit = channel.unary_unary(
                '/bank.Branch/Propagate_Deposit',
                request_serializer=customers__pb2.Event.SerializeToString,
                response_deserializer=customers__pb2.ResponseStatus.FromString,
                )
        self.Propagate_Withdraw = channel.unary_unary(
                '/bank.Branch/Propagate_Withdraw',
                request_serializer=customers__pb2.Event.SerializeToString,
                response_deserializer=customers__pb2.ResponseStatus.FromString,
                )
        self.MsgDelivery = channel.unary_unary(
                '/bank.Branch/MsgDelivery',
                request_serializer=customers__pb2.Event.SerializeToString,
                response_deserializer=customers__pb2.EventResponse.FromString,
                )
        self.InitStubs = channel.unary_unary(
                '/bank.Branch/InitStubs',
                request_serializer=customers__pb2.CustNodes.SerializeToString,
                response_deserializer=customers__pb2.ResponseStatus.FromString,
                )


class BranchServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Propagate_Deposit(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Propagate_Withdraw(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def MsgDelivery(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def InitStubs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BranchServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Propagate_Deposit': grpc.unary_unary_rpc_method_handler(
                    servicer.Propagate_Deposit,
                    request_deserializer=customers__pb2.Event.FromString,
                    response_serializer=customers__pb2.ResponseStatus.SerializeToString,
            ),
            'Propagate_Withdraw': grpc.unary_unary_rpc_method_handler(
                    servicer.Propagate_Withdraw,
                    request_deserializer=customers__pb2.Event.FromString,
                    response_serializer=customers__pb2.ResponseStatus.SerializeToString,
            ),
            'MsgDelivery': grpc.unary_unary_rpc_method_handler(
                    servicer.MsgDelivery,
                    request_deserializer=customers__pb2.Event.FromString,
                    response_serializer=customers__pb2.EventResponse.SerializeToString,
            ),
            'InitStubs': grpc.unary_unary_rpc_method_handler(
                    servicer.InitStubs,
                    request_deserializer=customers__pb2.CustNodes.FromString,
                    response_serializer=customers__pb2.ResponseStatus.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'bank.Branch', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Branch(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Propagate_Deposit(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/bank.Branch/Propagate_Deposit',
            customers__pb2.Event.SerializeToString,
            customers__pb2.ResponseStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Propagate_Withdraw(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/bank.Branch/Propagate_Withdraw',
            customers__pb2.Event.SerializeToString,
            customers__pb2.ResponseStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def MsgDelivery(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/bank.Branch/MsgDelivery',
            customers__pb2.Event.SerializeToString,
            customers__pb2.EventResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def InitStubs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/bank.Branch/InitStubs',
            customers__pb2.CustNodes.SerializeToString,
            customers__pb2.ResponseStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
