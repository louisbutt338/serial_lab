/*
serial_posix.cpp copied from https://www.geeksforgeeks.org/cpp/serial-port-connection-in-cpp/
This code is contributed by Susobhan Akhuli
*/
#include <cstring>
#include <errno.h>
#include <fcntl.h>
#include <iostream>
#include <termios.h>
#include <unistd.h>
using namespace std;

// Function to open the serial port
int openSerialPort(const char* portname)
{
    int fd = open(portname, O_RDWR | O_NOCTTY | O_SYNC);
    if (fd < 0) {
        cerr << "Error opening " << portname << ": "
             << strerror(errno) << endl;
        return -1;
    }
    return fd;
}

// Function to configure the serial port
bool configureSerialPort(int fd, int speed)
{
    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        cerr << "Error from tcgetattr: " << strerror(errno)
             << endl;
        return false;
    }

    cfsetospeed(&tty, speed);
    cfsetispeed(&tty, speed);

    tty.c_cflag
        = (tty.c_cflag & ~CSIZE) | CS8; // 8-bit characters
    tty.c_iflag &= ~IGNBRK; // disable break processing
    tty.c_lflag = 0; // no signaling chars, no echo, no
                     // canonical processing
    tty.c_oflag = 0; // no remapping, no delays
    tty.c_cc[VMIN] = 0; // read doesn't block
    tty.c_cc[VTIME] = 5; // 0.5 seconds read timeout

    tty.c_iflag &= ~(IXON | IXOFF
                     | IXANY); // shut off xon/xoff ctrl

    tty.c_cflag
        |= (CLOCAL | CREAD); // ignore modem controls,
                             // enable reading
    tty.c_cflag &= ~(PARENB | PARODD); // shut off parity
    tty.c_cflag &= ~CSTOPB;
    tty.c_cflag &= ~CRTSCTS;

    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        cerr << "Error from tcsetattr: " << strerror(errno)
             << endl;
        return false;
    }
    return true;
}

// Function to read data from the serial port
int readFromSerialPort(int fd, char* buffer, size_t size)
{
    return read(fd, buffer, size);
}

// Function to write data to the serial port
int writeToSerialPort(int fd, const char* buffer,
                      size_t size)
{
    return write(fd, buffer, size);
}

// Function to close the serial port
void closeSerialPort(int fd) { close(fd); }

// set keithley settings and do zero correction for current readings
void doZeroCorrection(int fd)
{
    // declare strings for the keithley
    const char* zc1 = "*rst \r";
    const char* zc2 = "syst:zch on \r ; rang 200e-6  \r ; init \r";
    const char* zc3 = "syst:zcor:acq \r ; syst:zcor on \r ; rang:auto on \r ";
    const char* zc4 = "syst:zch off \r ";

    // write commands to the keithley
    writeToSerialPort(fd,zc1, strlen(zc1));
    writeToSerialPort(fd,zc2, strlen(zc2));
    writeToSerialPort(fd,zc3, strlen(zc3));
    writeToSerialPort(fd,zc4, strlen(zc4));
    cerr << "zero correction complete " << endl;
}

// remote control the keithley and trigger current measurements
void readData(int fd)
{
    // take measurement
    const char* read = "read? \r";
    writeToSerialPort(fd,read, strlen(read));

    // decode values
    //current_reading = serial_line[:13].decode()
    //time_reading = serial_line[15:28].decode()
    //try:
    //    print('current(A):',float(current_reading),
    //          'time(s):',   time_reading)
    //    return current_reading,time_reading
    // except ValueError:
    //     print('current(A):','N/A',
    //            'time(s):', time_reading)
    //     return 'N/A',time_reading
}

int main()
{
    // Replace with your serial port name
    const char* portname = "/dev/cu.usbserial-110";
    int fd = openSerialPort(portname);
    if (fd < 0)
        return 1;

    if (!configureSerialPort(fd, B9600)) {
        closeSerialPort(fd);
        return 1;
    }

    const char* message = "Hello, Serial Port!";
    if (writeToSerialPort(fd, message, strlen(message))
        < 0) {
        cerr << "Error writing to serial port: "
             << strerror(errno) << endl;
    }
    else {
        //writeToSerialPort(fd, message, strlen(message));
        doZeroCorrection(fd);
    }

    while(true) {
        readData(fd);
        char buffer[100];
        int n = readFromSerialPort(fd, buffer, sizeof(buffer));
        if (n < 0) {
            cerr << "Error reading from serial port: "
                 << strerror(errno) << endl;
        }
        else {
            cout << "Read from serial port: "
                 << std::string(buffer, n) << endl;
        }
    }

    closeSerialPort(fd);
    return 0;
}