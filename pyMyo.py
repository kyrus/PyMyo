#!/usr/bin/env python

###############################################################################
## File       :  pyMyo.py
## Description:  Wrapper around the actual pyMyo classes to allow clean
##            :  runtime reloading
## Created_On :  Thu Nov  1 13:36:32 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Sun May  5 18:45:59 2013
## Modified_By:  Rich Smith (rich@syndis.is)
## License    :  BSD-3
##
##
###############################################################################
import pyMyoCli as _pyMyo

##Do performance logging to identify bottle necks ?
HOTSHOT = False

def pyMyo_loop():
    
    while True:

        try:
            ##Kick off the interpreter loop - the exit code will tell us when to quit or to reload
            pmyo = _pyMyo.pyMyoCli()
            reload_pymyo = pmyo()
            
            if not reload_pymyo:
                ##A normal exit, not reinstantiation required
                break
            
            print "[!] Reloading pyMyo ...."
            
        except KeyboardInterrupt:
            print "Ctrl-C caught. Exiting"
            pmyo.postloop()
            break    

##Done in this way via _pyMyo as it allows it to reload the pyMyo module without
## it being __main__ (which fails) and provides a way to reinstantiate the class to
## actually load any changes made to the pyMyo class
if __name__ == "__main__":
    
    
    if HOTSHOT:
        import hotshot, hotshot.stats
        
        ##Run the benchmark
        hs_profile = hotshot.Profile("pymyo.prof")
        ret = hs_profile.runcall(pyMyo_loop)
        hs_profile.close()
        
        ##Now print results
        stats = hotshot.stats.load("pymyo.prof")
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(20)  
        
    else:
        pyMyo_loop()
