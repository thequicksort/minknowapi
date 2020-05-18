from typing import NewType
from enum import Enum
import minknow.rpc.protocol_pb2 as protocol
import minknow.rpc.manager_pb2 as manager


##################
# Flow Cell
##################

FlowCellPosition = NewType("FlowCellPosition", manager.FlowCellPosition)


##################
# Protocol
##################

from .protocol import ProtocolState, StartProtocolRequest
