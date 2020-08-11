# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: job_scheduler.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
    name="job_scheduler.proto",
    package="",
    syntax="proto3",
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
    serialized_pb=b'\n\x13job_scheduler.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\x91\x01\n\x12ScheduleJobRequest\x12\x1f\n\x0bshelf_grows\x18\x01 \x03(\x0b\x32\n.ShelfGrow\x12\x1e\n\ngrow_phase\x18\x02 \x01(\x0b\x32\n.GrowPhase\x12\x13\n\x0bpower_level\x18\x03 \x01(\x05\x12\x11\n\tred_level\x18\x04 \x01(\x05\x12\x12\n\nblue_level\x18\x05 \x01(\x05"5\n\x10ScheduleJobReply\x12\x11\n\tsucceeded\x18\x01 \x01(\x08\x12\x0e\n\x06reason\x18\x02 \x01(\t"P\n\tShelfGrow\x12\x0f\n\x07grow_id\x18\x01 \x01(\x05\x12\x0f\n\x07room_id\x18\x02 \x01(\x05\x12\x0f\n\x07rack_id\x18\x03 \x01(\x05\x12\x10\n\x08shelf_id\x18\x04 \x01(\x05"\xd2\x01\n\tGrowPhase\x12\x0f\n\x07grow_id\x18\x01 \x01(\x05\x12\x18\n\x10recipe_phase_num\x18\x02 \x01(\x05\x12\x11\n\trecipe_id\x18\x03 \x01(\x05\x12\x38\n\x14phase_start_datetime\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x36\n\x12phase_end_datetime\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x15\n\ris_last_phase\x18\x06 \x01(\x08"2\n\x10RemoveJobRequest\x12\x1e\n\ngrow_phase\x18\x02 \x01(\x0b\x32\n.GrowPhase"3\n\x0eRemoveJobReply\x12\x11\n\tsucceeded\x18\x01 \x01(\x08\x12\x0e\n\x06reason\x18\x02 \x01(\t2z\n\x0cJobScheduler\x12\x37\n\x0bScheduleJob\x12\x13.ScheduleJobRequest\x1a\x11.ScheduleJobReply"\x00\x12\x31\n\tRemoveJob\x12\x11.RemoveJobRequest\x1a\x0f.RemoveJobReply"\x00\x62\x06proto3',
    dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,],
)


_SCHEDULEJOBREQUEST = _descriptor.Descriptor(
    name="ScheduleJobRequest",
    full_name="ScheduleJobRequest",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="shelf_grows",
            full_name="ScheduleJobRequest.shelf_grows",
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="grow_phase",
            full_name="ScheduleJobRequest.grow_phase",
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="power_level",
            full_name="ScheduleJobRequest.power_level",
            index=2,
            number=3,
            type=5,
            cpp_type=1,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="red_level",
            full_name="ScheduleJobRequest.red_level",
            index=3,
            number=4,
            type=5,
            cpp_type=1,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="blue_level",
            full_name="ScheduleJobRequest.blue_level",
            index=4,
            number=5,
            type=5,
            cpp_type=1,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=57,
    serialized_end=202,
)


_SCHEDULEJOBREPLY = _descriptor.Descriptor(
    name="ScheduleJobReply",
    full_name="ScheduleJobReply",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="succeeded",
            full_name="ScheduleJobReply.succeeded",
            index=0,
            number=1,
            type=8,
            cpp_type=7,
            label=1,
            has_default_value=False,
            default_value=False,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="reason",
            full_name="ScheduleJobReply.reason",
            index=1,
            number=2,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=204,
    serialized_end=257,
)


_SHELFGROW = _descriptor.Descriptor(
    name="ShelfGrow",
    full_name="ShelfGrow",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="grow_id",
            full_name="ShelfGrow.grow_id",
            index=0,
            number=1,
            type=5,
            cpp_type=1,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="room_id",
            full_name="ShelfGrow.room_id",
            index=1,
            number=2,
            type=5,
            cpp_type=1,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="rack_id",
            full_name="ShelfGrow.rack_id",
            index=2,
            number=3,
            type=5,
            cpp_type=1,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="shelf_id",
            full_name="ShelfGrow.shelf_id",
            index=3,
            number=4,
            type=5,
            cpp_type=1,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=259,
    serialized_end=339,
)


_GROWPHASE = _descriptor.Descriptor(
    name="GrowPhase",
    full_name="GrowPhase",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="grow_id",
            full_name="GrowPhase.grow_id",
            index=0,
            number=1,
            type=5,
            cpp_type=1,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="recipe_phase_num",
            full_name="GrowPhase.recipe_phase_num",
            index=1,
            number=2,
            type=5,
            cpp_type=1,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="recipe_id",
            full_name="GrowPhase.recipe_id",
            index=2,
            number=3,
            type=5,
            cpp_type=1,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="phase_start_datetime",
            full_name="GrowPhase.phase_start_datetime",
            index=3,
            number=4,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="phase_end_datetime",
            full_name="GrowPhase.phase_end_datetime",
            index=4,
            number=5,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="is_last_phase",
            full_name="GrowPhase.is_last_phase",
            index=5,
            number=6,
            type=8,
            cpp_type=7,
            label=1,
            has_default_value=False,
            default_value=False,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=342,
    serialized_end=552,
)


