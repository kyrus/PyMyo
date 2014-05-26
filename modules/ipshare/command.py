
###############################################################################
## File       :  ipv4.py
## Description:  Do a reverse lookup on an IP address / hostname to see what
##            :  other web sites are hosted on the same host. Uses whois.webhosting.info
## Created_On :  Tue Sep 25 17:21:36 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Tue Jan 29 16:43:09 2013
## Modified_By:  Rich Smith (rich@kyr.us)
## License    :  BSD-3
##
##
###############################################################################
import ReverseLookup
from libs import utils

__author__  = "rich@kyr.us"
__version__ = 1.0
__updated__ = "31/10/2012"
__help__    = "Module for reverse looking up websites that share the same IP address"
__alias__   = []

def Command(pymyo, name, *args):
    """
    Get the domains that share the same IP using whois.webhosting.info
    """
    try:
        rl = ReverseLookup.ReverseLookup()
        
        for x in args:
            
            results = rl(x)

            for r in results:
                pymyo.output(r)
            
    except:
        pymyo.error("Error doing a shared host lookup for for %s"%(args[0]))

