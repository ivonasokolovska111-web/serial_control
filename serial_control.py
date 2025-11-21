import serial
import time
from typing import List

class SerialController:
    START_BYTE = 0xAA
    
    def __init__(self, port: str, baudrate: int = 115200):
        """Initialize serial communication."""
        self.serial = serial.Serial(port=port, 
                                  baudrate=baudrate,
                                  bytesize=serial.EIGHTBITS,
                                  parity=serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE)
        
    def calculate_checksum(self, data: List[int]) -> int:
        """Calculate XOR checksum of the data."""
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum
    
    def send_command(self, address: int, command: int, data: List[int]) -> bool:
        """
        Send command to the microcontroller.
        
        Args:
            address: Target address byte
            command: Command byte (0x01 or 0x02)
            data: List of data bytes to send
        
        Returns:
            bool: True if command was sent successfully
        """
        if command not in [0x01, 0x02]:
            print("Error: Invalid command. Use 0x01 or 0x02")
            return False
            
        # Prepare packet
        packet = [
            self.START_BYTE,    # Start byte
            address,            # Address byte
            command,            # Command byte
            len(data),         # Data length
        ]
        packet.extend(data)    # Data field
        
        # Calculate and append checksum
        checksum = self.calculate_checksum(packet)
        packet.append(checksum)
        
        try:
            # Send the packet
            self.serial.write(bytes(packet))
            print(f"Sent packet: {[hex(b) for b in packet]}")
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def close(self):
        """Close the serial connection."""
        if self.serial.is_open:
            self.serial.close()

def main():
    # Replace 'COM3' with your actual serial port
    PORT = 'COM3'
    controller = None
    
    try:
        controller = SerialController(PORT)
        print(f"Connected to {PORT}")
        
        while True:
            print("\nAvailable commands:")
            print("1. Send Command 0x01")
            print("2. Send Command 0x02")
            print("3. Exit")
            
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == '3':
                break
                
            if choice not in ['1', '2']:
                print("Invalid choice. Please try again.")
                continue
                
            # Get address
            try:
                address = int(input("Enter address (0-255): "), 0)
                if not 0 <= address <= 255:
                    print("Address must be between 0 and 255")
                    continue
            except ValueError:
                print("Invalid address format")
                continue
                
            # Get data
            try:
                data_str = input("Enter data bytes (space-separated hex values, e.g., '0A 1B 2C'): ").strip()
                if data_str:
                    data = [int(x, 16) for x in data_str.split()]
                    if not all(0 <= x <= 255 for x in data):
                        print("All data bytes must be between 0 and 255")
                        continue
                else:
                    data = []
            except ValueError:
                print("Invalid data format")
                continue
            
            # Send command
            command = 0x01 if choice == '1' else 0x02
            controller.send_command(address, command, data)
            
    except serial.SerialException as e:
        print(f"Error: Could not open port {PORT}. {e}")
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        if controller:
            controller.close()
            print("Serial connection closed")

if __name__ == "__main__":
    main()