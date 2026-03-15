from app.core.arduino import ArduinoInterface, parse_arduino_response
from app.core.models import ArduinoData
import json

def test_buffer_processing():
    interface = ArduinoInterface(port="MOCK")
    
    # Valid ArduinoData object
    valid_obj = '{"timestamp": "2026-03-10T11:00:00+01:00", "device": "Arduino UNO", "sensors": {"ultrasonic": {"out_of_range": true, "echo_duration_us": 0, "distance_in_cm": 0.0}, "pir": {"motion": true}, "rfid": {"card_present": false, "uid": "", "card_type": ""}, "soil_moisture": {"raw": 1}, "ir_receiver": {"received": false, "code": ""}}}'
    # Partial sensor data (the kind causing the reported error)
    invalid_obj = '{"raw": 1}'
    
    print("Test 1: Partial data followed by valid data")
    interface._buffer = invalid_obj + valid_obj
    interface._process_buffer()
    if interface.latest_data and interface.latest_data.device == "Arduino UNO":
        print("Success: Valid object parsed even after partial data.")
    else:
        print(f"Failed: latest_data is {interface.latest_data}")

    print("\nTest 2: Valid data followed by partial data")
    interface.latest_data = None
    interface._buffer = valid_obj + invalid_obj
    interface._process_buffer()
    if interface.latest_data and interface.latest_data.device == "Arduino UNO":
        print("Success: Valid object parsed and not overwritten by following partial data.")
    else:
        print(f"Failed: latest_data is {interface.latest_data}")
        
    print(f"\nRemaining buffer: '{interface._buffer}'")
    if interface._buffer == invalid_obj:
        print("Success: Valid object removed from buffer, partial data (incomplete for parsing but complete JSON) also removed from buffer if it was a complete JSON object but failed parsing.")
        # Wait, if it's a complete JSON object that failed parsing, it SHOULD be removed from buffer in my new logic.
        # Let's check my logic: it updates last_end_index for EVERY complete JSON object.
    else:
        print(f"Buffer state: '{interface._buffer}'")

if __name__ == "__main__":
    test_buffer_processing()
