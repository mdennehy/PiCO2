#!/usr/bin/python

# Original framework taken from https://www.circuits.dk/testing-mh-z19-ndir-co2-sensor-module/
# That code didn't work at all for me, so made several changes to get it to run
# on my Pi Zero W

import serial
import os, time, sys, datetime, csv

#Function to calculate MH-Z19 crc according to datasheet
def crc8(a):
    crc=0x00
    count=1
    b=bytearray(a)
    while count<8:
        crc+=b[count]
        count=count+1
    #Truncate to 8 bit
    crc%=256
    #Invert number with xor
    crc=~crc&0xFF
    crc+=1
    return crc

# try to open serial port
port='/dev/serial0'
sys.stderr.write('Trying port %s\n' % port)

try:
    # try to read a line of data from the serial port and parse
    with serial.Serial(port, 9600, xonxoff=True, timeout=2.0) as ser:
        # 'warm up' with reading one input
        result=ser.write('\xff\x01\x86\x00\x00\x00\x00\x00\x79')
        time.sleep(0.1)
        s=ser.read(9)
        z=bytearray(s)
        # Calculate crc
        crc=crc8(s)
        if crc != z[8]:
            sys.stderr.write('CRC error calculated %d bytes= %d:%d:%d:%d:%d:%d:%d:%d crc= %d\n' % (crc, z[0],z[1],z[2],z[3],z[4],z[5],z[6],z[7],z[8]))
        else:
            sys.stderr.write('Data: %d:%d:%d:%d:%d:%d:%d:%d\n' % (z[0],z[1],z[2],z[3],z[4],z[5],z[6],z[7]))

        # loop will exit with Ctrl-C, which raises a KeyboardInterrupt
        while True:
            #Send "read value" command to MH-Z19 sensor
            result=ser.write('\xff\x01\x86\x00\x00\x00\x00\x00\x79')
            time.sleep(0.1)
            s=ser.read(9)
            z=bytearray(s)
            crc=crc8(s)
            #Calculate crc
            if crc != z[8]:
                sys.stderr.write('CRC error calculated %d bytes= %d:%d:%d:%d:%d:%d:%d:%d crc= %d\n' % (crc, z[0],z[1],z[2],z[3],z[4],z[5],z[6],z[7],z[8]))
            else:
                if s[0] == "xff" and s[1] == "x86":
                    print "co2=", ord(s[2])*256 + ord(s[3]) 
            co2value=ord(s[2])*256 + ord(s[3])
            now=time.ctime()
            parsed=time.strptime(now)
            lgtime=time.strftime("%Y %m %d %H:%M:%S")
            row=[lgtime,co2value]
            print row
            #Sample every minute
            time.sleep(60)
except Exception as e:
    sys.stderr.write('Error reading serial port %s: %s\n' % (type(e).__name__, e))
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    print 'EXCEPTION IN ({}, LINE {}): {}'.format(filename, lineno, exc_obj)

except KeyboardInterrupt as e:
    sys.stderr.write('Ctrl+C pressed, exiting log of %s to %s\n' % (port, outfname))
