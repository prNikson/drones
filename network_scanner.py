# https://github.com/dbaldwin/DroneBlocks-TelloEDU-Python/blob/master/network-scan.py
# A basic script to scan a local network for IP addresses to indentify Tello EDU drones

# Import modules
import subprocess
import ipaddress
from subprocess import Popen, PIPE
from multiprocessing.pool import ThreadPool

# Create the network
# The IP below is associated with the TP-Link wireless router
# https://amzn.to/2TR1r56
ip_net = ipaddress.ip_network(u'192.168.0.1/24', strict=False)

def scan(ip):
    # Let's ping the IP to see if it's online
    toping = Popen(['ping', '-n', '1', '-w', '100', ip], stdout=PIPE)
    output = toping.communicate()[0]
    hostalive = toping.returncode
    
    res = hostalive == 0

    if res:
        print(ip)
    # Print whether or not device is online
    return res

if __name__ == '__main__':
    with ThreadPool(32) as p:
        p.map(scan, (str(ip) for ip in ip_net.hosts()))
    input("Done...")

    