
###############################################################################
## File       :  screenshot.py
## Description:  Kick off a screen capture tool - cross platform support
##            :  
## Created_On :  Tue Sep 25 17:21:36 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Tue Jan 29 16:44:00 2013
## Modified_By:  Rich Smith (rich@kyr.us)
## License    :  BSD-3
##
##
###############################################################################
import os
import sys
import tempfile
import subprocess

__author__  = "rich@kyr.us"
__version__ = 1.0
__updated__ = "01/10/2012"
__help__    = "Module for taking a screenshot"
__alias__   = ["ss"]

def Command(pymyo, name, *args):
    """
    Take a screenshot
    """
    
    curr_plat = sys.platform
    
    ##OSX
    if curr_plat == "darwin":
        
        tmp_handle, tmp_fn = tempfile.mkstemp(suffix = ".png")
        
        ss_cmd   = ["/usr/sbin/screencapture"]

        if "choose" in args or "c" in args:
            
            ss_cmd.append("-w")
        
        ##Add in filename
        ss_cmd.append(tmp_fn)

        try:
            ret = subprocess.check_output(ss_cmd)
            pymyo.output( ret )
            pymyo.output("Saved screenshot to: %s"%(tmp_fn))
        except subprocess.CalledProcessError, err:
            pymyo.error("Error grabbing screenshot: %s"%(err))
            
        ##Close file    
        os.close(tmp_handle)
        
        
    #TODO support other platforms
    else:
        pymyo.notify( "%s is not supported for screenshots at the moment"%(sys.platform))
