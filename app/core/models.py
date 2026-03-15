from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime

class UltrasonicDistance(BaseModel):
    out_of_range: bool
    echo_duration_us: int
    distance_in_cm: float

class MotionDetection(BaseModel):
    motion: bool

class RFIDReader(BaseModel):
    card_present: bool
    uid: str
    card_type: str

class SoilMoisture(BaseModel):
    raw: int

class IRReceiver(BaseModel):
    received: bool
    code: str

class Sensors(BaseModel):
    ultrasonic: UltrasonicDistance
    pir: MotionDetection
    rfid: RFIDReader
    soil_moisture: SoilMoisture
    ir_receiver: IRReceiver

class ArduinoData(BaseModel):
    device: str
    timestamp: datetime
    sensors: Sensors
