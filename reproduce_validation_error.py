import json
import time
from app.core.arduino import ArduinoInterface
from app.core.models import ArduinoData
import logging

# Configure logger
logging.basicConfig(level=logging.DEBUG)

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

def test_validation_error():
    interface = ArduinoInterface(port="MOCK")
    interface.connect()
    
    # Simulate a buffer with a different JSON object that doesn't match ArduinoData
    # followed by a valid ArduinoData object.
    # The issue description shows an object with {'received': True, 'code': '0x0'}
    invalid_obj = '{"received": true, "code": "0x0"}'
    valid_obj = '{"timestamp": "2026-03-10T11:00:00+01:00", "device": "Arduino UNO", "sensors": {"ultrasonic": {"out_of_range": true}, "pir": {"motion": true}, "rfid": {"card_present": false, "uid": "", "card_type": ""}, "soil_moisture": {"raw": 1}, "ir_receiver": {"received": false, "code": ""}}}'
    
    mock_serial = interface.serial
    # Case 1: invalid then valid
    mock_serial.data_to_read = (invalid_obj + valid_obj).encode('utf-8')
    mock_serial.in_waiting = len(mock_serial.data_to_read)
    
    # Wait for processing
    time.sleep(0.5)
    
    data = interface.read_and_parse()
    if data and data.device == "Arduino UNO":
        print("Success: Valid object was parsed after invalid one.")
    else:
        print(f"Failed: data is {data}")

    # Case 2: valid then invalid (the invalid one is the LAST one)
    mock_serial.data_to_read = (valid_obj + invalid_obj).encode('utf-8')
    mock_serial.in_waiting = len(mock_serial.data_to_read)
    time.sleep(0.5)
    
    data = interface.read_and_parse()
    # In current implementation, it might fail because it only takes the LAST valid JSON string
    # but that string might not be a valid ArduinoData object.
    if data and data.device == "Arduino UNO":
         print("Success: Still have valid data even if last object in buffer was invalid schema.")
    else:
         print(f"Failed after invalid trailing: data is {data}")

    interface.disconnect()

if __name__ == "__main__":
    test_validation_error()
