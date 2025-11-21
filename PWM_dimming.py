import serial
import time

PORT = "COM3" 
BAUD = 115200

HEADER = 0xAA
ADDRESS = 0x52
CMD_GREEN = 0x02
LENGTH = 2
PWM_MAX = 60000

def checksum(b):
    cs = 0
    for x in b:
        cs ^= x
    return cs & 0xFF

def send_pwm(ser, value):
    if value < 0: value = 0
    if value > PWM_MAX: value = PWM_MAX
    high = (value >> 8) & 0xFF
    low  = value & 0xFF
    pkt = bytearray([HEADER, ADDRESS, CMD_GREEN, LENGTH, high, low])
    pkt.append(checksum(pkt))
    ser.write(pkt)
    #print("Sent:", " ".join(f"{x:02X}" for x in pkt))

if __name__ == "__main__":
    ser = serial.Serial(PORT, BAUD, timeout=0.5)
    try:
        # quick demo: ramp up and down
        for v in range(0, PWM_MAX + 1, 6000):
            send_pwm(ser, v)
            time.sleep(0.5)
        for v in range(PWM_MAX, -1, -6000):
            send_pwm(ser, v)
            time.sleep(0.5)
    finally:
        ser.close()