import logging
import time
import argparse
from app.core.arduino import ArduinoInterface

# Basic logging configuration for CLI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("arduino-cli")

def main():
    parser = argparse.ArgumentParser(description="Arduino Serial Monitor CLI")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port (default: /dev/ttyACM0)")
    parser.add_argument("--baud", type=int, default=9600, help="Baud rate (default: 9600)")
    parser.add_argument("--interval", type=float, default=1.0, help="Read interval in seconds (default: 1.0)")
    
    args = parser.parse_args()
    
    interface = ArduinoInterface(port=args.port, baud=args.baud)
    
    logger.info(f"Starting Arduino CLI monitor on {args.port} at {args.baud} baud...")
    
    try:
        interface.connect()
        while True:
            data = interface.read_and_parse()
            if data:
                # The ArduinoInterface already logs the state at INFO level
                pass
            else:
                logger.debug("No data received in this cycle.")
            
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logger.info("CLI monitor stopped by user.")
    except Exception as e:
        logger.error(f"Error in CLI monitor: {e}")
    finally:
        interface.disconnect()

if __name__ == "__main__":
    main()
