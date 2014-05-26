
###############################################################################
## File       :  _pyMyo.py
## Description:  Multi purpose extensible shell
##            :  
## Created_On :  Tue Sep 25 13:03:39 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Sun May  5 18:45:20 2013
## Modified_By:  Rich Smith (rich@syndis.is)
## License    :  BSD-3
##
##
###############################################################################
__version__ = 0.1
__author__  = "rich@kyr.us"

import os
import sys
import ConfigParser
from collections import OrderedDict

from libs import utils 
    
##The abslute location of this file 
MODULE_LOCATION = os.path.abspath(os.path.dirname(__file__))


class pyMyo(object):
    """
    Core pyMyo class without any presentation layer bits
    """
    def __init__(self):
        self.available_modules   = {}
        self.aliases             = {} 
        
        ##Whether to cause the pyMyo class to be reinstantiated so runtime code changes will be loaded
        self.reload_pymyo        = False

        ##Read the configuration file
        self.read_config()
        
        
    def read_config(self):
        """
        Read and set configuration variables
        """
        ##Set defaults incase config file is corrupted
        config_defaults = {"prompt" : "pymyo #",
                           "shell"  : "/bin/bash",
                           "use_ipy":  "False",
                           "debug"  :  "False",
                           "banner" :  "True"
                           }
        
        ##Read config
        self.config = ConfigParser.SafeConfigParser(defaults = config_defaults)
        self.config.read(os.path.join(MODULE_LOCATION, "pyMyo.conf"))
        
        self.prompt   = self.config.get("Config", "prompt")+" " 
        self.shell    = self.config.get("Config", "shell")
        self.use_ipy  = self.config.getboolean("Config", "use_ipy")
        self.debug    = self.config.getboolean("Config", "debug")
        self.banner   = self.config.getboolean("Config", "banner")
        
        
    def __call__(self):
        """
        Overload this with a presentation layer specific invocation
        """
        self._main()
        return self.reload_pymyo
        
    
    def load_modules(self):
        """
        (pre)Load all the pyMyo modules so we can access their help docs, aliases etc
        """
        self.output("[+] Loading PyMyo Modules...")
        self.available_modules = utils.ImportModules()(os.path.join(MODULE_LOCATION, "modules"), filter = "command")


    def reload_modules(self):
        """
        Reloads all the pyMyo modules to take account of any changes, useful for when developing them etc
        """
        ##Load any entirely new modules & remove any modules that have been deleted from the fs
        #self.load_modules()
        
        ##Reload modules that already existed but may have changed
        #for m_name, m_obj in self.available_modules.items():
        #    m_obj = reload(m_obj)
        #    self.available_modules[m_name] = m_obj
            
        ## Reload pyMyo itself - this reloads the module but the class still needs to be reinstantiated
        pymyo_mod = reload(sys.modules["_pyMyo"])

        ##Marker to get the class reinstantiated from the caller - this must be returned by the subclasses __call__ method
        self.reload_pymyo = True

    def change_debug_state(self):
        """
        Flip debug flag to opposite state - 'on' to 'off', 'off' to 'on'
        """
        if self.debug:
            self.debug = False
        else:
            self.debug = True

        
    def populate_aliases(self):
        """
        Map module aliases to the modules
        """
        for m in self.available_modules.values():
            aliases = getattr(m, "__alias__", [])
            
            for a in aliases:
                self.aliases[a] = m
                

    def get_module(self, module_name):
        """
        Locate & return a module object from those loaded earlier
        """
        try:
            ##Equivilent to from modules import <supplied command>
            module_obj = self.available_modules.get(module_name, None)
            
            if not module_obj:
                ##Check for an alias/shortcut if not a named module
                module_obj = self.aliases[module_name]
                
        except KeyError:
            self.error( "Unknown command: '%s '"%(module_name) ) 
            module_obj = None
            
        return module_obj


    def call_module(self, module_name, *module_args):
        """
        Bridge method to allow one module to call another one, helps keep this reusable
        The return from this method is whatever the called module returns
        
        All error handling must hapen in the caller, or callee
        """
        module_obj = self.get_module(module_name)
                    
        if module_obj:
            
            ##Then run module.<supplied command name>(args)
            data = getattr(module_obj, "Command")(self, module_name, *module_args)
            
            return data  
        
        
    def get_module_info(self, module_name):
        """
        Return a dictionary of meta info about a module  
        """
        module_obj = self.get_module(module_name)
        info_dict = OrderedDict()
        
        if module_obj:
            
            info_dict["Author"]       = module_obj.__author__
            info_dict["Version"]      = module_obj.__version__
            info_dict["Last Updated"] = module_obj.__updated__
            info_dict["Aliases"]      = module_obj.__alias__
            info_dict["Help"]         = module_obj.__help__
            
        return info_dict
    
    def get_project(self, module):
        pass
    
    
    def set_project(self, module):
        pass 
    
    def error(self, msg):
        """
        Display error
        OVERIDE IN PRESENTATION SPECIFIC SUBCLASS
        """
        pass
    
    def _error(self):
        """
        Hook to call from subclass to print debugging info if enabled
        """
        if self.debug:
            print "[!] DEBUG DATA:"
            import traceback
            traceback.print_exc()
    
    def output(self, msg):
        """
        Message something back to the user (not used for errors)
        OVERIDE IN PRESENTATION SPECIFIC SUBCLASS
        """
        pass
    
    def cleanup(self):
        pass    

