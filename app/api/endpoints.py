from fastapi import APIRouter, HTTPException, Depends
from app.core.arduino import ArduinoInterface
from app.core.models import ArduinoData, UltrasonicDistance, MotionDetection, RFIDReader, SoilMoisture, IRReceiver
from typing import Optional

router = APIRouter()


# Global variable for the Arduino interface (simplest way to persist connection)
# In a production app, you might use a dependency injection or a startup event.
# On start, when ACM0 is not available, test for ACM2 and ACM3
arduino = ArduinoInterface(port=["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3"], baud=9600)

def get_arduino():
    """Dependency that ensures the Arduino is connected."""
    try:
        arduino.connect()
        return arduino
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Arduino not connected: {e}")

@router.get("/", response_model=ArduinoData)
async def get_arduino_data(interface: ArduinoInterface = Depends(get_arduino)):
    """Endpoint to return the last complete JSON response from the Arduino."""
    data = interface.read_and_parse()
    if not data:
        raise HTTPException(status_code=404, detail="No data received from Arduino yet.")
    return data

@router.get("/ultrasonic", response_model=UltrasonicDistance)
async def get_ultrasonic_distance(interface: ArduinoInterface = Depends(get_arduino)):
    """Retrieve the latest ultrasonic distance state."""
    data = interface.read_and_parse()
    if not data:
        raise HTTPException(status_code=404, detail="No data received from Arduino yet.")
    return data.sensors.ultrasonic

@router.get("/motion", response_model=MotionDetection)
async def get_motion_detection(interface: ArduinoInterface = Depends(get_arduino)):
    """Retrieve the latest motion detection state."""
    data = interface.read_and_parse()
    if not data:
        raise HTTPException(status_code=404, detail="No data received from Arduino yet.")
    return data.sensors.pir

@router.get("/rfid", response_model=RFIDReader)
async def get_rfid_reader(interface: ArduinoInterface = Depends(get_arduino)):
    """Retrieve the latest RFID reader state."""
    data = interface.read_and_parse()
    if not data:
        raise HTTPException(status_code=404, detail="No data received from Arduino yet.")
    return data.sensors.rfid

@router.get("/soil-moisture", response_model=SoilMoisture)
async def get_soil_moisture(interface: ArduinoInterface = Depends(get_arduino)):
    """Retrieve the latest soil moisture state."""
    data = interface.read_and_parse()
    if not data:
        raise HTTPException(status_code=404, detail="No data received from Arduino yet.")
    return data.sensors.soil_moisture

@router.get("/ir-receiver", response_model=IRReceiver)
async def get_ir_receiver(interface: ArduinoInterface = Depends(get_arduino)):
    """Retrieve the latest IR receiver state."""
    data = interface.read_and_parse()
    if not data:
        raise HTTPException(status_code=404, detail="No data received from Arduino yet.")
    return data.sensors.ir_receiver
