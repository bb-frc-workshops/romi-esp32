import board
import struct
import time
from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

"""
const shmemBuffer: {[key: string]: ShmemElementDefinition} = {
    ioConfig: { offset: 0, type: ShmemDataType.UINT16_T},
    firmwareIdent: { offset: 2, type: ShmemDataType.UINT8_T},
    status: { offset: 3, type: ShmemDataType.UINT8_T},
    heartbeat: { offset: 4, type: ShmemDataType.BOOL},
    builtinConfig: { offset: 5, type: ShmemDataType.UINT8_T},
    builtinDioValues: { offset: 6, type: ShmemDataType.BOOL, arraySize: 4},
    extIoValues: { offset: 10, type: ShmemDataType.INT16_T, arraySize: 5},
    analog: { offset: 20, type: ShmemDataType.UINT16_T, arraySize: 2},
    leftMotor: { offset: 24, type: ShmemDataType.INT16_T},
    rightMotor: { offset: 26, type: ShmemDataType.INT16_T},
    batteryMillivolts: { offset: 28, type: ShmemDataType.UINT16_T},
    resetLeftEncoder: { offset: 30, type: ShmemDataType.BOOL},
    resetRightEncoder: { offset: 31, type: ShmemDataType.BOOL},
    leftEncoder: { offset: 32, type: ShmemDataType.INT16_T},
    rightEncoder: { offset: 34, type: ShmemDataType.INT16_T},
};
"""

_ROMI_I2C_ADDR = 0x14
_ROMI_FIRMWARE_IDENT = 118

_ROMI_IOCONFIG: int = const(0x0) # UINT16_T
_ROMI_FIRMWAREID: int = const(0x2) # UINT8_T
_ROMI_STATUS: int = const(0x3) # UINT8_T
_ROMI_HEARTBEAT: int = const(0x4) # BOOL
_ROMI_BUILTIN_CONFIG: int = const(0x5) # UINT8_T
_ROMI_BUILTIN_DIO_VALUES: int = const(0x6) # BOOL x4
_ROMI_EXT_IO_VALUES: int = const(0xA) # INT16_T x5
_ROMI_ANALOG: int = const (0x14) # UINT16_T x2
_ROMI_LEFT_MOTOR: int = const(0x18) # INT16_T
_ROMI_RIGHT_MOTOR: int = const(0x1A) # INT16_T
_ROMI_BATT_MV: int = const(0x1C) # UINT16_T
_ROMI_RESET_LEFT_ENC: int = const(0x1E) # BOOL
_ROMI_RESET_RIGHT_ENC: int = const(0x1F) # BOOL
_ROMI_LEFT_ENC: int = const(0x20) #INT16_T
_ROMI_RIGHT_ENC: int = const(0x22) # INT16_T

class Romi:
    def __init__(self):
        try:
            self.i2c_bus = board.I2C()
        except RuntimeError:
            print("Could not initialize I2C. Check that Romi is powered")
            raise RuntimeError("Could not initialize I2C. Check that Romi is powered")


        self.i2c_device = I2CDevice(self.i2c_bus, _ROMI_I2C_ADDR)
        self._buf = bytearray(12)

        _fw_ident = (self._read_register(_ROMI_FIRMWAREID)[0]) & 0xFF
        if _fw_ident != 118:
            raise ValueError(
                "Unable to find Romi with FW ident " + str(hex(_ROMI_FIRMWARE_IDENT)) + "at address " + str(hex(_ROMI_I2C_ADDR)))

    def _read_register(self, addr: int, num: int = 1) -> int:
        self._buf[0] = addr
        with self.i2c_device as i2c:
            i2c.write_then_readinto(
                self._buf, self._buf, out_end=1, in_start=1, in_end=num + 1
            )
        return self._buf[1 : num + 1]

    def _write_register(self, addr: int, data: int = None) -> None:
        self._buf[0] = addr
        end = 1
        if data:
            self._buf[1] = data
            end = 2
        with self.i2c_device as i2c:
            i2c.write(self._buf, end=end)

    def _write_pack(self, addr: int, format, *data) -> None:
        data_array = list(struct.pack(format, *data))
        self._buf[0] = addr
        end = 1
        for byte in data_array:
            self._buf[end] = byte
            end += 1

        with self.i2c_device as i2c:
            i2c.write(self._buf, end=end)

    def ledDemo(self):
        for i in range(0, 5):
            print("on")
            # self._write_register(_ROMI_BUILTIN_DIO_VALUES + 3, 1)
            self._write_pack(_ROMI_BUILTIN_DIO_VALUES + 3, "B", True)
            time.sleep(0.5)
            print("off")
            # self._write_register(_ROMI_BUILTIN_DIO_VALUES + 3, 0)
            self._write_pack(_ROMI_BUILTIN_DIO_VALUES + 3, "B", False)
            time.sleep(0.5)

    def motorDemo(self):
        print("Starting motors")
        # self._write_register(_ROMI_LEFT_MOTOR, 200)
        # self._write_register(_ROMI_RIGHT_MOTOR, 200)
        self._write_pack(_ROMI_LEFT_MOTOR, "h", 200)
        self._write_pack(_ROMI_RIGHT_MOTOR, "h", 200)

        time.sleep(5)

        print("Stopping_motors")
        # self._write_register(_ROMI_LEFT_MOTOR, 0)
        # self._write_register(_ROMI_RIGHT_MOTOR, 0)

        self._write_pack(_ROMI_LEFT_MOTOR, "h", 0)
        self._write_pack(_ROMI_RIGHT_MOTOR, "h", 0)

        time.sleep(5)

    def get_battery_mv(self) -> int:
        data = self._read_register(_ROMI_BATT_MV, 2)
        return struct.unpack("H", data)
