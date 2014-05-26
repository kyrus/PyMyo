
###############################################################################
## File       :  utils.py
## Description:  general purpose library utilities
##            :  
## Created_On :  Tue Sep 25 17:36:21 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Sun Apr 14 19:44:54 2013
## Modified_By:  Rich Smith (rich@syndis.is)
## License    :  BSD-3
##
##
###############################################################################
import os
import re
import imp
import sys
import time

def sort_ipv4(ips):
    """
    Sort a list of ipv4 addresses in ascending order
    """
    for i in range(len(ips)):
        ips[i] = "%3s.%3s.%3s.%3s" % tuple(ips[i].split("."))
    ips.sort()
    for i in range(len(ips)):
        ips[i] = ips[i].replace(" ", "")   
        
    return ips

class ImportModules(object):
    """
    A pattern for importing all Python modules from a supplied directory root that is walked 
    until the leaves, .py, .pyc, .pyo, .pyd will all be imported with the normal import preference
    rules applied
    
    Optionally supply a regex string, which if supplied must match the PATH of any modules that 
    you want to be imported
    
    return a dictionary of modules keyed on their names qualified by dotted path
    
    NOTE:
    In the case of the rpyc_implant_server we walk the dir tree from the given start point and
    find any 'Service.py' module. We then import it (which means doing all the parent hierachy imports)
    and then finally add that module to a list of capabilities.
    """
    def __call__(self, path, only_packages = False, filter=None, fail_hard = False):
        """
        Walk the dir structure and import appropriate files
        
        Return a dictionary with all loaded modules in
        """
        #TODO proper exception handling
        self.path        = path
        self.fail_hard   = fail_hard
        self.module_dict = {}
        
        self.only_import_packages = only_packages

        ##Walk the tree to all leaves
        for root, dirs, files in os.walk(path):
            
            ##Filter out python modules and import
            if self.only_import_packages:
                self._import(root, dirs)
            else:
                self._import(root, self._filter(files, filter_re=filter))
        
        return self.module_dict
            
            
    def _import(self, root, modules_to_import, put_in_dict=True):
        """
        Do the import - raise any errors up for the caller to deal with
        """
        f = None

        for m in modules_to_import:
            
            ##Do the parent imports required for a hierarchical import
            if root and root != self.path:
                ##We eat up the chain of the directory hierarchy until we hit the path we began
                ## from, we then know we will have imported all parents etc
                
                ##Snip one level off the root
                parent_root   = os.path.sep.join(root.split(os.path.sep)[:-1])
                parent_module = root.split(os.path.sep)[-1]
                self._import(parent_root, [parent_module], False)
                
            q_mod = os.path.join(root.replace(self.path,""),m).replace(os.path.sep, ".").strip(".")

            try:
                ##Find the modules whatever the extension
                f, filename, descr = imp.find_module(m, [root])

                loaded_module = imp.load_module(q_mod, f, filename, descr)
                #print "\t Imported %s"%(q_mod)
                
                ##Load it and add it to our dict representation of this dir tree
                if put_in_dict:
                    #self.module_dict[q_mod] = loaded_module
                    self.module_dict[q_mod.split(".")[0]] = loaded_module
                    
                
            except ImportError, err:
                print "[-] Error importing %s : [%s]"%(q_mod, err)
                if self.fail_hard:
                    raise
            
            finally:
                if f:
                    f.close()
    
        
    def _filter(self, modules, filter_re=None):
        """
        Skip __init__ & produce a unique list of modules across all known extensions
        Apply filtering to list of returned files prior to import
        """
        ret = []
        py_exts = [".py", ".pyc", ".pyo", ".pyd"] #todo others
        
        for m in modules:

            if "__init__" in m or \
               os.path.splitext(m)[-1] not in py_exts or\
               os.path.splitext(m)[0]  in ret:
                continue
            
            ##Check special regex filter - if re supplied and nothing matched return
            if filter_re and not re.search(filter_re, m):
                continue
            
            ret.append(os.path.splitext(m)[0])
        
        return ret
