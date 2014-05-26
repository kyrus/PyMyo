
###############################################################################
## File       :  whois.py
## Description:  Module for doing whois lookups on domains
##            :  
## Created_On :  Wed Sep 26 14:39:00 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Tue Jan 29 16:44:15 2013
## Modified_By:  Rich Smith (rich@kyr.us)
## License    :  BSD-3
##
##
###############################################################################
import pywhois

__author__  = "rich@kyr.us"
__version__ = 1.0
__updated__ = "26/09/2012"
__help__    = "Module for doing whois lookups on domains"
__alias__   = []

def Command(pymyo, name, *args):
    
    for d in args:
        data = pywhois.whois(d)
        
        data_order = ["domain_name", "registrant_name", "registrar", "registrar_url",
                      "creation_date","updated_date", "expiration_date" ]
        for d in data_order:
            try:
                pymyo.output( "%s: %s"%(d.replace("_", " "), getattr(data, d, "")[0]) )
            except:
                pymyo.output( "%s: "%(d.replace("_", " ")) )
