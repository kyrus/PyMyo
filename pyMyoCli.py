__version__ = 0.1
__author__  = "rich@kyr.us"

import os
import cmd
import sys
import code
import readline
import traceback
import rlcompleter

from _pyMyo import pyMyo

##Command completion for OS X requires this as it doesn't use gnu readline
if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
    
else:
    readline.parse_and_bind("tab: complete")

##Stop overly large histories    
readline.set_history_length(1000)

##Try for iPython support
#ToDo - make supported shells / consoles modular in a /shells subdir ?
try:
    from IPython import embed
    ipy_support = True
    
except ImportError:
    print "[-] IPython support seems unavailable"
    ipy_support = False
    
##The absolute location of this file
MODULE_LOCATION = os.path.abspath(os.path.dirname(__file__))

class pyMyoCli(pyMyo, cmd.Cmd):
    """
    General CLI/Shell wrapper for the invocation of modules that
    help with a whole variety of nifty things
    """ 
    def __init__(self):
        """
        Set some defaults
        """
        ##Init pyMyo - super does not work correctly ...... ?
        pyMyo.__init__(self)

        ##Init parser loop
        cmd.Cmd.__init__(self)
        
        ##Defaults
        self.prev_arg            = ""
        self.shotcuts            = ["!", ">", "=", "$"]
        self.autoarg_exceptions  = ["help", "console", "shell"]

        if self.banner:

            self.intro = """
   ___       \033[35m__  ___\033[0m
  / _ \__ __\033[35m/  |/  /_ _____\033[0m
 / ___/ // \033[35m/ /|_/ / // / _ \\\033[0m
/_/   \\_, \033[35m/_/  /_/\\_, /\\___/\033[0m
     /___/       \033[35m/___/\033[0m"""+" v %s\n"%(__version__)


    def _main(self):
        """
        Just call the cmdloop method in cmd module
        """
        return self.cmdloop() 
    
    
    def _save_history(self, history_file):
        """
        Save the commandline history to the readline history provided
        + Clear the history buffer
        """
        readline.write_history_file(os.path.join(MODULE_LOCATION, history_file))
        readline.clear_history()  
        
    
    def _load_history(self, history_file):
        """
        Load a previously saved readline history file 
        """
        try:
            readline.read_history_file(os.path.join(MODULE_LOCATION, history_file))
        except IOError:
            pass    
        
        
    def _swap_history(self, old_history, new_history):
        """
        Save old history and swap to new history
        """
        self._save_history(old_history)
        self._load_history(new_history)
    
    
    def cmdloop(self, intro = None):
        """
        Overload cmdloop to allow a cleaner way for us to actually reload the pymyo instance
        at run time to allow nicer dev cycles
        """
        cmd.Cmd.cmdloop(self, self.intro)

        return self.reload_pymyo
    
    
    def preloop(self):
        """
        Retrieve previous history before we kick off the main loop
        """
        try:
            readline.read_history_file(os.path.join(MODULE_LOCATION, ".pymyo.history"))
        except IOError:
            pass 
        
        self.load_modules()
        self.populate_aliases()
        #self.populate_help()
        #self.populate_autocomplete()
        
        
    def postloop(self):
        """
        Save the history before we exit
        """
        ##Save history
        readline.write_history_file(os.path.join(MODULE_LOCATION, ".pymyo.history"))
        
        
    def postcmd(self, stop, line):
        """
        Store the previous argument for quick auto retrevial in future commands
        """
        line = line.strip()
        self.prev_arg = ''.join(line.split(" ")[1:])
        
        return stop
        
    def precmd(self, line):
        """
        Hook to add previous argument to current command if no arg is given 
        (and the command isn't on an exception list)
        """
        line = line.strip()
        if len(line) and len( line.split(" ")) <2 and line[0] not in self.shotcuts and line.split(" ")[0] not in self.autoarg_exceptions and not line[0].isdigit():
            line = "%s %s"%(line, self.prev_arg)
            
        return line
        
        
    def parseline(self, line):
        """
        Override the standard parseline method to allow us to alias '#' to "do_py"
        in the same way "!" is aliased to "do_shell"
        """
        line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
            
        elif line[0] == "=":
            if hasattr(self, 'do_eval'):
                line = 'eval ' + line[1:]
            else:
                return None, None, line 
            
        elif line[0] == ">":
            if hasattr(self, 'do_ipyconsole') and self.use_ipy and ipy_support:
                line = 'ipyconsole ' + line[1:]
            elif hasattr(self, 'do_console'):
                line = 'console ' + line[1:]
            else:
                return None, None, line         
            
        elif line[0] == '$':
            if hasattr(self, 'do_ishell'):
                line = 'ishell ' + line[1:]
            else:
                return None, None, line
            
        elif line[0] == '!':
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        i, n = 0, len(line)
        while i < n and line[i] in self.identchars: i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line            
        
        
    def do_py(self, line):
        """
        Execute python expression 
        """
        try:
            exec(line)
        except:
            self.output(  "[-] Error executing expression '%s' "%(line) )
            traceback.print_exc()
            self.output( self.ruler*70 )
    
    
    def do_eval(self, line):    
        """
        Evaluate python expression (also accessed via `= expr` )
        """
        try:
            self.output( eval(line) )
        except:
            self.output( "[-] Error evaluating expression '%s' "%(line) )
            traceback.print_exc()
            self.output( self.ruler*70 )        
            
            
    def do_ipyconsole(self, line):
        """
        Drop to an IPython interactive shell 
        """
        #TODO - support saving ipython history between sessions ....
        if not ipy_support:
            print "[-] IPython dependencies not avaialble, please install IPython"
            return None
        
        ##Save the pyMyo and the python console histories
        self._save_history(".pymyo.history")

        ##Start the embedded IPython console - ctrl-d to exit
        embed()
    
        ##Restore previous pyMyo history
        self._load_history(".pymyo.history")
    
    
    def do_console(self, line):
        """
        Drop to a python interactive shell (also accessed via `> expr` )
        (Ctrl-D to exit by to pyMyo)
        """        
        ##Swap the pyMyo and the python console histories
        self._swap_history(".pymyo.history", ".pymyo_console.history")
        
        console = code.InteractiveConsole()
        banner = "** \033[35mPress Ctrl-D to exit back to the pyMyo shell\033[0m **\n"
        banner += "Python %s on %s"%(sys.version, sys.platform)
        console.runsource("import sys;sys.ps1='pB >>> '")
        console.interact(banner)
        
        ##Save console history and Restore previous pyMyo history
        self._swap_history(".pymyo_console.history", ".pymyo.history")
        
        
    def do_shell(self, line):
        """
        Run a shell command (also accessed via `! cmd` )
        """
        print os.popen(line).read()        
        
    
    def do_ishell(self, line):
        """
        Drop to interactive system shell (also accessed via `$` )
        (Ctrl-D to exit by to pyMyo)
        """        
        ##Swap the pyMyo and the system shell histories
        readline.write_history_file(os.path.join(MODULE_LOCATION, ".pymyo.history"))
        readline.clear_history()

        print "** \033[35mPress Ctrl-D to exit back to the pyMyo shell\033[0m **\n"
        os.system(self.shell) 
        
        try:
            readline.read_history_file(os.path.join(MODULE_LOCATION, ".pymyo.history"))
        except IOError:
            pass          
      
        
    def do_list(self, line):
        """
        List available pyMyo modules
        """
        am = self.available_modules.keys()
        am.sort()
        
        ##Pretty print into columns
        longest_name = 0
        for m in am:
            if len(m) > longest_name:
                longest_name = len(m)
        
        print "Module %s Aliases"%(" "*(longest_name-5))
        print "------ %s -------"%(" "*(longest_name-5))
        for m in am:
            print "%s %s- %s"%(m, " "*(longest_name-len(m)), ', '.join(self.available_modules[m].__alias__))
            
        
    def do_info(self, line):
        """
        Display metadata about a specified module
        """
        split_line = line.split(" ")
        
        info_dict = self.get_module_info(split_line[0])
        
        if not info_dict:
            self.output("No info available for %s "%(split_line[0]))
        
        else:
            self.output("Info for %s module:\n"%(split_line[0]))
            
            for key, value in info_dict.items():
                
                self.output("%s - %s"%(key, value))
        
    
    def do_reload(self, line):
        """
        Call the reload routine to reload all pyMyo modules
        """
        self.reload_modules()
        
        ##Cause the cmdloop to exit so the pymyo class itself can be reinistantiated to take account of
        ## any changes in the reloaded pymyo module
        return True


    def do_debug(self, line):
        """
        Turn debugging on/off
        """
        self.change_debug_state()
        self.output("Debugging = %s"%(self.debug))


    def do_new_module(self, line):
        """
        Create a skeleton directory for a new module - will then need to be hand coded
        """
        #todo
        
    
    def default(self, line):
        """
        Run a pyMyo module
        
        This is the catchall that is used when the input command doesn't match any of the hardcoded
         commands above. We then try and import a module of the specified name from the 'modules'
         dir. This allows for simple extension without having to modify the core pyMyo class.
        """
        ##Call a module or do a calculation ? - check if first char is a digit if so do a calc
        if line[0].isdigit():
            self.do_eval(line)
            
            return None
            
        split_line = line.split(" ")

        try:
            ##Attempt to find a given module via it's name or alias
            module_obj = self.get_module(split_line[0])
            
            if module_obj:
                
                ##Then run module.<supplied command name>(args)
                data = getattr(module_obj, "Command")(self, split_line[0], *split_line[1:])
                self.output( "" )
                
                return data
            
        except Exception, err:
            self.output( self.ruler*70 )
            print err
            self.error("Error executing command '%s' "%(line))
            self._error()
            self.output( self.ruler*70 )
            

    def do_EOF(self, arg):
        """
        Catch ctrl-d
        """
        print "\nCtrl-D caught. Exiting"
        return self.do_exit
    
    def do_exit(self, arg):
        """
        Quit the shell
        """
        ##call pyMyo cleanup routines
        self.cleanup()
        
        return True
    
    def do_quit(self, arg):
        """
        Quit the shell
        """
        return self.do_exit
    
    def do_q(self, arg):
        """
        Quit the shell
        """
        return self.do_exit  
    
     
    def output(self, msg):
        """
        Print output to stdout in the CLI
        """
        #TODO take a iterable/json instead of a string ?
        print msg
        
        
    def notify(self, msg):
        """
        Print message to stdout in the CLI with a "[!]" prepended
        """
        #TODO take a iterable/json instead of a string ?
        print "[!] %s"%(msg)
        
        
    def error(self, msg):
        """
        Print error to stdout in the CLI with a "[-]" prepended
        """
        #TODO take a iterable/json instead of a string ?
        print "[-] %s"%(msg)
        
        ##Call the main error class to do traceback prints etc if debugging enabled
        self._error()
        
        
if __name__ == "__main__":
    
    try:
        ##Kick off the interpreter loop
        pbc = pyMyoCli()
        pbc()
        
    except KeyboardInterrupt:
        print "Ctrl-C caught. Exiting"
        pbc.postloop()