_REMOVEJOBREQUEST = _descriptor.Descriptor(
    name="RemoveJobRequest",
    full_name="RemoveJobRequest",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="grow_phase",
            full_name="RemoveJobRequest.grow_phase",
            index=0,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=554,
    serialized_end=604,
)


_REMOVEJOBREPLY = _descriptor.Descriptor(
    name="RemoveJobReply",
    full_name="RemoveJobReply",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="succeeded",
            full_name="RemoveJobReply.succeeded",
            index=0,
            number=1,
            type=8,
            cpp_type=7,
            label=1,
            has_default_value=False,
            default_value=False,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="reason",
            full_name="RemoveJobReply.reason",
            index=1,
            number=2,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=606,
    serialized_end=657,
)

_SCHEDULEJOBREQUEST.fields_by_name["shelf_grows"].message_type = _SHELFGROW
_SCHEDULEJOBREQUEST.fields_by_name["grow_phase"].message_type = _GROWPHASE
_GROWPHASE.fields_by_name[
    "phase_start_datetime"
].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_GROWPHASE.fields_by_name[
    "phase_end_datetime"
].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_REMOVEJOBREQUEST.fields_by_name["grow_phase"].message_type = _GROWPHASE
DESCRIPTOR.message_types_by_name["ScheduleJobRequest"] = _SCHEDULEJOBREQUEST
DESCRIPTOR.message_types_by_name["ScheduleJobReply"] = _SCHEDULEJOBREPLY
DESCRIPTOR.message_types_by_name["ShelfGrow"] = _SHELFGROW
DESCRIPTOR.message_types_by_name["GrowPhase"] = _GROWPHASE
DESCRIPTOR.message_types_by_name["RemoveJobRequest"] = _REMOVEJOBREQUEST
DESCRIPTOR.message_types_by_name["RemoveJobReply"] = _REMOVEJOBREPLY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ScheduleJobRequest = _reflection.GeneratedProtocolMessageType(
    "ScheduleJobRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _SCHEDULEJOBREQUEST,
        "__module__": "job_scheduler_pb2"
        # @@protoc_insertion_point(class_scope:ScheduleJobRequest)
    },
)
_sym_db.RegisterMessage(ScheduleJobRequest)

ScheduleJobReply = _reflection.GeneratedProtocolMessageType(
    "ScheduleJobReply",
    (_message.Message,),
    {
        "DESCRIPTOR": _SCHEDULEJOBREPLY,
        "__module__": "job_scheduler_pb2"
        # @@protoc_insertion_point(class_scope:ScheduleJobReply)
    },
)
_sym_db.RegisterMessage(ScheduleJobReply)

ShelfGrow = _reflection.GeneratedProtocolMessageType(
    "ShelfGrow",
    (_message.Message,),
    {
        "DESCRIPTOR": _SHELFGROW,
        "__module__": "job_scheduler_pb2"
        # @@protoc_insertion_point(class_scope:ShelfGrow)
    },
)
_sym_db.RegisterMessage(ShelfGrow)

GrowPhase = _reflection.GeneratedProtocolMessageType(
    "GrowPhase",
    (_message.Message,),
    {
        "DESCRIPTOR": _GROWPHASE,
        "__module__": "job_scheduler_pb2"
        # @@protoc_insertion_point(class_scope:GrowPhase)
    },
)
_sym_db.RegisterMessage(GrowPhase)

RemoveJobRequest = _reflection.GeneratedProtocolMessageType(
    "RemoveJobRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _REMOVEJOBREQUEST,
        "__module__": "job_scheduler_pb2"
        # @@protoc_insertion_point(class_scope:RemoveJobRequest)
    },
)
_sym_db.RegisterMessage(RemoveJobRequest)

RemoveJobReply = _reflection.GeneratedProtocolMessageType(
    "RemoveJobReply",
    (_message.Message,),
    {
        "DESCRIPTOR": _REMOVEJOBREPLY,
        "__module__": "job_scheduler_pb2"
        # @@protoc_insertion_point(class_scope:RemoveJobReply)
    },
)
_sym_db.RegisterMessage(RemoveJobReply)


_JOBSCHEDULER = _descriptor.ServiceDescriptor(
    name="JobScheduler",
    full_name="JobScheduler",
    file=DESCRIPTOR,
    index=0,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
    serialized_start=659,
    serialized_end=781,
    methods=[
        _descriptor.MethodDescriptor(
            name="ScheduleJob",
            full_name="JobScheduler.ScheduleJob",
            index=0,
            containing_service=None,
            input_type=_SCHEDULEJOBREQUEST,
            output_type=_SCHEDULEJOBREPLY,
            serialized_options=None,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.MethodDescriptor(
            name="RemoveJob",
            full_name="JobScheduler.RemoveJob",
            index=1,
            containing_service=None,
            input_type=_REMOVEJOBREQUEST,
            output_type=_REMOVEJOBREPLY,
            serialized_options=None,
            create_key=_descriptor._internal_create_key,
        ),
    ],
)
_sym_db.RegisterServiceDescriptor(_JOBSCHEDULER)

DESCRIPTOR.services_by_name["JobScheduler"] = _JOBSCHEDULER

# @@protoc_insertion_point(module_scope)
