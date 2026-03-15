import json
import time
from app.core.arduino import ArduinoInterface
from app.core.models import ArduinoData

# Mocking serial.Serial
class MockSerial:
    def __init__(self, *args, **kwargs):
        self.is_open = True
        self.in_waiting = 0
        self.data_to_read = b""

    def read(self, size):
        res = self.data_to_read[:size]
        self.data_to_read = self.data_to_read[size:]
        self.in_waiting = len(self.data_to_read)
        return res

    def close(self):
        self.is_open = False

import serial
serial.Serial = MockSerial

def test_fragmented_garbage():
    interface = ArduinoInterface(port="MOCK")
    interface.connect()
    
    # Simulate fragmented garbage that looks like valid JSON but not ArduinoData
    garbage = 'Some garbage before {"motion": true} some garbage between {"timestamp": "2026-03-10T11:00:00+01:00", "device": "Arduino UNO", "sensors": {"ultrasonic": {"out_of_range": true}, "pir": {"motion": true}, "rfid": {"card_present": false, "uid": "", "card_type": ""}, "soil_moisture": {"raw": 1}, "ir_receiver": {"received": false, "code": ""}}}'
    
    mock_serial = interface.serial
    mock_serial.data_to_read = garbage.encode('utf-8')
    mock_serial.in_waiting = len(mock_serial.data_to_read)
    
    # Wait for processing
    time.sleep(1.0)
    
    data = interface.read_and_parse()
    if data and data.device == "Arduino UNO":
        print("Success: Final correct object was parsed despite garbage/fragment before it.")
    else:
        print(f"Failed: data is {data}")

    interface.disconnect()

if __name__ == "__main__":
    test_fragmented_garbage()
