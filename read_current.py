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

def read_data():
    """ remote control the keithley and trigger current measurements at time intervals
    """
    # take measurement
    ser.write(b'read? \r')
    serial_line = ser.readline()
    # decode values
    current_reading = float(serial_line[:13].decode())
    time_reading = float(serial_line[15:28].decode())
    print('current(A):',current_reading,
          'time(s):',time_reading)

    return current_reading,time_reading

def dump_data(current,time):
    """ Dump current and time data into txt file

    Parameters
    ----------
    current : str
        current str from reading
    time : str
        time str from reading
    """
    output_filepath = 'output.txt'
    with open(output_filepath,'w') as file:
        file.writelines(['current(A)', 'time(s)\n'])
        file.writelines([current,time,'\n'])

def sleep_time(start_time,end_time,time_int):
    """ Get code to sleep for appropriate time 
    depending on the time interval set

    Parameters
    ----------
    start_time : time
        start time before the measurement
    end_time : time
        end time after the measurement
    time_int : time
        interval time desired between measurements
    """
    measurement_time = end_time - start_time
    # sleep for remainder of set time interval, or nothing
    if time_int > measurement_time:
        time.sleep(time_int-measurement_time)
    else:
        time.sleep(0)


# zero correct
zero_correction()

# set time interval (s) between each Keithley readings (minimum 1.4s due to legnth of read_data fn)
time_interval = 2
total_start_time = time.ctime()
print(f'start time for first reading: {total_start_time}')

# infinite loop to read the data from the serial port
while True :
        
        # take reading and dump data with time measurements either side
        measure_st = time.time()
        c,t = read_data(time_interval)
        dump_data(c,t)
        measure_et = time.time()

        # sleep the code for remaining time in time_interval
        sleep_time(measure_st,measure_et,time_interval)