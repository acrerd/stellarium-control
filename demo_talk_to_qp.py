#simple test of controlling QP (https://bitbucket.org/nxg/qp/src/default/ or  http://www.astro.gla.ac.uk/users/norman/distrib/qp/doc/index.html) from python
import serial
import numpy as np

#Acre Road Obeservatory
lat = 55.9024278/180*np.pi
lon = -4.307582/180*np.pi

# Home position
oaz = (38.0-16.0)/180*np.pi
oalt = 3.0/180*np.pi

# Example slew-to position
az =  130.0/180*np.pi
alt = 22.0/180*np.pi

def send(s):
    with  serial.Serial('/dev/ttyACM0',19200, timeout=1) as ser:
       ser.write(s+'\n')
    return
 
 
    
#send('gH')
#send('O'  + ' %.5f' % lat + ' %.5f' % lon + ' 0.0 0.0 '+' %.5f' % oaz +' %.5f' % oalt + ' 6.0')
send('gh' + ' %.5f' % az +' %.5f' % alt ) 

## to listen:
#with  serial.Serial('/dev/ttyACM0',19200, timeout=1) as ser:
#    while True:
#        line = ser.readline()
#        if line!='':
#          print line
