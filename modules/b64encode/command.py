###############################################################################
## File       :  b64encode.py
## Description:  Base64 encode a supplied list of strings
##            :  
## Created_On :  Wed Sep 26 12:33:16 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Tue Jan 29 16:42:46 2013
## Modified_By:  Rich Smith (rich@kyr.us)
## License    :  BSD-3
##
###############################################################################
import base64

__author__  = "rich@kyr.us"
__version__ = 1.0
__updated__ = "26/09/2012"
__help__    = "Module for encoding a string in Base64 representation"
__alias__   = ["b64e"]

def Command(pymyo, name, *args):
    """
    Base64 denode each argument supplied
    """
    for s in args:
        try:
            pymyo.output( base64.encodestring(s).strip() )
        except:
            pymyo.error( "Error encoding %s"%(s) )
