import minknow.rpc.acquisition_pb2 as ac
import minknow.rpc.acquisition_pb2_grpc as ac_rpc

from typing import NewType
from enum import Enum
CurrentStatusResponse = NewType("CurrentStatusResponse", ac.CurrentStatusResponse)
MinknowStatus = Enum(value="MinknowStatus", names=ac.MinknowStatus.items())


class Acquisition:

    def __init__(self, channel):
        self.channel = channel
        self._stub = ac_rpc.AcquisitionServiceStub(channel)

    @property
    def current_status(self) -> MinknowStatus:
        request = ac.CurrentStatusRequest()
        status = MinknowStatus(self._stub.current_status(request).status)
        return status

    def start(self):
        print("Making request")
        request = ac.StartRequest()
        print("Made request")
        resp = self._stub.start(request)
        print(f"Got response: {resp!s}")
        return resp

    def stop(self):
        request = ac.StopRequest()
        resp = self._stub.stop(request)
        return resp

    def list_runs(self):
        request = ac.ListAcquisitionRunsRequest()
        resp = self._stub.list_acquisition_runs(request)
        return resp


#     def get_acquisition_info(self):
#         request = ac.GetAcquisitionRunInfoRequest()

#     'current_status', 'get_acquisition_info', 'get_current_acqu
# isition_run', 'get_progress', 'list_acquisition_runs', 'set_signal_reader', 'start', 'stop', 'watch_c
# urrent_acquisition_run', 'watch_for_status_change'