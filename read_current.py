import time
import serial
import struct

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


def instrument_info():
    """ print the instrument description
    """
    ser.write(b'*idn?\r')
    serial_line = ser.readline()
    print(serial_line)

def zero_correction():
    """ do zero correction for current readings
    """
    ser.write(b'*rst \r')
    ser.write(b'syst:zch on \r ; rang 200e-6  \r ; init \r ')
    ser.write(b'syst:zcor:acq \r ; syst:zcor on \r ; rang:auto on \r ')
    ser.write(b'syst:zch off \r ')
    ser.write(b'read? \r')
    ser.readline()
    print('zero correction complete')

 
def read_data(time_int):
    """ remote control the keithley and trigger current measurements at time intervals

    Parameters
    ----------
    time_int : float
        set time interval (s) between readings
    """
    # take measurement and measure total time taken
    measure_st = time.time()
    ser.write(b'read? \r')
    serial_line = ser.readline()
    print('current(A):',float(serial_line[:13].decode()),
          'time(s):',float(serial_line[15:28].decode()))
    measure_et = time.time()
    measure_tt = measure_et - measure_st

    # sleep for remainder of set time interval, or nothing
    if time_int > measure_tt:
        time.sleep(time_int-measure_tt)
    else:
        time.sleep(0)

def parse_txt():
    """ Parse txt data into two arrays
    """
    input_filepath = 'output.txt'
    with open(input_filepath,'w') as txt_data_file:
        txt_contents = txt_data_file.readlines()
        time = []
        countrate = []
        for line in txt_contents:
            time.append(float(line.split()[0]))
            countrate.append(float(line.split()[1]))
    return time,countrate


# zero correct
zero_correction()

# set time interval (s) between each Keithley readings (minimum 1.4s due to legnth of read_data fn)
time_interval = 2
total_start_time = time.ctime()
print(f'start time for first reading: {total_start_time}')

# infinite loop to read the data from the serial port
while True :
        read_data(time_interval)