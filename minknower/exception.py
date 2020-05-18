# class MinKnowException(Exception):
#     def __init__(self, message, troubleshooting):
#         pass
import grpc

from typing import NewType

#DataType = NewType("DataType", data.GetDataTypesResponse.DataType)

grpc.StatusCode.FAILED_PRECONDITION

class NoFlowCellsFound(Exception):
    """There are no devices or flow cells connected to this machine.

    Troubleshooting steps:
    1) Is the nanopore device plugged into your machine?
    2) Does the nanopore device have a flowcell installed?
    """
    pass

class NoProtocolFound(Exception):
    pass

class NoProtocolRunning(Exception):
    pass



# Utilities and helpers

def is_precondition_failed_error(grpc_error) -> bool:
    is_precondition_failed = grpc_error.code() == grpc.StatusCode.FAILED_PRECONDITION
    return is_precondition_failed

