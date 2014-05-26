
###############################################################################
## File       :  ipv4.py
## Description:  Return ipv4 lookup data for a host
##            :  
## Created_On :  Tue Sep 25 17:21:36 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Tue Jan 29 16:59:22 2013
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
__help__    = "Module for looking up IPv4 address of host"
__alias__   = ["ip4"]

def Command(pymyo, name, *args):
    """
    Get the IPv4 address of the host
    """
    try:
        data = socket.gethostbyname_ex(args[0])

        unique = []
        for row in data[2]:
            unique.append(row)
             
        unique = utils.sort_ipv4(list(set(unique)))

        for x in unique:
            pymyo.output(x)
            
    except:
        pymyo.error("Error looking up ipv4 address")
