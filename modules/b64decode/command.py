
###############################################################################
## File       :  b64decode.py
## Description:  Base64 decode a supplied list of strings
##            :  
## Created_On :  Wed Sep 26 12:33:16 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Tue Jan 29 16:42:41 2013
## Modified_By:  Rich Smith (rich@kyr.us)
## License    :  BSD-3
##
##
###############################################################################
import base64

__author__  = "rich@kyr.us"
__version__ = 1.0
__updated__ = "26/09/2012"
__help__    = "Module for decoding a string from Base64 representation"
__alias__   = ["b64d"]

def Command(pymyo, name, *args):
    """
    Base64 decode each argument supplied
    """
    for s in args:
        try:
            pymyo.output( base64.decodestring(s) )
        except:
            pymyo.error("Error decoding %s"%(s) )