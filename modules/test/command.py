
###############################################################################
## File       :  test.py
## Description:  Test command module for pymyo
##            :  
## Created_On :  Tue Sep 25 14:29:44 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Tue Jan 29 16:44:09 2013
## Modified_By:  Rich Smith (rich@kyr.us)
## License    :  BSD-3
##
##
###############################################################################
__author__  = "rich@kyr.us"
__version__ = 1.0
__updated__ = "26/09/2012"
__help__    = "Test module for showing structure"
__alias__   = ["t", "t3st"]

def Command(pymyo, name, *args):
    
    print "This is a test command."
    if args:
        pymyo.output( "The arguments passed were %s"%args)
        
    pymyo.notify("The reference back to the pymyo instance is: %s"%(pymyo))
