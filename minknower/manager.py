import logging
from typing import Iterable, NewType, Optional

import grpc

import minknow.rpc.manager_pb2 as manager
import minknow.rpc.manager_pb2_grpc as manager_rpc

from .flowcell import Flowcell, FlowCellPosition
from .types import FlowCellPosition
from .utils import get_address

class MinKnow:
    def __init__(self, server="localhost", port=9501, logger=None):
        """An adapter class for interacting with Oxford Nanopore Technology nanopore devices.
        This class provides a subset of MinKNOW functionality, and can be used
        for running protocols remotely and streaming data directly from devices like the minION.

        This class also abstracts away the serialization protocol details, providing a
        high-level interface.

        Parameters
        ----------
        server : str, optional
            The hostname of the server hosting the nanopore device, by default "localhost"
        port : int, optional
            The server port that MinKNOW should connect to, by default 9501
        port : logger, optional
            The logger to use for logging. Uses default namespaced logger by default if a logger is not provided.
        """
        self.server = server
        address = get_address(server, port)
        # TODO: Make this a context manager to automatically close connection when finished.
        self.channel = grpc.insecure_channel(address)

        self.logger = logger or logging.getLogger(__name__)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.channel.close()

    def flow_cells(self) -> Iterable[Flowcell]:
        # TODO: ListDevicesReq is depreceatd in 3.6. Maybe as a token of good faith, update the repository
        # example to use flow cell in stead of list_devices.
        manager_stub = manager_rpc.ManagerServiceStub(self.channel)
        flow_cell_positions = manager_stub.flow_cell_positions(
            manager.FlowCellPositionsRequest()
        )

        flow_cells = next(flow_cell_positions).positions

        # TODO: Open all flow-cell connections, or do this lazily?
        def make_flow_cell(cell: FlowCellPosition) -> Flowcell:
            return Flowcell(cell, server=self.server, logger=self.logger)

        flow_cells = map(make_flow_cell, flow_cells)
        return flow_cells

    def default_flow_cell(self) -> Flowcell:
        try:
            return next(self.flow_cells())
        except StopIteration:
            message = "No flow cells found."
            self.logger.error(message)
