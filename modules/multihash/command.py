
###############################################################################
## File       :  multihash.py
## Description:  Module for doing an MD5, SHA1, SHA224, SHA256, SHA384, SHA512
##            :  hash over a supplied list of values, return in Hex form
## Created_On :  Tue Jan 29 16:32:23 2013
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Tue Jan 29 17:08:17 2013
## Modified_By:  Rich Smith (rich@kyr.us)
## License    :  BSD-3
##
##
###############################################################################
import hashlib
from libs import utils

__author__  = "rich@kyr.us"
__version__ = 1.0
__updated__ = "29/01/2013"
__help__    = "Module for returning an MD5, SHA1, SHA224, SHA256, SHA384, or SHA512 hash of a supplied values. 'all_hash' returns every hash type for the value."
__alias__   = list(hashlib.algorithms) + ['all_hash', 'allhash']

def Command(pymyo, name, *args):
    """
    Calculate and return the MD5, SHA1, SHA224, SHA256, SHA384, SHA512 hash of the supplied values
    
    Uses introspection to the alias that it was called with to determine what hashing function to use
    or whether to iterate through them all
    """    
    ##Do a hash of a specified type or do all hashes ?
    if name in ["all_hash", "allhash", "multihash"]:
        hash_functions = hashlib.algorithms
    else:
        hash_functions = [name]
        
    
    for hashme in args:
        
        results = []
        pymyo.output("Hash value(s) of '%s':\n"%(hashme))
        
        for hf in hash_functions:
        
            try:
                ##Choose the hashing function depending on the alias the function was actually 
                ## called by. Saves having to have many sperate modules that do the same thing
                hash_obj = getattr(hashlib, hf)
                pymyo.output("%s: %s"%(hf.upper(), hash_obj(hashme).hexdigest()))

                    
            except:
                pymyo.error("Error perfoming %s hash operation of %s"%(name, args[0]))
