
###############################################################################
## File       :  viewstatedecode.py
## Description:  Return a decoded viewstate from an encoded viewstate parameter
##            :  
## Created_On :  Tue Sep 25 17:21:36 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Tue Jan 29 16:43:54 2013
## Modified_By:  Rich Smith (rich@kyr.us)
## License    :  BSD-3
##
##
###############################################################################
import base64
import peekviewstate
from libs import utils

__author__  = "rich@kyr.us"
__version__ = 1.0
__updated__ = "09/07/2012"
__help__    = "Module for decoding viewstate parameters"
__alias__   = ["vsd"]

def Command(pymyo, name, *args):
    """
    Decodes a viewstate, based on a modified peekviewstate (https://code.google.com/p/peekviewstate)
    """
    for s in args:
        try:
            vs = base64.decodestring(s)
            pymyo.output( peekviewstate.parse(vs)[1] )
        except:
            pymyo.error("Error viewstate decoding %s"%(s) )
