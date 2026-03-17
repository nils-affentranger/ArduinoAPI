import serial
import json
import logging
import threading
import time
import random
from datetime import datetime
from typing import Optional
from app.core.models import ArduinoData, Sensors, UltrasonicDistance, MotionDetection, RFIDReader, SoilMoisture, IRReceiver

# Configure logger
logger = logging.getLogger(__name__)

class ArduinoInterface:
    def __init__(self, port: str | list[str], baud: int = 21000, timeout: float = 1.0):
        self.ports = [port] if isinstance(port, str) else port
        self.current_port: Optional[str] = None
        self.baud = baud
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        self.latest_data: Optional[ArduinoData] = None
        self._stop_event = threading.Event()
        self._monitor_thread: Optional[threading.Thread] = None
        self._buffer = ""

    def connect(self):
        """Establish a connection to the Arduino, trying multiple ports if provided."""
        if self.serial and self.serial.is_open:
            return self.serial

        for port in self.ports:
            try:
                self.serial = serial.Serial(
                    port=port,
                    baudrate=self.baud,
                    timeout=self.timeout
                )
                self.current_port = port
                logger.info(f"Connected to Arduino on {port}")
                self.start_monitoring()
                return self.serial
            except Exception as e:
                logger.warning(f"Failed to connect to Arduino on {port}: {e}")

        logger.error(f"Failed to connect to any of the ports: {self.ports}")
        raise serial.SerialException(f"Could not connect to any of the ports: {self.ports}")

    def disconnect(self):
        """Close the serial connection."""
        self.stop_monitoring()
        if self.serial and self.serial.is_open:
            self.serial.close()
            logger.info(f"Disconnected from Arduino on {self.current_port}")

    def start_monitoring(self):
        """Start a background thread to monitor the serial port."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Started Arduino monitoring thread.")

    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
            logger.info("Stopped Arduino monitoring thread.")

    def _monitor_loop(self):
        """Continuously read from serial and update latest_data."""
        while not self._stop_event.is_set():
            if self.serial and self.serial.is_open:
                try:
                    # Read available bytes
                    if self.serial.in_waiting > 0:
                        chunk = self.serial.read(self.serial.in_waiting).decode('utf-8', errors='ignore')
                        self._buffer += chunk
                        self._process_buffer()
                    else:
                        time.sleep(0.1)
                except Exception as e:
                    logger.error(f"Error in monitor loop: {e}")
                    time.sleep(1.0)
            else:
                time.sleep(1.0)

    def _process_buffer(self):
        """Extract and parse all complete JSON objects from the buffer, updating latest_data with valid ArduinoData objects."""
        last_valid_data = None
        last_end_index = -1

        # Search for all complete JSON objects in the buffer
        search_index = 0
        while "{" in self._buffer[search_index:] and "}" in self._buffer[search_index:]:
            start_index = self._buffer.find("{", search_index)
            bracket_count = 0
            end_index = -1
            for i in range(start_index, len(self._buffer)):
                if self._buffer[i] == "{":
                    bracket_count += 1
                elif self._buffer[i] == "}":
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_index = i
                        break
            
            if end_index != -1:
                json_str = self._buffer[start_index:end_index+1]
                last_end_index = end_index
                # Move search_index forward to find the next possible object
                search_index = end_index + 1
                
                try:
                    data = parse_arduino_response(json_str)
                    last_valid_data = data
                except Exception as e:
                    # Log error if it's NOT a validation error (e.g. invalid JSON), 
                    # but keep it quiet if it's just a schema mismatch (part of normal data flow).
                    # Actually, for debugging it might be good to log, but let's keep it clean.
                    logger.debug(f"Failed to parse JSON into ArduinoData: {e}")
            else:
                # Incomplete JSON at the end of buffer
                break

        if last_valid_data:
            self.latest_data = last_valid_data
            logger.debug(f"Updated latest Arduino data: {self.latest_data.device}")

        if last_end_index != -1:
            # Discard everything up to and including the last processed object
            self._buffer = self._buffer[last_end_index+1:]

    def read_and_parse(self) -> Optional[ArduinoData]:
        """Return the latest parsed ArduinoData object."""
        return self.latest_data

class MockArduinoInterface(ArduinoInterface):
    def __init__(self, port: str | list[str] = "MOCK", baud: int = 9600, timeout: float = 1.0):
        super().__init__(port, baud, timeout)
        self.current_port = "MOCK"

    def connect(self):
        """Simulate connecting to a mock Arduino."""
        logger.info("Connected to Mock Arduino")
        self.start_monitoring()
        return None

    def disconnect(self):
        """Simulate disconnecting from a mock Arduino."""
        self.stop_monitoring()
        logger.info("Disconnected from Mock Arduino")

    def _monitor_loop(self):
        """Continuously generate mock data and update latest_data."""
        while not self._stop_event.is_set():
            try:
                # Generate realistic mock data
                mock_data = ArduinoData(
                    device="MockArduinoUno",
                    timestamp=datetime.now(),
                    sensors=Sensors(
                        ultrasonic=UltrasonicDistance(
                            out_of_range=random.choice([True, False]),
                            echo_duration_us=random.randint(500, 30000),
                            distance_in_cm=round(random.uniform(2.0, 400.0), 2)
                        ),
                        pir=MotionDetection(
                            motion=random.choice([True, False])
                        ),
                        rfid=RFIDReader(
                            card_present=random.choice([True, False]),
                            uid=f"{random.randint(100, 999)}:{random.randint(100, 999)}:{random.randint(100, 999)}:{random.randint(100, 999)}",
                            card_type="Mifare"
                        ),
                        soil_moisture=SoilMoisture(
                            raw=random.randint(300, 800)
                        ),
                        ir_receiver=IRReceiver(
                            received=random.choice([True, False]),
                            code=hex(random.getrandbits(32))
                        )
                    )
                )
                self.latest_data = mock_data
                logger.debug(f"Updated mock Arduino data: {self.latest_data.device}")
                time.sleep(1.0)  # Update every second
            except Exception as e:
                logger.error(f"Error in mock monitor loop: {e}")
                time.sleep(1.0)

def parse_arduino_response(json_str: str) -> ArduinoData:
    """Parse the Arduino JSON response into an ArduinoData object."""
    data = json.loads(json_str)
    return ArduinoData(**data)
