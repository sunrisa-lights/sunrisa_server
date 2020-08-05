# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import app.job_scheduler.job_scheduler_pb2 as job__scheduler__pb2


class JobSchedulerStub(object):
    """The JobScheduler service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ScheduleJob = channel.unary_unary(
            "/JobScheduler/ScheduleJob",
            request_serializer=job__scheduler__pb2.ScheduleJobRequest.SerializeToString,
            response_deserializer=job__scheduler__pb2.ScheduleJobReply.FromString,
        )


class JobSchedulerServicer(object):
    """The JobScheduler service definition.
    """

    def ScheduleJob(self, request, context):
        """Schedules a job on the job scheduler
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_JobSchedulerServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "ScheduleJob": grpc.unary_unary_rpc_method_handler(
            servicer.ScheduleJob,
            request_deserializer=job__scheduler__pb2.ScheduleJobRequest.FromString,
            response_serializer=job__scheduler__pb2.ScheduleJobReply.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "JobScheduler", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class JobScheduler(object):
    """The JobScheduler service definition.
    """

    @staticmethod
    def ScheduleJob(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/JobScheduler/ScheduleJob",
            job__scheduler__pb2.ScheduleJobRequest.SerializeToString,
            job__scheduler__pb2.ScheduleJobReply.FromString,
            options,
            channel_credentials,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
