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


import struct
import socket, select
import numpy as np

from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz

from astropy.utils.iers import conf
conf.auto_max_age = None

Acre_Road = EarthLocation(lat=55.902483*u.deg, lon=-4.307573*u.deg, height=50*u.m)

open_sockets = []
listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listening_socket.bind( ("", 10002) ) # port number
listening_socket.listen(5)

goto_ra = 0
goto_dec = 0
c = SkyCoord(ra=goto_ra*u.radian, dec=goto_dec*u.radian, frame='icrs')
track = False

while True:
    rlist, wlist, xlist = select.select( [listening_socket] + open_sockets, [], [],1 )
    for i in rlist:
        if i is listening_socket:
            new_socket, addr = listening_socket.accept()
            open_sockets.append(new_socket)
        else:
            data = i.recv(1024)
            if data == "":
                open_sockets.remove(i)
                print ("Connection closed")

            else:
                data = struct.unpack("3iIi", data)
                goto_ra = data[3]*(np.pi/0x80000000)
                goto_dec = data[4]*(np.pi/0x80000000)
                print('from Stellarium: RA = {0:2.3f} Dec = {1:2.3f} radians'.format(goto_ra,goto_dec))
                c = SkyCoord(ra=goto_ra*u.radian, dec=goto_dec*u.radian, frame='icrs')
                time = Time.now()
                c_altaz = c.transform_to(AltAz(obstime=time,location=Acre_Road))
                print("Alt = {0.alt:.5}   Az = {0.az:.5}".format(c_altaz))

                #send current position back to client (here just sets current=target)
                my_ra = goto_ra
                my_dec = goto_dec
                imy_ra = int(my_ra*0x80000000/np.pi)
                imy_dec = int(my_dec*0x80000000/np.pi)
                reply = struct.pack("3iIii", 24, 0, data[2], imy_ra, imy_dec, 0)
                i.send(reply)
                print(reply)
                track = True
    if track:
        time = Time.now()
        c_altaz = c.transform_to(AltAz(obstime=time,location=Acre_Road))
        print("Alt = {0.alt:.5}   Az = {0.az:.5}".format(c_altaz)) 
        my_ra = goto_ra
        my_dec = goto_dec
        imy_ra = int(my_ra*0x80000000/np.pi)
        imy_dec = int(my_dec*0x80000000/np.pi)
        reply = struct.pack("3iIii", 24, 0, data[2], imy_ra, imy_dec, 0)
        i.send(reply)