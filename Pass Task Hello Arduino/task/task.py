import serial
import random
import time

# set baud rate, same speed as set in your Arduino sketch.
boud_rate = 9600

# set serial port as suits your operating system
s = serial.Serial('COM4', boud_rate, timeout=10)

while True:  # infinite loop, keep running

    #  a random number between 1 and 6.
    data_send = random.randint(1, 6)

    # Write in serial port to send to arduino
    d1 = s.write(bytes(str(data_send), 'utf-8'))
    print(f"Send >>> {data_send} ({d1} bytes)")

    # Read from serial port that arduino sends
    for _ in range(10): # retry 10 times
        d2 = s.readline().decode("utf-8").strip()
        if d2:
            print(f"Recv <<< {d2}")
            try:
                # Sleep based on the number arduino sends
                sleep_time = int(d2)
                print(f"Sleep for {sleep_time}s")
                time.sleep(sleep_time)
                break # exit the loop
            except ValueError:
                print(d2)