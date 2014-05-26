
###############################################################################
## File       :  ips.py
## Description:  Return both ipv4 and ipv6 data for a given host
##            :  
## Created_On :  Tue Sep 25 16:33:26 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Sun Apr 14 19:41:40 2013
## Modified_By:  Rich Smith (rich@syndis.is)
## License    :  BSD-3
##
##
###############################################################################
import socket
from libs import utils

__author__  = "rich@kyr.us"
__version__ = 1.0
__updated__ = "26/09/2012"
__help__    = "Module for looking up both IPv4 & IPv6 addresses of host"
__alias__   = ["ip46", "ip64"]

def Command(pymyo, name, *args):
    """
    Get both the IPv4 & IPV6 addresses of the host - just call through to the 
    ipv4 & ipv6 modules
    """
    try:
        pymyo.call_module("ipv4", *args)
        pymyo.call_module("ipv6", *args)
    
    except:
        pymyo.error("Error looking up ip addresses for %s"%(args[0]))
    