import time
import serial

def zero_correction():
    """ set keithley settings and do zero correction for current readings
    """
    ser.write(b'*rst \r')
    ser.write(b'syst:zch on \r ; rang 200e-6  \r ; init \r ')
    ser.write(b'syst:zcor:acq \r ; syst:zcor on \r ; rang:auto on \r ')
    ser.write(b'syst:zch off \r ')
    print('zero correction complete')

def read_data(total_st):
    """ remote control the keithley and trigger current measurements
    at time intervals from start time
    """
    # take measurement
    ser.write(b'read? \r')
    serial_line = ser.read_until()
    # decode values
    current_reading = serial_line[:13].decode()
    #time_reading = serial_line[15:28].decode()
    time_reading = str(time.time() - total_st)
    try:
        print('current(A):',float(current_reading),
              'time(s):',   time_reading)
        return current_reading,time_reading
    except ValueError:
        print('current(A):','N/A',
               'time(s):', time_reading)
        return 'N/A',time_reading

def dump_data(current,time,outfile):
    """ Dump current and time data into txt file

    Parameters
    ----------
    current : str
        current str from reading
    time : str
        time str from reading
    outfile : str
        full output file name i.e. output.txt
    """
    with open(outfile,'a') as file:
        file.writelines([current,' ',time,'\n'])

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

# set output file and clear of all data
output_file = 'output.txt'
open(output_file,'w').close

# set time interval (s) between each Keithley readings (minimum 1.4s due to legnth of read_data fn)
time_interval = 2
total_start_time = time.time()
print(f'start time for measurements: {time.ctime(total_start_time)}')

# header on output data file
with open(output_file,'a') as file:
    file.writelines(f'start time for measurements: {time.ctime(total_start_time)}\n')
    file.writelines(['current(A)',' ', 'time(s)\n'])

# zero correction and first reading
zero_correction()
c,t = read_data(total_start_time)
dump_data(c,t,output_file)

# infinite loop to read the data from the serial port
while True :
        
        # take reading and dump data with time measurements either side
        measure_st = time.time()
        c,t = read_data(total_start_time)
        dump_data(c,t,output_file)
        measure_et = time.time()

        # sleep the code for remaining time in time_interval
        sleep_time(measure_st,measure_et,time_interval)