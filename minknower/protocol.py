import minknow.rpc.protocol_pb2 as protocol
import minknow.rpc.protocol_pb2_grpc as protocol_rpc

from logging import getLogger
from enum import Enum

from typing import NewType

import minknow.rpc.data_pb2 as data
import minknow.rpc.data_pb2_grpc as data_rpc


StartProtocolRequest = NewType("StartProtocolRequest", protocol.StartProtocolRequest)
ProtocolRunInfo = NewType("ProtocolRunInfo", protocol.ProtocolRunInfo)

ProtocolState = Enum(value="ProtocolState", names=protocol.ProtocolState.items())

class Protocol:

    def __init__(self, channel, start_request: StartProtocolRequest):
        """You don't have to worry about creating these yourself. Use the `make_experiment(...)` method of `Flowcell`.

        Parameters
        ----------
        protocol_stub : [type]
            [description]
        start_request : StartProtocolRequest
            [description]
        """
        self.run_id = None
        self.channel = channel
        self._protocol_stub = protocol_rpc.ProtocolServiceStub(channel)
        self._start_request = start_request

    def start(self):
        start_response = self._protocol_stub.start_protocol(self._start_request)
        self.run_id = start_response.run_id

    def stop(self):
        self._protocol_stub.stop_protocol(protocol.StopProtocolRequest())
        self.run_id = None

    # def get_signal_bytes(self, first_channel=1, last_channel=256):
    #     ds.get_signal_bytes(data.GetSignalBytesRequest(seconds=1, first_channel=first_channel, last_channel=last_channel)))

    @property
    def run_info(self):
        run_info = self._protocol_stub.get_run_info(protocol.GetRunInfoRequest())
        return run_info

    @property
    def state(self) -> ProtocolState:
        state = ProtocolState(self.run_info.state)
        return state


# This function is borrowed straight from https://github.com/nanoporetech/minknow_api/blob/fd2f741705a6bca641bf88a3b2acf75276b17158/examples/start_protocol.py#L44
# Define a utility to search for a protocol in the list of returned protocols:
def find_protocol(protocols, flow_cell, kit, experiment_type):
    def has_tag(protocol, tag_name, tag_value):
        # Search each tag to find if it matches the requested tag
        for tag in protocol.tags:
            if tag == tag_name and protocol.tags[tag].string_value == tag_value:
                return True
        return False

    # Search all protocols to find the one with matching flow cell and kit
    for protocol in protocols.protocols:
        if (
            has_tag(protocol, "flow cell", flow_cell)
            and has_tag(protocol, "kit", kit)
            and has_tag(protocol, "experiment type", "sequencing")
        ):
            return protocol

    # Potentially an invalid script combination was requested?
    raise Exception("Protocol %s %s %s not found!" % (flow_cell, kit, experiment_type))

