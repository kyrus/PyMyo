###############################################################################
## File       :  ReverseLookup.py
## Description:  
##            :  
## Created_On :  Wed Oct 31 18:01:06 2012
## Created_By :  Rich Smith (rich@kyr.us)
## Modified_On:  Wed Oct 31 18:30:22 2012
## Modified_By:  Rich Smith (rich@kyr.us)
## License    :  BSD-3
##
##
###############################################################################
##Quick and Dirty IP -> hostnames lookup from the webhosting.info site
import sys
import socket
import getpass
import urllib2


class ReverseLookup:
    
    def __init__(self, user=None, password=None, proxy=None):
        
        
        ##Who are we asking for the lookup
        self.domain = "whois.webhosting.info/"
        
        ##Set up a proxy if needed 
        if proxy:
            http_proxy = urllib2.ProxyHandler({'http': 'http://%s:%s@%s'%(user, password, proxy)})
            auth       = urllib2.HTTPBasicAuthHandler()
            opener     = urllib2.build_opener(http_proxy, auth, urllib2.HTTPHandler)
            urllib2.install_opener(opener)

            
    def __call__(self, ip_to_lookup):
        """
        Lookup the specified ip address and return a list of domains hosted there
        """
        #self.ip_to_lookup = ip_to_lookup
        
        ##Is the argument passed in an IP address or a hostname ?
        self.ip_to_lookup = self._check_ip(ip_to_lookup)
        if not self.ip_to_lookup:
            return []
        
        try:
            conn = urllib2.urlopen("http://%s/%s"%(self.domain, self.ip_to_lookup))
            data = conn.read()
            
            return self.parse_response(data)
        
        except (urllib2.HTTPError, urllib2.URLError), err:
            print "[-] Error in lookup: %s"%(err)
            return []
        
        
    def _check_ip(self, ip_to_lookup):
        """
        Check if passed string is ip or hostname and try and validate hostname
        returns a vlaidated ip string
        """
        try:
            socket.inet_aton(ip_to_lookup)
            return ip_to_lookup
        
        except socket.error:
            ##Doesn't look like an ip
            print "[!] Looking up IP address of %s"%(ip_to_lookup)
            
        try:
            ip_to_lookup = socket.gethostbyname_ex(ip_to_lookup)[-1][0]
            print "[!] IP address determined as %s"%(ip_to_lookup)
            return ip_to_lookup
        
        except socket.error:
            print "[-] Cannot lookup IP address for %s"%(ip_to_lookup)
            return ""
        
        
    def parse_response(self, data):
        """
        Parse out the domains we want from the page returned
        """
        #NASTY !!! - Need to do properly with BeautifulSoup or what not
        results = []
        
        ##Markers that contain the looked up domain
        tag = '<td><a href="'
        tag_len = len(tag)

        ##Marker to help us chop off a lot to parse
        start_pos = data.find("#FFFFFF")
        
        ##If we haven't found the start position then there were no results
        if start_pos == -1:
            print "[-] No results for %s found"%(self.ip_to_lookup)
            return results
        
        ##If we see this then we have hit the throttle limit & it wants a captch
        #TODO - pop the link in http://charting.webhosting.info/scripts/sec.php?<uuid> in the webbrowser ctrl and let the user post back the captcha
        throttle_tag = "Security Measure"
        
        if throttle_tag in data:
            print "[!] You have made too many requests, captcha required - do a search by hand to reset this. [http://whois.webhosting.info/%s] "%(self.ip_to_lookup)
            return results
        
        chunks = data[start_pos:].split("\n")
        for c in chunks:
            
            
            if c.startswith(tag):
                results.append(c[tag_len: tag_len+ c[tag_len:].find('">')].replace(self.domain,"").lower())
                
            elif c.startswith('<tr bgcolor="#C9C9C9">'):
                break
        #/NASTY---
            
        return results
        
        
if __name__ == "__main__":
    
    try:
        #PROXY = "webproxy-inet-auth.ms.com:8888"
        PROXY = None
        rl = ReverseLookup()
        
        ##Test with Hotmail.com ip - "64.4.20.186"
        for x in rl(sys.argv[1]):
            print x
            
    except KeyboardInterrupt:
        print "[!] Ctrl-C caught ...exiting"