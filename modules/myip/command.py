
###############################################################################
## File       :  myip.py
## Description:  Get the public IP of this system
##            :  
## Created_On :  Wed Sep 26 12:23:31 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Tue Jan 29 16:43:44 2013
## Modified_By:  Rich Smith (rich@kyr.us)
## License    :  BSD-3
##
##
###############################################################################
import urllib2

__author__  = "rich@kyr.us"
__version__ = 1.0
__updated__ = "26/09/2012"
__help__    = "Module for getting the public IP of the system"
__alias__   = ["icanhazip", "whatismyip", "mip"]

def Command(pymyo, name, *args):
    """
    Get the public IP of this system
    ref : http://www.commandlinefu.com/commands/view/2966/return-external-ip#comment
    """
    #https://secure.inofrmaction.com/ipecho/
    try:
        ret_ip = urllib2.urlopen("http://icanhazip.com")
        pymyo.output( ret_ip.read().strip() )
        
    except Exception, err:
        pymyo.error("Error resolving public IP: %s"%(err))