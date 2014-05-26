#pyMyo README

##About

pyMyo is an extensible python shell interface that allows quick 'n' dirty scripts to be written to help with common tasks and have them easily integrate with a common shell interface. pyMyo also allows the evaluation of Python statements and system commands, as well as quick access to a Python REPL and system shells.

The example modules so far included are focused on pen-testing and
target recon, but you could write modules to do whatever you like.

pyMyo was inspired by [Ronin](http://ronin-ruby.github.io/) but I wanted it to be a Python system as that is the rapid development language I prefer. The name pyMyo is a portmanteau of 'python' and ['daimyo'](http://en.wikipedia.org/wiki/Daimyo) to show the inspiration by [Ronin](http://ronin-ruby.github.io/).

The underlying functionality & interaction layers are separate, however currently the only interface to the backend is from a commandline shell. It should be fairly simple to add in other ways to interact as desired.


##Usage

The current functionality & shortcuts can be summarised as:

    'console' or '>'     - drop to a interactive python shell (ctrl-d to exit back to pyMyo)
    'ipyconsole' or '>'  - drop to a interactive python shell if available (ctrl-d to exit back to pyMyo)
    [whether '>' gives a standard or ipyconsole is set in the config file]
    'ishell' or '$'      - drop to a interactive system shell (ctrl-d to exit back to pyMyo)
    [the system shell used is set in the config file]
    'eval' or '='        - evaluate the argument as python code
    'shell' or '!'       - execute the argument as system shell code
    'py'                 - execute the argument as python code
    'list'               - list the available modules
    'info <module name>' - Show module metadata
    <module name> arg1 arg2 ... - run module on list of arguments
    <enter>              - run previous command
    <module name> enter  - without args runs the stated module with the last argument specified
    <tab>                - autocomplete
    <up>, <down>         - browse shell history, separate histories are kept for pyMyo shell, system shells & python shells. All histories are saved and restored each session for persistent history 
                       
    <math expression>    - any command that starts with a digit will be evaluated as a math expression using standard Python mathematical operators and rules
    
    'reload'             - Cause pyMyo to reload all the command modules without restarting pyMyo, useful for debugging / developing new command modules
    'debug'              - Toggle debugging output, useful when things are breaking
    
    'q','exit', 'ctrl-d', 'ctrl-c' - quit pyMyo
    
    
##Example modules

Some initial example modules are bundled with the open source release of pyMyo, these are:

* `b64encode`       - Return a base64 encoded version of the argument passed
* `b64decode`       - Return a base64 decoded version of the argument passed
* `geoip`           - Return GeoIP data of the passed IP adrress (The latest version of the `GeoLiteCity.dat` database needs to be downloaded from MaxMind and placed in `/modules/geoip` before this module will work)
* `hashcrack`       - Submit a hash value to a variety of online hash cracking services in an effort to crack it
* `ips`             - Return the ipv4 and ipv6 address of the passed in domain name
* `ipv4`            - Return the ipv4 address of the passed in domain name
* `ipv6`            - Return the ipv6 address of the passed in domain name
* `multihash`       - Return the MD5, SHA1, SHA224, SHA256, SHA384 & SHA512 hashes of the argument string
* `myip`            - Return the public IP of the system pyMyo is on
* `rip`             - Return the reverse DNS of supplied IP address
* `screenshot`      - Perform a screengrab (OS X only)
* `test`            - Barebones example command module
* `viewstatedecode` - Attempt to decode the viewstate string passed in as an argument 
* `whois`      - Return WHOIS data on the supplied IP / hostname
    
##Extension
Custom command modules reside in directories under `/modules` and have a very simple structure, looking at the example code should show you everything you need to know. However a quick rundown is:

* Each command module must be in a subdir of `/modules` with a unqiue name, this name will be how the command is invoked from the pyMyo shell
* The entry point of each command is a module named `command.py`
* In `command.py` there needs to be a function named `Command` and some `metadata`
* The `Command` function takes three arguments `(pymyo, name, *args)`
	* The first argument `pymo` gives access to the calling class's namespace and has some common library functions described below 
* Within command you can carry out whatever logic you need
* The metadata for each module is just a series of variables:
	* `__author__`  - Who created the module (string)
	* `__version__` - The version of the module (float)
	* `__updated__` - When the module was last update (string)
	* `__help__`    - A brief description of what the module does (string)
	* `__alias__`   - Alternative short names by which this command can be called from the pyMyo shell (list of strings)
	
A barebones command module looks like:

**command.py**

```
__author__  = "you@an_email.com"
__version__ = 1.0
__updated__ = "26/05/2014"
__help__    = "A useful string of test about the module"
__alias__   = ["t", "t3st"]

def Command(pymyo, name, *args):
    print "This is a test command."
    if args:
        pymyo.output( "The arguments passed were %s"%args)
    pymyo.notify("The reference back to the pymyo instance is: %s"%(pymyo))

```

The `pymyo` argument passed to every command module gives access to the pymyo namespace and has a number of convenience functions that are used by command modules:

* `pymyo.call_module()` - Call another myo module by name along with arguments e.g. `pymyo.call_module("ipv4", *args)`
* `pymyo.output()`      - Display a message in the interaction layer
* `pymyo.notify()`      - Display a notification message in the interaction layer
* `pymyo.error()`       - Display a error message in the interaction layer

	
##Supported Systems
pyMyo has been tested most on OS X but I expect should work fine on Linux or BSD like systems. No idea about Windows, good luck (in so many ways) if you wish to use pyMyo on a Windows box. 
	
##License

pyMyo is licensed under the BSD 3-clause license.

Code from other open source projects is covered under the licenses specified by them, these projects include:

* pygeoip (LGPL)
* findmyhash.py (GPL-v3)
* sh.py (??)
* whois.py (??)
* peekviewstate.py (??) 