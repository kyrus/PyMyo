
###############################################################################
## File       :  rip.py
## Description:  Return reverse dns lookup for supplied address
##            :  
## Created_On :  Tue Sep 25 17:21:36 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Tue Jan 29 16:43:54 2013
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
__help__    = "Module for doing reverse DNS lookups"
__alias__   = ["r"]

def Command(pymyo, name, *args):
    """
    Get reverse DNS lookup of the host
    """
    try:
        data = socket.gethostbyaddr(args[0])
        pymyo.output( data[0] )
            
    except:
        pymyo.error( "Error doing reverse lookup for for %s"%(args[0]) )
