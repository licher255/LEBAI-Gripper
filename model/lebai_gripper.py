# model/lebai_gripper.py
import serial
import serial.tools.list_ports
import time

class LEBAI_Gripper:
    def __init__(self, com=None, baudrate=115200, address=1, debug=False):
        self.com = com
        self.baudrate = baudrate
        self.address = address
        self.debug = debug
        self.ser = None
        self.status = {
            'position': None,
            'torque': None,
            'is_moving': None,
            'homing_done': None,
            'speed': None,
        }

    def _crc16(self, data: bytes) -> bytes:
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc.to_bytes(2, byteorder='little')

    def connect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        try:
            self.ser = serial.Serial(
                port=self.com,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            return True
        except Exception as e:
            if self.debug:
                print(f"[ERROR] Connect failed: {e}")
            return False

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None

    def _send_and_receive(self, packet: bytes, expected_length: int = None) -> bytes:
        if not self.ser or not self.ser.is_open:
            return None

        try:
            self.ser.flushInput()
            self.ser.write(packet)
            self.ser.flush()
            
            # 给 RS485 足够时间切换方向 + 设备响应
            time.sleep(0.02)  # 20ms
            
            response = self.ser.read(expected_length or 100)
            
            # --- 以下逻辑全部在 try 内部 ---
            if not response:
                if self.debug:
                    print("[DEBUG] No response received")
                return None
                
            if len(response) < 5:
                if self.debug:
                    print(f"[DEBUG] Response too short: {response.hex()}")
                return None

            received_crc = response[-2:]
            calculated_crc = self._crc16(response[:-2])
            if received_crc != calculated_crc:
                if self.debug:
                    print(f"[DEBUG] CRC mismatch: got {received_crc.hex()}, expected {calculated_crc.hex()}")
                return None

            return response

        except Exception as e:
            if self.debug:
                print(f"[ERROR] Serial communication failed: {e}")
            return None

    def _build_write_packet(self, reg_l: int, value: int) -> bytes:
        addr = self.address.to_bytes(1, 'big')
        func = b'\x10'
        reg_h = b'\x9C'
        reg_l = reg_l.to_bytes(1, 'big')
        reg_count = b'\x00\x01'
        byte_count = b'\x02'
        data = value.to_bytes(2, 'big')
        frame = addr + func + reg_h + reg_l + reg_count + byte_count + data
        crc = self._crc16(frame)
        return frame + crc

    def _build_read_packet(self, reg_l: int) -> bytes:
        addr = self.address.to_bytes(1, 'big')
        func = b'\x03'
        reg_h = b'\x9C'
        reg_l = reg_l.to_bytes(1, 'big')
        reg_count = b'\x00\x01'
        frame = addr + func + reg_h + reg_l + reg_count
        crc = self._crc16(frame)
        return frame + crc

    def _parse_write_response(self, resp: bytes) -> bool:
        return resp is not None and len(resp) >= 8 and resp[0] == self.address and resp[1] == 0x10

    def _parse_read_response(self, resp: bytes) -> int:
        if resp and len(resp) >= 5 and resp[0] == self.address and resp[1] == 0x03 and resp[2] == 2:
            return int.from_bytes(resp[3:5], 'big')
        return None

    # === Public API ===
    def set_position(self, percent: int):
        assert 0 <= percent <= 100
        packet = self._build_write_packet(0x40, percent)
        resp = self._send_and_receive(packet, 8)
        success = self._parse_write_response(resp)
        if success:
            self.status['position'] = percent
        return success

    def set_force(self, force: int):
        assert 0 <= force <= 100
        packet = self._build_write_packet(0x41, force)
        resp = self._send_and_receive(packet, 8)
        return self._parse_write_response(resp)

    def set_speed(self, speed: int):
        assert 0 <= speed <= 100
        packet = self._build_write_packet(0x4A, speed)
        resp = self._send_and_receive(packet, 8)
        if self._parse_write_response(resp):
            self.status['speed'] = speed
        return True

    def save_speed(self):
        packet = self._build_write_packet(0x4B, 0)
        resp = self._send_and_receive(packet, 8)
        return self._parse_write_response(resp)

    def start_homing(self):
        packet = self._build_write_packet(0x48, 1)
        resp = self._send_and_receive(packet, 8)
        return self._parse_write_response(resp)

    def stop_auto_homing(self, value:int):
        packet = self._build_write_packet(0x9A, value) 
        # value: 
        # 1 关闭 
        # 2 关闭自动找行程并且断电保存 
        # 3 恢复自动找行程并且断电保存
        resp = self._send_and_receive(packet, 8)
        return self._parse_write_response(resp)

    def read_position(self):
        packet = self._build_read_packet(0x45)
        resp = self._send_and_receive(packet, 7)
        val = self._parse_read_response(resp)
        if val is not None:
            self.status['position'] = val
        return val

    def read_torque(self):
        packet = self._build_read_packet(0x46)
        resp = self._send_and_receive(packet, 7)
        val = self._parse_read_response(resp)
        if val is not None:
            self.status['torque'] = val
        return val

    def is_command_done(self):
        packet = self._build_read_packet(0x47)
        resp = self._send_and_receive(packet, 7)
        val = self._parse_read_response(resp)
        self.status['is_moving'] = (val == 0) if val is not None else None
        return val == 1 if val is not None else None

    def is_homing_done(self):
        packet = self._build_read_packet(0x49)
        resp = self._send_and_receive(packet, 7)
        val = self._parse_read_response(resp)
        done = (val == 1) if val is not None else None
        self.status['homing_done'] = done
        return done

    @staticmethod
    def list_ports():
        return [port.device for port in serial.tools.list_ports.comports()]