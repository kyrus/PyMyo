
###############################################################################
## File       :  ipv6.py
## Description:  return an IPv6 address of a host name using nslookup
##            :  
## Created_On :  Tue Sep 25 14:43:56 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Wed Sep 26 14:10:00 2012
## Modified_By:  Rich Smith (rich@kyr.us)
## License    :  BSD-3
##
##
###############################################################################
import re
import sys
from libs.sh import nslookup

def Command(*args):
    """
    Get the IPv6 address of the specified host
    """
    if sys.platform == "darwin":
        data = nslookup("-querytype=AAAA", args[0])
        
    elif sys.platform == "linux":
        data = nslookup("-q=AAAA", args[0])
        
    else:
        print "ipv6 module does support %s"%(sys.platform)
        
    ##Parse output 
    try:
        addr = re.split("AAAA address ", str(data))[1].split("\n")[0] #NASTY
        print addr
    except:
        print "%s does not resolve to an ipv6 address"%(args[0])