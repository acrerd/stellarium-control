
#Talking to Stellarium through a tcp socket.
#Install telescope control on Stellarium
#In config, choose:
#    telescope controlled by external software
#    name: SRT
#    connection delay 1 s
#    host: localhost
#    port: 10002
#    field of view 3
#
#this code stops (not prettily) when stellarium disconnects
#

from __future__ import print_function

import struct
import socket, select
import numpy as np
import serial


from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz

#from astropy.utils.iers import conf
#conf.auto_max_age = None

ser = serial.Serial('/dev/ttyACM1',19200, timeout=1)

def send(s):
    ser.write(s+'\n')
    print("to qp: " + s)
    return


#Acre Road Obeservatory
acre_lat = 55.9024278*u.degree
acre_lon = -4.307582/180*u.degree

Acre_Road = EarthLocation(lat=acre_lat.to(u.radian), lon=acre_lon.to(u.radian), height=50*u.m)
# Home position
oaz = 22.0*u.degree
oalt = 3.0*u.degree

#initialise

send('O'  + ' %.5f' % acre_lat.to(u.radian).value + ' %.5f' % acre_lon.to(u.radian).value + ' 0.0 0.0 '+' %.5f' % oaz.to(u.radian).value +' %.5f' % oalt.to(u.radian).value + ' 6.0')
send('gH')
home = False

while not home:
     line = ser.readline()
     if  line.split(' ')[0] == '#home:':
          home = True
     print("from qp: "+line)

open_sockets = []
listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listening_socket.bind( ("", 10002) ) # port number
listening_socket.listen(5)

time = Time.now()
home_pos = AltAz(oalt,oaz,obstime=time,location=Acre_Road)
goto_ra = SkyCoord(home_pos).icrs.ra
goto_dec = SkyCoord(home_pos).icrs.dec
c = SkyCoord(ra=goto_ra.to(u.radian), dec=goto_dec.to(u.radian), frame='icrs')
track = False

while True:
    rlist, wlist, xlist = select.select( [listening_socket] + open_sockets, [], [],1 ) # get any goto data from stellarium, 1 sec timeout
    for i in rlist:
        if i is listening_socket:
            new_socket, addr = listening_socket.accept()
            open_sockets.append(new_socket)
        else:
            data = i.recv(1024)
            if data == "":
                open_sockets.remove(i)
                print ("Connection closed")

            else: # we have goto data from stellarium...
                data = struct.unpack("3iIi", data)
                goto_ra = data[3]*(np.pi/0x80000000)
                goto_dec = data[4]*(np.pi/0x80000000)
                print('from Stellarium: RA = {0:2.3f} Dec = {1:2.3f} radians'.format(goto_ra,goto_dec))
                c = SkyCoord(ra=goto_ra*u.radian, dec=goto_dec*u.radian, frame='icrs')
                track = True
    if track:
        time = Time.now()
        c_altaz = c.transform_to(AltAz(obstime=time,location=Acre_Road))
   #     print("Alt = {0.alt:.5}   Az = {0.az:.5}".format(c_altaz))
        send('gh'  + ' %.5f' % c_altaz.az.to(u.radian).value + ' %.5f' % c_altaz.alt.to(u.radian).value)

# see that qp has to say for itself
        for line in ser.readlines():
             print("from qp: "+line)

# send cursor data back to stellarium
        my_ra = goto_ra
        my_dec = goto_dec
        imy_ra = int(my_ra*0x80000000/np.pi)
        imy_dec = int(my_dec*0x80000000/np.pi)
        reply = struct.pack("3iIii", 24, 0, data[2], imy_ra, imy_dec, 0)
        i.send(reply)

