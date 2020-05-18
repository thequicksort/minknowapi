from .types import FlowCellPosition
from functools import lru_cache
from .protocol import Protocol

from .utils import get_address

import logging
import grpc


from .exception import NoProtocolRunning

from .protocol import find_protocol, ProtocolRunInfo

import minknow.rpc.protocol_pb2 as protocol
import minknow.rpc.protocol_pb2_grpc as protocol_grpc

import minknow.rpc.acquisition_pb2 as ac
import minknow.rpc.acquisition_pb2_grpc as ac_rpc

from google.protobuf.wrappers_pb2 import StringValue
import minknow.rpc.data_pb2 as data
import minknow.rpc.data_pb2_grpc as data_rpc



class Flowcell:
    def __init__(self, flowcell: FlowCellPosition, server="localhost", logger=None):
        self.flowcell = flowcell
        port = flowcell.rpc_ports.insecure
        self.server = server
        address = get_address(server, port)
        self.channel = grpc.insecure_channel(address)

        self.logger = logger or logging.getLogger(__name__)

        self._protocol_stub = protocol_grpc.ProtocolServiceStub(self.channel)
        self._data_stub = data_rpc.DataServiceStub(self.channel)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.channel.close()

    """
    TODO: Generate a "Run" object that combines message ProtocolRunInfo {
    and AcquisitionRunInfo into a single object that has most fields.
    """
    def get_current_run(self) -> ProtocolRunInfo:
        """Gets current run, if one exists

        Returns
        -------
        ProtocolRunInfo
            [description]

        Raises
        ------
        NoProtocolRunning
            [description]
        """
        try:
            protocol_info = self._protocol_stub.get_current_protocol_run(protocol.GetCurrentProtocolRunRequest())
            return protocol_info
        except grpc.RpcError as e:
            raise NoProtocolRunning

    def get_signal_bytes_by_seconds(self, seconds: int, first_channel=1, last_channel=126):
        request = data.GetSignalBytesRequest(seconds=seconds, first_channel=first_channel, last_channel=last_channel)
        bytes_iterator = self._data_stub.get_signal_bytes(request)
        return bytes_iterator

    def get_signal_bytes_by_samples(self, samples: int, first_channel=1, last_channel=126):
        request = data.GetSignalBytesRequest(samples=samples, first_channel=first_channel, last_channel=last_channel)
        bytes_iterator = self._data_stub.get_signal_bytes(request)
        return bytes_iterator

    def _make_run_userinfo(self, experiment_group_id: str, sample_id: str):
        experiment_group_value = StringValue(value=experiment_group_id)
        sample_id_value = StringValue(value=sample_id)
        protocol_user_info = protocol.ProtocolRunUserInfo(protocol_group_id=experiment_group_value, sample_id=sample_id_value)
        return protocol_user_info

    def make_experiment(self, experiment_group_id: str, sample_id: str, flow_cell="FLO-FLG001", kit="SQK-LSK108", experiment_type="sequencing",):
        protocol_user_info = self._make_run_userinfo(experiment_group_id, sample_id)
        protocol_to_start = find_protocol(self.protocols, flow_cell, kit, experiment_type)

        # Sets up the request for starting the protocol
        start_request = protocol.StartProtocolRequest()
        start_request.identifier = protocol_to_start.identifier
        start_request.user_info.CopyFrom(protocol_user_info)

        prot = Protocol(self.channel, start_request=start_request)
        return prot

    def get_protocol(self, flow_cell="FLO-FLG001", kit="SQK-LSK108", experiment_type="sequencing"):
        try:
            proto = find_protocol(
                self.protocols,
                flow_cell=flow_cell,
                kit=kit,
                experiment_type=experiment_type,
            )
            return proto
        except Exception as e:
            self.logger.exception(e)
            raise e

    @property
    def protocols(self, force_reload=False):
        protocol_stub = protocol_grpc.ProtocolServiceStub(self.channel)
        protocols = protocol_stub.list_protocols(protocol.ListProtocolsRequest(force_reload=force_reload))
        return protocols
