
import minknow.rpc.data_pb2 as data
import minknow.rpc.data_pb2_grpc as data_rpc


import minknow.rpc.device_pb2 as device
import minknow.rpc.device_pb2_grpc as device_rpc


UnblockRequest = device.UnblockRequest
GetSampleRateRequest = device.GetSampleRateRequest

GetTemperatureRequest = device.GetTemperatureRequest
SetTemperatureRequest = device.SetTemperatureRequest
GetCalibrationRequest = device.GetCalibrationRequest

from typing import Sequence, NewType

GetChannelConfigurationResponse = NewType("GetChannelConfigurationResponse", device.GetChannelConfigurationResponse)
SetTemperatureResponse = NewType("SetTemperatureResponse", device.SetTemperatureResponse)
GetTemperatureResponse = NewType("GetTemperatureResponse", device.GetTemperatureResponse)
GetCalibrationResponse = NewType("GetCalibrationResponse", device.GetCalibrationResponse)

class Device:

    def __init__(self, channel):
        self.channel = channel
        self._device_stub = device_rpc.DeviceServiceStub(channel)

    def unblock_for_seconds(self, seconds: int, channels: Sequence[int]):
        self._device_stub.unblock(UnblockRequest(channels=channels, duration_in_seconds=seconds))

    def unblock_for_milliseconds(self, milliseconds: int, channels: Sequence[int]):
        self._device_stub.unblock(UnblockRequest(channels=channels, duration_in_milliseconds=milliseconds))

    def get_channel_config(self, channels: Sequence[int]) -> GetChannelConfigurationResponse:
        resp = self._device_stub.get_channel_configuration(device.GetChannelConfigurationRequest(channels=channels))
        return resp

    def get_calibration(self, first_channel=1, last_channel=1):
        request = GetCalibrationRequest(first_channel=first_channel, last_channel=last_channel)
        resp = self._device_stub.get_calibration(request)
        return resp


    def wait_for_temperature(self, temperature: float, timeout=600, min_stable_duration=0, tolerance=0.5) -> SetTemperatureResponse:
        """Tries to set the device temperature, blocking until the desired temperature is reached.
        Temperature must be within the device's allowed ranges.

        Parameters
        ----------
        temperature : float
            Desired temperature (in degrees celcius).
        timeout : int, optional
            Maximum time to wait for the device to reach temperature before giving up in seconds, by default 600 (5 minutes)
        min_stable_duration : int, optional
            Minimum time the device must be at temperature before proceeding (in seconds), by default 0
        tolerance : float, optional
            Tolerance range for the temperature to be considered in range (in degrees celcius), by default 0.5

        Returns
        -------
        SetTemperatureResponse
            Response indicating whether we timed out before the temperature was reached.
        """
        request = SetTemperatureRequest(temperature=temperature, wait_for_temperature={"timeout": timeotu, "min_stable_duration": min_stable_duration, "tolerance": tolerance})
        resp = self._device_stub.set_temperature(request)
        return resp

    @property
    def temperature(self) -> GetTemperatureResponse:
        request = GetTemperatureRequest()
        resp = self._device_stub.get_temperature(request)
        return resp

    @temperature.setter
    def temperature(self, temperature: float) -> SetTemperatureResponse:
        request = SetTemperatureRequest(temperature=temperature)
        resp = self._device_stub.set_temperature(request)
        return resp


    @property
    def sample_rate(self):
        resp = self._device_stub.get_sample_rate(GetSampleRateRequest())
        rate = resp.sample_rate
        return rate

    # @sample_rate.setter
    # def _get_sample_rate(self) -> int:
    #     """
    #     Gets the device's current sampling rate.
    #     """
    #     resp = self._device_stub.get_sample_rate(GetSampleRateRequest())
    #     rate = resp.sample_rate
    #     return rate

    @sample_rate.setter
    def sample_rate(self, sample_rate: int) -> int:
        """Sets the approximate sample rate for the device.

        Note that the real sample rate may not match the given one, as each device
        rounds differently (e.g. the promethion rounds to the nearest 1000 Hz).

        Parameters
        ----------
        sample_rate : int
            Desired sample rate (this will be rounded to a real sample rate on the device).

        Returns
        -------
        int
            The real sample rate on this device.
        """
        resp = self._device_stub.get_sample_rate(SetSampleRateRequest(sample_rate=sample_rate))
        rate = resp.real_sample_rate
        return rate

    @property
    def bias_voltage(self):
       """Bias voltage applied across the well (in millivolts). Must be a multiple of 5 (because the documentation says so).

       Returns
       -------
       [type]
           [description]
       """
       resp = self._device_stub.get_bias_voltage(device.GetBiasVoltageRequest())
       voltage = resp.bias_voltage
       return voltage

    @bias_voltage.setter
    def bias_voltage(self, voltage):
        resp = self.devstub.set_bias_voltage(device.SetBiasVoltageRequest(bias_voltage=voltage))