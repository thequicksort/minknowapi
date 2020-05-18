from enum import Enum

from typing import NewType, Union

import minknow.rpc.data_pb2 as data
import minknow.rpc.data_pb2_grpc as data_rpc

DataType = NewType("DataType", data.GetDataTypesResponse.DataType)
import numpy as np

DataTypeType = Enum(value="DataTypeType", names=data.GetDataTypesResponse.DataType.Type.items())


def get_numpy_type(dataType: DataType) -> Union[np.uint8, np.uint16, np.uint32, np.int8, np.int16, np.int32, np.float]:
    datatype = (dataType.type, dataType.size)
    # Mapping of (type, size) to a numpy data type.
    type_and_size_to_numpy = {
        (DataTypeType.UNSIGNED_INTEGER.value, 1): np.uint8,
        (DataTypeType.UNSIGNED_INTEGER.value, 2): np.uint16,
        (DataTypeType.UNSIGNED_INTEGER.value, 4): np.uint32,
        (DataTypeType.SIGNED_INTEGER.value, 1): np.int8,
        (DataTypeType.SIGNED_INTEGER.value, 2): np.int16,
        (DataTypeType.SIGNED_INTEGER.value, 4): np.int32,
        (DataTypeType.FLOATING_POINT.value, 4): np.float,
    }

    numpy_type = type_and_size_to_numpy[datatype]
    return numpy_type

# import minknow.rpc.data_pb2 as data
# import minknow.rpc.data_pb2_grpc as data_rpc
#     ds = data_rpc.DataServiceStub(fc.channel); ds.get_data_types(data.GetDataTypesRequest())