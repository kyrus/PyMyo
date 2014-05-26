
###############################################################################
## File       :  ipv6.py
## Description:  Module for looking up IPv6 address of host
##            :  
## Created_On :  Tue Sep 25 18:40:46 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Tue Jan 29 16:54:23 2013
## Modified_By:  Rich Smith (rich@kyr.us)
## License    :  BSD-3
##
##
###############################################################################
import socket
from libs import utils

__author__  = "rich@kyr.us"
__version__ = 1.0
__updated__ = "26/09/2012"
__help__    = "Module for looking up IPv6 address of host"
__alias__   = ["ip6"]

def Command(pymyo, name, *args):
    """
    Get IPV6 addresses of the host
    """
    try:
        data = socket.getaddrinfo(args[0], 80)

        ipv6 = []
        for row in data:
            ip = row[4][0]
            if ":" in ip:
                ipv6.append(ip)
             
        ipv6 = list(set(ipv6))
        
        for x in ipv6:
            pymyo.output(x)
            
    except:
        pymyo.error("Error looking up ipv6 address")
