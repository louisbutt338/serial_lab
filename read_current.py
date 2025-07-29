import time
import serial
import threading

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
#open the serial connection
ser.isOpen()

# print the instrument description
def instrument_info():
    ser.write(b'*idn?\r')
    serial_line = ser.readline()
    print(serial_line)

# do zero correction for current readings
def zero_correction():
    ser.write(b'*rst \r')
    ser.write(b'syst:zch on \r ; rang 200e-6  \r ; init \r ')
    ser.write(b'syst:zcor:acq \r ; syst:zcor on \r ; rang:auto on \r ')
    ser.write(b'syst:zch off \r ')

# remote control the keithley and trigger current measurements at time intervals 
def read_data():
    ser.write(b'read? \r')
    serial_line = ser.readline()
    print('current:',serial_line[:41], 'time:',time.ctime())

# zero correct
zero_correction()

# set time interval (s) between each Keithley readings (minimum 1.4s due to legnth of read_data fn)
time_interval = 2
time.sleep(time_interval)

# infinite loop to read the data from the serial port
while True :
        # take measurement and measure time taken
        st = time.time()
        read_data()
        et=time.time()
        loop_time = et-st
        
        # sleep for remainder of set time interval, or nothing
        read_time = et-st
        if time_interval > read_time:
            time.sleep(time_interval-read_time)
        else:
            time.sleep(0)