
###############################################################################
## File       :  hashcrack.py
## Description:  Module to attemot to crack a hash using online services
##            :  
## Created_On :  Wed Sep 26 12:33:16 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Tue Jan 29 16:42:59 2013
## Modified_By:  Rich Smith (rich@kyr.us)
## License    :  BSD-3
##
##
###############################################################################
import findmyhash

__author__  = "rich@kyr.us"
__version__ = 1.0
__updated__ = "11/10/2012"
__help__    = "Module for cracking hashes using various online services"
__alias__   = ["hc"]




def Command(pymyo, name, *args):
    """
    Attempt to crack the supplied hash of the type specified
    args[0] - hashtype (md5, sha1 etc)
    args[1] - hash string
    """
    try:
        hashtype  = args[0].lower()
        hashvalue = args[1]

        ## Configure the Cookie Handler
        findmyhash.configureCookieProcessor()
    
        ## Initialize PRNG seed
        findmyhash.seed()
    
        ## Crack the hash
        cracked = findmyhash.crackHash_quiet(hashtype, hashvalue, pymyo.output)
        
        if not cracked:
            pymyo.output("Unable to crack hash: %s (%s)"%(hashvalue, hashtype))
            
        else:
            
            pymyo.output("\nHash cracked %s = %s\n"%(cracked.keys()[0],
                                                       cracked.values()[0][0]))
        
        
    except Exception, err:
        pymyo.error("Error while trying to crack hash: %s"%(err))
