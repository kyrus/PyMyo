
###############################################################################
## File       :  geoip.py
## Description:  Lookup the geoip result for a host
##            :  
## Created_On :  Tue Sep 25 15:58:00 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Sun Apr 14 20:16:43 2013
## Modified_By:  Rich Smith (rich@syndis.is)
## License    :  BSD-3
##
##
###############################################################################
import os
import socket

import pygeoip
MODULE_LOCATION = os.path.abspath(os.path.dirname(__file__))

__author__  = "rich@kyr.us"
__version__ = 1.0
__updated__ = "26/09/2012"
__help__    = "Module for looking up the geoip location of a host"
__alias__   = ["geo"]

#Todo - add functionality to update the db file
def Command(pymyo, name, *args):
    """
    Get the geoip results for the supplied address/host
    """
    ##Choose whether to lookup via ipv4, ipv6 or hostname
    target = args[0]
    
    if target == "update":
        return update(pymyo)

    ##Test ipv4
    try:
        socket.inet_pton(socket.AF_INET, target)
        gi = pygeoip.GeoIP(os.path.join(MODULE_LOCATION, "GeoLiteCity.dat"))
        record = gi.record_by_addr(args[0])
        pymyo.output("ipv4 :\t%s"%(args[0]))
        parse_record(pymyo, record)
        return None
    except Exception, err:
        pass

    ##Test ipv6 - not supported by the module yet
    #try:
        #socket.inet_pton(socket.AF_INET6, target)
        #gi = pygeoip.GeoIP(os.path.join(MODULE_LOCATION, "GeoLiteCityv6.dat"))
        #print gi.record_by_addr(args[0])
        #return None
        
    #except Exception, err:
        #print err  
    
    ##default to a host name
    try:
        gi = pygeoip.GeoIP(os.path.join(MODULE_LOCATION, "GeoLiteCity.dat"))
        record = gi.record_by_name(args[0])
        pymyo.output("hostname :\t%s"%(args[0]) )
        parse_record(pymyo,record)
        return None
    except Exception, err:
        pymyo.error("Unable to use geoip lookup on %s"%(target))


def parse_record(pymyo, record):
    """
    Pretty print the record data
    """
    for key, value in record.items():
        pymyo.output("%s :\t%s"%(key, value))


def update(pymyo):
    """
    Update the GeoIP database
    """
    pymyo.notify("Update of the database is not supported yet")

