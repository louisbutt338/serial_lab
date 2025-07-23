import time
import serial

# configure the serial connections (the parameters differ on the device you are connecting to)
try:
    ser = serial.Serial(
        port='/dev/cu.usbserial-110',
        baudrate=9600,
        timeout=1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
# exception if there is no port of that name available 
except OSError:
      print("Error connecting device")
      exit()
ser.isOpen()

# print the instrument description
#ser.write(b'*idn?\r')
#serial_line = ser.readline()
#print(serial_line)

# do zero correction for current readings
ser.write(b'*rst \r')
ser.write(b'syst:zch on \r ; rang 2e-9  \r ; init \r ')
ser.write(b'syst:zcor:acq \r ; syst:zcor on \r ; rang:auto on \r ')
ser.write(b'syst:zch off \r ')

# Reading the data from the serial port. This will be running in an infinite loop.
while True :
        st = time.time()
        # remote control the keithley and trigger zero-corr current measurements at time intervals 
        ser.write(b'read? \r')
        serial_line = ser.readline()
        print('current:',serial_line[:-1], 'time:',time.ctime())
        et=time.time()
        loop_time = et-st
        # time for program to run is ~1.38s. sleep for remainder of set time interval
        time.sleep(2-loop_time)

        # for reading and printing the bytes in waiting
        #bytesToRead = ser.in_waiting
        #data = ser.read(bytesToRead)
        #print(data)