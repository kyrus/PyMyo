#!/usr/bin/python
"""
Usage: peekviewstate [ options ]

Options:

  -d : decode
  -h : this help
  -x : show hex bytes along with decode
  -u : provide url to look-up viewstate from
  -r : provide file with raw viewstate saved in it
  -f : provide file with html and viewstate still in it

Standard input is read for viewstate string for decoding by default.

(c) 2008 Adam Pridgen  <adam.pridgen@thecoverofnight.com>
         Aaron Rhodes

Special thanks to all those that help support the code.  While this is not
a finished product, it can be polished up for use in a sqlinjection tool,
web application scanner, etc.  Many of the objects layouts were identified 
by reverse engineering the types and serialized data directly from Visual Studio

version 0.01b

"""

#TODO Add a mechnism to track children of Pairs, Arrays, Triples, etc.
#TODO Add a data setter, where [data] is set in the list objects and the 
#     length is updated and along with type of array in some cases
#TODO Set-up accessors based on objects location in the viewstate and child-parent relationship
#TODO Default initialization for objects in the viewstate e.g. Declare an array and it is filled with A's
#TODO Research how to add serialized class/objects and see if it is possible to get 'data' to call
#     functions serialized in the class
#TODO Identify analysis methods/functions that can identify how the application is using data
#TODO Incorporate a Functional approach to declaring viewstate e.g.  
#     Viewstate(Pair(Int32(4),SystemString("foobar"))
#TODO Create a rapid encoding function that will encode all objects by their presumed spefied position,
#     or by their parent-child relationship
#TODO Implement functions that return data size or or the serialized object size 
#TODO Implement doc testing functionality
#TODO reverse engineer the double type
#TODO search and replace by object type and other features such as children or data values
#TODO create a quick function to serialize the view state and then encode it

import base64, getopt, os, sys, time, urllib2



VSTYPELOOKUP = {}
ASSEMBLYLOOKUP = {}

def buildtypelookup():
    module = sys.modules[globals()['__name__']]
    for name in dir(module): # introspect myself to look for things that have _header
        item = getattr(module,name) # get the thing
        if hasattr(item,"_header"):
            VSTYPELOOKUP[getattr(item,"_header")] = item
            VSTYPELOOKUP[name] = VSTYPELOOKUP[getattr(item,"_header")]
    #print VSTYPELOOKUP["\x0b\x2a"]

def buildassemblylookup():
    module = sys.modules[globals()['__name__']]
    for name in dir(module): # introspect myself to look for things that have _header
        item = getattr(module,name) # get the thing
        if hasattr(item,"_assembly_name"):
            ASSEMBLYLOOKUP[getattr(item,"_assembly_name")] = item

def getKlass(s, pos=0):
  klass = unknown
  increment = 1
  try:
    if s[pos] in VSTYPELOOKUP:
      klass, increment = VSTYPELOOKUP[s[pos]],1
    elif s[pos:pos+2] in VSTYPELOOKUP:
      klass, increment = VSTYPELOOKUP[s[pos:pos+2]],2
    elif s[pos:pos+3] in VSTYPELOOKUP:
      klass, increment = VSTYPELOOKUP[s[pos:pos+3]],3
  except:
      print "pos = %u and s = %s"%(pos, s)
      raise
  #print repr(s[pos]), pos, str(klass.__name__), increment
  return klass, increment


def rparsevalue(s, pos=0, has_hash=True):
    #print "Parse Value",repr(s[pos:pos+10]), pos
    #global OUTPUT
    klass, incr = getKlass(s, pos)
    byte = s[pos]
    if len(s) - pos <= 20 and has_hash:
      klass = ViewStateHash
    decoded   = '???'
    increment = 1
    k = unknown()
    if hasattr(klass,"rdecode"):
      k = klass()
      k.__name__ = klass.__name__
    decoded,increment = k.decode(s,pos)
    #print decoded
    return k,increment

def unpackage(string):
  s = urllib.unquote(string)
  s = base64.decodestring(s)
  return s

def package_with_string(data):
  s = b64encode(data)
  return urllib.quote_plus(s)

def package_with_list(data):
  s = b64encode_vs_list(data)
  return urllib.quote_plus(s)

def b64encode_vs_list(data):
  s = ''
  for i in data:
    s += i.rencode()
  return b64encode(s)

def b64encode_vs_str(data):
  return b64encode(data)


def b64encode(s):
  s = base64.encodestring(s)
  return "".join(s.split('\n'))

def insert_by_string(s, pos, data):
  t1 = s[:pos]
  t2 = s[pos:]
  return t1 + data + t2

def insert_by_object(s,pos,value):
  nv = value.encode()
  return insert_by_string(s, pos, nv)


def removedata(s, pos):
  data, incr = rparsevalue(s, pos)
  t1 = s[:pos]
  t2 = s[pos+incr:]
  return t1 + t2

def replace_by_string(s,pos,new_value):
  val, incr = rparsevalue(s, pos)
  t1 = s[:pos]
  t2 = s[pos+incr:]
  return t1+new_value+t2

def replace_by_object(s,pos,new_value):
  nv = new_value.encode()
  return replace_by_string(s, pos, nv)




def usage():
    sys.stdout.write( __doc__ )
    sys.exit()


def parse_single_value(s, pos=0, has_hash=False):
    #print "Parse Value",repr(s[pos:pos+10]), pos
    #global OUTPUT
    klass, incr = getKlass(s, pos)
    byte = s[pos]
    if len(s) - pos <= 20 and has_hash:
      klass = ViewStateHash
    decoded   = '???'
    increment = 1
    k = unknown()
    if hasattr(klass,"decode"):
      k = klass()
      k.__name__ = klass.__name__
    decoded,increment = k.decode(s,pos)
    #print decoded
    return k,increment

def parse(s,position=0, has_hash=True):
    pos = position
    global OUTPUT
    data = []
    while pos < len(s):
        byte = s[pos]
        k = None
        if byte == '\x0b': print "+++++++++++++++ ",s[pos:pos+2]
        if VSTYPELOOKUP.has_key(byte):
            klass = VSTYPELOOKUP[byte]
        elif VSTYPELOOKUP.has_key(s[pos:pos+2]):
            klass = VSTYPELOOKUP[s[pos:pos+2]]
        else:
            klass = unknown
        # we got a class, create an instance and use it for decode
        if len(s) - pos <= 20 and has_hash:
           klass = ViewStateHash
        decoded   = '???'
        increment = 1
        if hasattr(klass,"decode"):
           k = klass()
           decoded,increment = k.decode(s,pos)
           data.append(k)
           k.__name__ = klass.__name__
        #OUTPUT += '%04d:0x%02x:%08s:%24s:%s\n' % (pos,ord(byte), repr(byte), 
        #                                            klass.__name__, decoded)
        #print '%04d:0x%02x:%08s:%24s:%s\n' % (pos,ord(byte), repr(byte), 
        #                                            klass.__name__, decoded)
        pos = pos + increment
    out = ''
    #print data
    for i in data:
      #out += i.summary()
      out += i.__str__()+"\n"
    #print out
    return data,out

#vs = base64.decodestring("".join(open('/home/apridgen/workspace/peekviewstate/viewstate_search.txt').readlines()))
#OUT = ''

#def test():
  #global vs, OUT
  #objs, out = parse(vs)
  #for i in objs:
    ##print i.summary()
    #OUT += i.encode()

def split_webpage_data(webpage):
  viewstate_str = '<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="'
  return webpage.split(viewstate_str)[1].split('"')[0]

def get_vs_from_webpage(url):
  import urllib2
  d = urllib2.urlopen(url)
  return split_webpage_data("".join(d.readlines()))


# build a lookup table of header bytes from the class defs in vstypes
# to use when decoding the viewstate


def main():
    buildtypelookup()
    buildassemblylookup()
    vs_data = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hxu:l:r:", ["help", "hex", "url=","local_webpage", "raw_file"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    showhex = False
    for o, a in opts:
        if o in ("-x", "--hex"):
            showhex = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-u", "--url"):
            vs_data = get_vs_from_webpage(a)
        elif o in ("-l", "--local_webpage"):
            vs_data = split_webpage_data("".join(open(a).readlines()))
        elif o in ("-r", "--raw_file"):
            vs_data = "".join(open(a).readlines())
        else:
            assert False, "unhandled option"
    # read in viewstate to decode
    if vs_data is None:
      print "Please paste the ViewState into the terminal now and press Ctrl-D when done:\n"
      vs_data = sys.stdin.read()
    #raw = sys.stdin.read()
    vs  = base64.decodestring(vs_data)
    print repr(vs)
    # parse it 

    objects, out = parse(vs)

class utf16:
    _header = '\xff'
    def __init__(self):
      self.pos = -1
      self.data = '\xff'
    def decode(self,s,pos=0):
        self.pos = pos
        return str(self),1
    def rdecode(self, s, pos=0):
        return self.decode(s,pos)
    def encode(self):
        return self._header
    def rencode(self):
        return self.encode()
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def __str__(self):
      return 'UTF-16'
class ViewState:
    _header = '\x01'
    def __init__(self):
      self.pos = -1
      self.data = []
    def decode(self,s,pos=0):
        self.pos = pos
        self.data = None
        self.hash = None
        return str(self), 1
    def rdecode(self,s,pos=0):
        self.pos = pos
        self.data, increment = rparsevalue(s, pos+1)
        return str(self), increment
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def __str__(self):
      s = '<Viewstate>\n'
      #print self.data
      return s
      #if self.data:
      #  s+= "\t"+"\n\t".join(["%s"%str(i) for i in self.data])
      #return s
    def encode(self):
      return self._header
    def rencode(self):
      s = self._header
      if not self.data:
        return s
      for i in self.data:
        s+= i.rencode()
      if self.hash:
        s+= self.hash
      return s
    def sobj_size(self):
      return len(self.rencode())

class ViewStateHash:
    _header = ''
    def __init__(self):
      self.pos = -1
      self.data = ''
    def decode(self, s, pos):
      self.pos = pos
      self.data = s[pos:]
      return str(self), len(self.data)
    def rdecode(self, s, pos):
      self.decode(s,data)
    def __str__(self):
      return repr(self.data)[1:-1]
    def summary(self):
      return '%04d:    :%8s:%24s:%s\n' % (self.pos,self._header,  self.__name__, str(self))
    def encode(self):
      return self.data
    def rencode(self): return self.encode()
    def sobj_size(self):
      return len(self.rencode())

class SerializedClass:
    _header = '\x32'
    _unknown = '\x00\x01\x00\x00\x00\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00\x0c\x02\x00\x00\x00'
    '''
        size_field = max_len(base128Format(int))
        s[0] = Header
        s[1:size_field] = decodeint32(bytes) = size of assembly in bytes
        s[1+size_field:size_field+23] = unknown
        s[25] = Assembly Name and PublicKeyToken size
        s[1+size_field:size_field+23] = Assembly Name and PublicKeyToken
        s[pos+offsetof_alloftheabove:pos+size+data_offset]
    '''
    def __init__(self):
      self.pos = -1
      self.size = 0
      self.data = []
      self.name = ''
    def decode(self, s, pos=0):
      self.pos = pos
      increment = 1
      data_offset = 0
      self.size, incr = decodeint32(s, pos+increment)
      data_offset = 1 + incr # data size
      increment += incr
      unknown = s[pos+increment:pos+increment+len(self._unknown)]
      increment += len(self._unknown)
      for i in xrange(0, len(self._unknown)):
        if unknown[i] != self._unknown[i]:
          print "Unknown string differs @ %d Known Value = %s VS Value = %s"%(i, repr(unknown[i]), repr(self._unknown[i]))
      self.name, incr = decodestring(s,pos+increment)
      increment += incr
      self.data = s[pos+increment:pos+self.size+data_offset]
      return str(self), self.size+data_offset
    def rdecode(self, s, pos=0): return self.decode(s, pos)
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def __str__(self):
       return "<SerializedClass %s %3d> Data:%s"%(self.name, self.size, repr(self.data))
    def encode(self):
      s = self._header
      s+= encodeint(self.size)
      s+= self._unknown
      s+= encodestring(self.name)
      s+= self.data
      return s
    def rencode(self): return self.encode()
    def sobj_size(self):
      return len(self.rencode())

class ClassType:
    _header = '\x28'
    def __init__(self):
      self.pos = -1
      self.size = 0
      self.data = []
      self.name = ''
    def decode(self, s, pos):
      self.pos = pos
      self.name = ''
      self.data = None
      increment = 0
      klass = unknown
      if s[pos+1] == '\x29':
        self.name, incr= decodestring(s, pos+1)
        if ASSEMBLYLOOKUP.has_key(self.name):
            klass = ASSEMBLYLOOKUP[self.name]
        increment += incr + 1
      t = klass()
      decode, incr = t.decode(s,pos+increment)
      increment += incr
      self.data = t
      return str(self), increment
    def rdecode(self, s, pos): return self.decode(s, pos)
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def __str__(self):
      return "<ClassType:%s>Data: %s"%(self.name, str(self.data))
    def encode(self):
      s = self._header
      if self.name != '':
        s+= '\x29'
        s+= encodestring(self.name)
      s+=self.data.encode()
      return s
    def rencode(self):
      s = self._header
      if self.name != '':
        s+= '\x29'
        s+= encodestring(self.name)
      s += self.data.rencode()
      return s
    def sobj_size(self):
      return len(self.rencode())

class Double:
    _header = '\x07'
    def __init__(self):
      self.pos = -1
      self.data = []
    def decode(self, s, pos):
      self.pos = pos
      self.data, incr = decodedouble(s, pos+1)
      return str(self),incr+1
    def rdecode(self, s, pos): self.decode(s, pos)
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def __str__(self):
      return repr(self.data)[1:-1]
    def encode(self):
      s = self._header
      s+= self.data
      return s
    def rencode(self): return self.encode()
    def sobj_size(self):
      return len(self.rencode())

class Int64:
    _assembly_name = 'System.Int64, mscorlib, Version=2.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089'
    _header = '\x28\x2b\x04'
    def __init__(self):
      self.pos = -1
      self.data = []
    def decode(self, s, pos):
      self.pos = pos
      self.data, increment = decodeint64(s, pos+len(self._assembly_name))
      return str(self), increment+1
    def rdecode(self, s, pos): return self.decode(s, pos)
    def __str__(self):
      return "<Int64 %l>"%(self._assembly_name, self.data)
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def encode(self):
      s = ''
      s+= self._header
      s+= encodestring(str(self.data))
      return s
    def rencode(self): return self.encode()
    def sobj_size(self):
      return len(self.rencode())

class SystemStringArray:
    _header = '\x15'
    def __init__(self):
      self.pos = -1
      self.size = 0
      self.data = []
    def decode(self, s, pos): return self.rdecode(s, pos)
    def rdecode(self, s, pos):
      self.pos = pos
      increment = 1
      self.size, t_increment = decodeint32(s, pos+increment)
      increment+=t_increment
      self.data, t_increment = decodestringarray(s, pos+increment, self.size)
      return str(self), increment+t_increment
    def summary(self):
      data = "\n ".join([i for i in self.data])
      return '%04d:0x%02x:%08s:%24s:<%03d>\n%s' % (self.pos,ord(self._header), repr(self._header), self.__name__, self.size, data+'\n')
    def __str__(self):
      name = 'SystemStringArray'
      s = "<%s:%03d>"%(name, self.size)
      if self.data:
        s+= "\n\t"+"\n\t".join(["%s"%i for i in self.data])
      return s
    def rencode(self):
      s = self._header
      s+= encodeint(self.size)
      #for i in self.data:
      #  print repr(i)
      s+= encodestringarray(self.data)
      return s
    def encode(self): return self.rencode()
    def sobj_size(self):
      return len(self.rencode())

class HybridDictionary:
    _header = '\x18'
    def decode(self, s, pos):
      self.pos = pos
      increment = 1
      self.size, incr = decodeint32(s, pos+1)
      #print "inside dictionary", incr, pos, self.size
      increment += incr
      self.data, incr = decodedictionary(s, pos+increment, self.size)
      increment += incr
      return str(self), increment
    def rdecode(self, s, pos):
      return self.decode(s, pos)
    def summarize_data(self):
      if not self.data: return ''
      key = self.data.keys()
      if len(key) == 0: return ''
      data_sum = '' 
      for k in key:
        d = ''
        if hasattr(k,"summary"): 
          d += '\tKey:: '+k.summary() 
        else:
          d += '\tKey: '+k
        d += '\n'
        if hasattr(self.data[k][0],"summary"): 
          x = self.data[k][0].summary().split('\n')
          d += '\tValue:\n\t\t'+"\n\t\t".join(x)
        else:
          d += '\tValue:\n\t\t'+self.data[k][0] + '\n'
        data_sum += d
      return data_sum
    def summary(self):
      data = self.summarize_data()
      return '%04d:0x%02x:%08s:%24s:<%03d>\n%s' % (self.pos,ord(self._header), repr(self._header), self.__name__, self.size, data)
    def __str__(self):
      name = 'HybridDictionary'
      s = "<%s:%03d>\n"%(name, self.size)
      if self.data:
        for item in self.data:
          k = "<Key>: %s\n"%(str(item))
          v = "<Values>: %s\n"%(str(self.data[str(item)][0]))
          s+= k+v
      return s
    def rencode(self):
      s = self._header
      s += encodeint(self.size)
      s += encodedictionary(self.data)
      return s
    def encode(self): return self.rencode()
    def sobj_size(self):
      return len(self.rencode())

class FullArray:
    _header = '\x14'
    _types = {'\x2b\x01':"Int32", 
              '\x2b\x02':"String",
              '\x2b\x03':"Boolean",
              '\x29':"ClassType", 
              '\x2b\x00':"Objects"
            }
    types_names = {"Int32":'\x2b\x01', 
              "String":'\x2b\x02',
              "Boolean":'\x2b\x03',
              "ClassType":'\x29',
              "Objects":'\x2b\x00'
            }
    def __init__(self):
      self.pos = -1
      self.size = 0
      self.array_type = ""
      self.data = []
      self.classname = ''
    def decode(self, s, pos=0):
      return self.rdecode(s, pos)
    def rdecode(self, s, pos):
      self.pos = pos
      increment = 1
      self.size = 0
      self.array_type = ""
      self.data = []
      self.classname = ''
      if s[pos+1] in self._types:
        self.array_type = s[pos+increment]
        increment += 1
        self.classname, t_increment = decodestring(s, pos+increment)
        increment+= t_increment
      elif s[pos+1:pos+3] in self._types:
        self.array_type = s[pos+increment:pos+3]
        increment+= 2
      else:
        self.array_type = s[pos:pos+100]
        self.classname = '????'
        self.size = 0
        return str(self), 1
      self.size, t_increment = decodeint32(s, pos+increment)
      increment+= t_increment
      self.data, t_increment = decodearray(s, pos+increment, self.size)
      return str(self), increment+t_increment
    def __str__(self):
      name = ''
      if self.array_type in self._types:
        name = self._types[self.array_type]
      else:
        name = repr(self.array_type)
      if self.classname != '':
        name += ":"+self.classname
      s = "<Full Array %s:%03d>"%(name, self.size)
      if self.data:
        s+= "\n\t"+"\n\t".join(["%s"%str(i) for i in self.data])
      return s
    def summarize_data(self):
      if not self.data: return ''
      d = ''
      for i in self.data:
        if hasattr(i,"summary"): 
          d += i.summary()
        else: d+= i+'\n'
      return d
    def summary(self):
      data = self.summarize_data()
      return '%04d:0x%02x:%08s:%24s:<%03d>\n%s' % (self.pos,ord(self._header), repr(self._header), self.__name__, self.size, data)
    def rencode(self):
      s = self._header
      if self.classname == "????": return s
      s += self.array_type
      s += encodeint(self.size)
      s += encodearray(self.data)
      return s
    def encode(self):  return self.rencode()
    def sobj_size(self):
      return len(self.rencode())

class IndexedArray:
    _header = '\x3c'
    _types = {'\x2b\x01':"Int32", 
              '\x2b\x02':"String",
              '\x2b\x03':"Boolean",
              '\x29':"ClassType", 
              '\x2b\x00':"Objects"
            }
    types_names = {"Int32":'\x2b\x01', 
              "String":'\x2b\x02',
              "Boolean":'\x2b\x03',
              "ClassType":'\x29',
              "Objects":'\x2b\x00'
            }
    def __init__(self):
      self.pos = -1
      self.size = 0
      self.array_type = ""
      self.data = []
      self.classname = ''
    def rdecode(self, s, pos):
      self.pos = pos
      increment = 1
      self.size = 0
      self.ndx_cnt = 0
      self.array_type = ""
      self.data = []
      self.classname = ''
      #TODO there might be a bug here, because
      # I have not encountered user defined classes in an 
      # array of any sort :(
      if s[pos+1] in self._types:
        self.array_type = s[pos+1]
        increment += 1
        self.classname, t_increment = decodestring(s, pos+increment)
        increment+= t_increment
      elif s[pos+1:pos+3] in self._types:
        self.array_type = s[pos+1:pos+3]
        increment += 2
      else:
        self.array_type = s[pos:pos+100]
        self.classname = '????'
        self.ndx_cnt = 0
        self.size = 0
        return str(self), 1
        #wild guess :(
      self.size, t_increment = decodeint32(s, pos+increment)
      increment+= t_increment
      self.ndx_cnt, t_increment = decodeint32(s, pos+increment)
      increment+= t_increment
      self.data, t_increment = decodeindexedarray(s, pos+increment, self.ndx_cnt)
      return str(self), increment+t_increment
    def decode(self, s, pos): return self.rdecode(s, pos)
    def __str__(self):
      name = ''
      if self.array_type in self._types:
        name = self._types[self.array_type]
      else:
        name = repr(self.array_type)
      if self.classname != '':
        name += ":"+self.classname
      s = "<Indexed Array %s:%03d Index Count:%03d>\n"%(name, self.size, self.ndx_cnt)
      s+= "\t"+"\n\t".join(["Index:%03d %s"%(self.data[i][0], str(self.data[i][1])) for i in xrange(0, len(self.data)) if self.data[i]])
      return s+'\n'
    def summarize_data(self):
      if not self.data: return ''
      d = ''
      for i in self.data:
        if hasattr(i,"summary"): 
          d += i.summary()
        else: d+= i+'\n'
      return d
    def summary(self):
      data = self.summarize_data()
      return '%04d:0x%02x:%08s:%24s:<%03d>\n%s' % (self.pos,ord(self._header), repr(self._header), self.__name__, self.size, data)
    def rencode(self):
      s = self._header
      if self.classname == "????": return s
      s += self.array_type
      s += encodeint(self.size)
      s += encodeint(self.ndx_cnt)
      s += encodeindexedarray(self.data)
      return s
    def encode(self):  return self.rencode()
    def sobj_size(self):
      return len(self.rencode())

class Pair:
    _header = '\x0f'
    def __init__(self):
      self.pos = -1
      self.size = 2
      self.data = []
    def decode(self,s,pos=0):  
      #self.data = None
      #return str(self), 1
      return self.rdecode(s, pos)
    def rdecode(self,s,pos=0):
        self.pos = pos
        # TODO add a variable to check the number of children
        self.size = 2
        self.data, increment = decodearray(s, pos+1, 2)
        return str(self),increment+1
    def __str__(self):
      s = "<Pair>"
      if self.data:
        s+= "\n\t"+"\n\t".join(["%s"%str(i) for i in self.data])
      return s
    def summarize_data(self):
      if not self.data: return ''
      d = ''
      for i in self.data:
        if hasattr(i,"summary"): 
          d += i.summary()
        else: d+= i+'\n'
      return d
    def summary(self):
      data = self.summarize_data()
      return '%04d:0x%02x:%08s:%24s:<%03d>\n%s' % (self.pos,ord(self._header), repr(self._header), self.__name__, self.size, data)
    def rencode(self):
      s = self._header
      if self.data:
        s += encodearray(self.data)
      return s
    def encode(self): return self.rencode()
    def sobj_size(self):
      return len(self.rencode())

class Triple:
    _header = '\x10'
    def __init__(self):
      self.pos = -1
      self.size = 3
      self.data = []
    def decode(self,s,pos=0):  
      #self.data = None
      #return str(self), 1
      return self.rdecode(s, pos)
    def rdecode(self,s,pos=0):
        self.pos = pos
        self.data, increment = decodearray(s, pos+1, 3)
        self.size = 3
        return str(self),increment+1
    def __str__(self):
      s = "<Triple>"
      if self.data:
        s+= "\n\t"+"\n\t".join(["%s"%str(i) for i in self.data])
      return s
    def summarize_data(self):
      if not self.data: return ''
      d = ''
      for i in self.data:
        if hasattr(i,"summary"): 
          d += i.summary()
        else: d+= i+'\n'
      return d
    def summary(self):
      data = self.summarize_data()
      return '%04d:0x%02x:%08s:%24s:<%03d>\n%s' % (self.pos,ord(self._header), repr(self._header), self.__name__, self.size, data)
    def rencode(self):
      s = self._header
      if self.data:
        s += encodearray(self.data)
      return s
    def encode(self): return self.rencode()
    def sobj_size(self):
      return len(self.rencode())

class SystemString:
    _header = '\x05'
    def __init__(self):
      self.pos = -1
      self.data = ''
    def decode(self,s,pos=0):
        self.pos = pos
        self.data, increment = decodestring(s,pos+1)
        return str(self), increment+1
    def rdecode(self, s, pos): return self.decode(s, pos)
    def __str__(self):
        return "<%03d>%s"%(len(self.data),self.data)
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def encode(self): 
      return self._header + encodestring(self.data)
    def rencode(self): return self.encode()
    def sobj_size(self):
      return len(self.rencode())

class SystemWebString:
    _header = '\x0b\x2a'
    def __init__(self):
      self.pos = -1
      self.data = ''
    def decode(self,s,pos=0):
        self.pos = pos
        self.data, increment = decodestring(s,pos+2)
        return str(self), increment+2
    def rdecode(self, s, pos): return self.decode(s, pos)
    def __str__(self):
        return "<%03d>%s"%(len(self.data),self.data)
    def summary(self):
      return '%04d:0x%s:%08s:%24s:%s\n' % (self.pos,"".join(["%x"%ord( i ) for i in self._header]), repr(self._header), self.__name__, str(self))
    def encode(self): 
      return self._header + encodestring(self.data)
    def rencode(self): return self.encode()
    def sobj_size(self):
      return len(self.rencode())

class SystemWebUiIndexedString:
    _header = '\x1e'
    def __init__(self):
      self.pos = -1
      self.data = ''
    def decode(self,s,pos=0):
        self.pos = pos
        self.data, increment = decodestring(s,pos+1)
        return str(self), increment+1
    def rdecode(self, s, pos): return self.decode(s, pos)
    def __str__(self):
        return "<%03d>%s"%(len(self.data),self.data)
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def encode(self): 
      return self._header + encodestring(self.data)
    def rencode(self): return self.encode()
    def sobj_size(self):
      return len(self.rencode())

class SystemWebUiIndexedString_Char:
    _header = '\x1f'
    def __init__(self):
      self.pos = -1
      self.data = ''
    def decode(self,s,pos=0):
        self.pos = pos
        self.data = s[pos+1]
        return str(self), 2
    def rdecode(self, s, pos): return self.decode(s, pos)
    def __str__(self):
        return "<%03d>%s"%(len(self.data),repr(self.data)[1:-1])
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def encode(self): 
      print '''SystemWebUiIndexedString_Char:  Encode may be off, because we believe these 
               are char values and so we only consider the first byte.'''
      return self._header + self.data
    def rencode(self): return self.encode()
    def sobj_size(self):
      return len(self.rencode())

class ArrayList:
    _header = '\x16'
    def __init__(self):
      self.pos = -1
      self.size = 0
      self.data = []
    def decode(self,s,pos=0):
        #self.pos = pos
        #self.size, sz_incr = decodeint32(s, pos+1)
        #self.data=None
        #return str(self),sz_incr+1
        return self.rdecode(s,pos)
    def rdecode(self, s, pos):
        self.pos = pos
        self.size, sz_incr = decodeint32(s, pos+1)
        #print 'ArrayList rdecode + 2 lines'
        #print self.size, pos, sz_incr
        #print repr(s[pos:pos+20])
        #print self.size
        self.data, cnt_incr = decodearray(s, pos+sz_incr+1, self.size)
        #print len(self.data)
        return str(self),cnt_incr+sz_incr+1
    def __str__(self):
      s = "<ArrayList:%03d>\n"%self.size
      if self.data:
        s+= "\t\t"+"\n\t\t".join(["%s"%str(i) for i in self.data])
      return s
    def summarize_data(self):
      if not self.data: return ''
      d = ''
      for i in self.data:
        if hasattr(i,"summary"): 
          d += i.summary()
        else: d+= i+'\n'
      return d
    def summary(self):
      data = self.summarize_data()
      return '%04d:0x%02x:%08s:%24s:<%03d>\n%s' % (self.pos,ord(self._header), repr(self._header), self.__name__, self.size, data)
    def encode(self): 
      s = self._header
      s += encodeint(self.size)
      return s
    def rencode(self):
      s = self._header
      s += encodeint(self.size)
      if self.data:
        s += encodearray(self.data)
      return s
    def sobj_size(self):
      return len(self.rencode())

class NULL:
    _header = '\x64'
    def __init__(self):
      self.pos = -1
      self.data = "NULL"
    def decode(self,s,pos=0):
        self.pos = pos
        self.data = "NULL"
        return str(self),1
    def rdecode(self, s, pos): return self.decode(s, pos)
    def __str__(self):
        return '<NULL>'
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def encode(self):
      return self._header
    def rencode(self):
      return self._header
    def sobj_size(self):
      return len(self.rencode())

class IntZero:
    _header = '\x66'
    def __init__(self):
      self.pos = -1
      self.size = 0
      self.data = 0
    def decode(self,s,pos=0):
        self.data = 0
        self.pos = pos
        return str(self),1
    def rdecode(self, s, pos): return self.decode(s, pos)
    def __str__(self):
        return "<Zero %s>"%(self.data)
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def encode(self):
      return self._header
    def rencode(self):
      return self._header
    def sobj_size(self):
      return len(self.rencode())

class BooleanTrue:
    _header = '\x67'
    def __init__(self):
      self.pos = -1
      self.data = True
    def decode(self,s,pos=0):
        self.pos = pos
        self.data = True
        return str(self), 1
    def rdecode(self, s, pos): return self.decode(s, pos)
    def __str__(self):
        return "<Boolean %s>"%(self.data)
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def encode(self):
      return self._header
    def rencode(self):
      return self.encode()
    def sobj_size(self):
      return len(self.rencode())

class BooleanFalse:
    _header = '\x68'
    def __init__(self):
      self.pos = -1
      self.data = False
    def decode(self,s,pos=0):
        self.pos = pos
        self.data = False
        return str(self), 1
    def rdecode(self, s, pos): return self.decode(s, pos)
    def __str__(self):
        return "<Boolean %s>"%(str(self.data))
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def encode(self):
      return self._header
    def rencode(self):
      return self.encode()
    def sobj_size(self):
      return len(self.rencode())

class Int32:
    _header = '\x02'
    def __init__(self):
      self.pos = -1
      self.data = 0
    def decode(self,s,pos=0):
        self.pos = pos
        self.data, increment = decodeint32(s,pos+1)
        self.data = ConvertToSignedValue(self.data)
        return str(self), increment+1
    def rdecode(self, s, pos): return self.decode(s, pos)
    def __str__(self):
        return "<Int32 %s>"%(int(self.data))
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def encode(self):
      return self._header+encodeint(self.data)
    def rencode(self):
      return self.encode()
    def sobj_size(self):
      return len(self.rencode())

class unknown:
    def decode(self,s,pos=0):
         self.pos = pos
         self.name = "????"
         self.data = s[pos]
         self._header = s[pos]
         return str(self),1 
    def rdecode(self, s, pos): return self.decode(s, pos)
    def __str__(self):
        return "Type: %s Value:%s"%(self.name, repr(self.data)[1:-1])
    def summary(self):
      return '%04d:0x%02x:%08s:%24s:%s\n' % (self.pos,ord(self._header), repr(self._header), self.__name__, str(self))
    def encode(self):
      return self.data
    def rencode(self):
      return self.data
    def sobj_size(self):
      return len(self.rencode())

def decodedictionary(s, pos=0, items=0):
  itm_cnt = 0
  data = {}
  byte_incr = 0
  while itm_cnt < items:
    key, incr = rparsevalue(s, pos+byte_incr)
    byte_incr += incr
    #print str(key), byte_incr, pos
    value, incr = rparsevalue(s, pos+byte_incr)
    #print str(value), byte_incr, pos
    #print value.summary()
    data[str(key)] = (value, key)
    byte_incr+= incr
    itm_cnt+=1
  return data, byte_incr

def encodedictionary(d):
  s = ''
  keys = d.keys()
  for i in keys:
    pair = d[i]
    s += pair[1].rencode()
    s += pair[0].rencode()
  return s

def encodevalue(val):
  return val.rencode()

def decodestringarray(s, pos=0, sz=0):
  byte_incr = 0
  elm_cnt = 0
  data = []
  while elm_cnt < sz:
    string, incr = decodestring(s, pos+byte_incr)
    data.append(string)
    byte_incr+= incr
    elm_cnt+=1
  return data, byte_incr

def encodestringarray(array):
  s = ''
  #print array
  for i in array:
    k = encodestring(i)
    s+= k
    #print repr(k)
  return s

def decodeindexedarray(s, pos=0, ndx_cnt=0):
    elm_cnt = 0
    byte_incr = 0
    data = []
    while elm_cnt < ndx_cnt:
      ndx, incr = decodeint32(s, pos+byte_incr)
      byte_incr += incr
      #klass,incr = getKlass(s, pos+byte_incr)
      #d = klass()
      decode, incr = rparsevalue(s, pos+byte_incr)
      byte_incr += incr
      data.append((ndx,d))
      #print ndx, str(d), byte_incr, incr
      elm_cnt += 1
    return data, byte_incr

def encodeindexedarray(array):
  s = ''
  for i in array:
    s += encodestring(str(i[0])) # encode the index value
    s += i[1].encodevalue()
  return s

def decodearray(s, pos=0, ary_sz=0):
    elm_cnt = 0
    byte_incr = 0
    data = []
    #print "Inside decode array"
    #print "array size, pos",ary_sz, pos
    while elm_cnt < ary_sz:
      #klass, incr = getKlass(s, pos+byte_incr)
      #d = klass()
      #print klass.__name__
      #decode, incr = d.rdecode(s, pos+byte_incr)
      d, incr = rparsevalue(s, pos+byte_incr)
      #print decode, incr
      byte_incr += incr
      data.append(d)
      elm_cnt += 1
    return data, byte_incr

def encodearray(array):
  s = ""
  for i in array:
    s += i.rencode()
  return s

def encodestring(string):
  size = encodeint(len(string))
  #print size,string
  return size+string

def decodestring(s,pos=0):
    s = s[pos:]
    length, increment = decodeint32(s,0) # first byte is how long the string is
    data    = repr(s[1:length+1])[1:-1] #take off the stupid quotes
    return data,length + increment 

def decodeint32(string, pos=0):
  # collect the Int32 byte string
  string = string[pos:]
  int_str = ''
  for i in string:
    v = ord(i)
    int_str += chr(v)
    if v < 0x80:
      break;
  #print repr(int_str)
  #print repr(string[:10])
  #time.sleep(10)
  intVal = decodeint(int_str)
  return intVal, len(int_str)

def encodeint(dec):
  '''
      Converts the int value into a base 128 .Net string
      Test values used:
          1800355996 == \x9c\x81\xbd\xda\x06
          155 == \0x9b\x01
          16383 == \xff\x7f
          16384 == \x80\x80\x01 (128^2)
          128 == \x80\x01 (128^1)
          0 == \x00 (128^0)
          1024 == \x80\x08
          2048 == \x80\x10
          4096 == \x80\x20
          65538== \x80\x80\x04
      268435456== \x80\x80\x80\x80\x01 (128^4)
  '''
  #print dec
  r = dec % 0x80
  d = (dec // 0x80)
  if dec == 0:
      return "\x66"
  elif (dec-r) == 0:
      return chr(0x80+r)
  elif ((dec-r)- (0x80 * d)) == 0 and d < 0x80:
      return chr(0x80+r)+chr(d)
  #elif d&(~0xff) >= 0x80:
  #    print hex(d), " ", hex(dec), " ", 0x80*(d&0xff), " ", dec-0x80*(d&0xff)
  #    return chr(0x80+r)+chr(0x80+d&0xff)+encodeint((dec-r)-0x80*(d&0xff))
  elif d < 0x80:
      #print hex(d), " ", hex(dec), " ", 0x80*(d&0xff), " ", dec-0x80*(d&0xff)
      return chr(0x80+r)+chr(d)+encodeint((dec-r)-0x80*d)
  else:
      #print hex(d), " ", hex(dec), " ", 0x80*(d&0xff), " ", dec-0x80*(d&0xff)
      return chr(0x80+r)+encodeint((dec-r)/0x80)



def ConvertToSignedValue(val):
  if val > 2147483647: return val + (2*-2147483648)
  return val

def ConvertToUnsignedValue(val):
  if val < 0: return val + (2*+2147483648)
  return val

def decodeint(int_str):
  '''
    Expected int_strue is a char buffer.
  '''
  result = 0
  j = 0 
  i = 0
  l = len(int_str)
  #print len(int_str), repr(int_str)
  if ord(int_str[0]) < 0x80: return ord(int_str[0])
  while i < l:
    g = ord(int_str[i])
    if g >= 0x80:
      #print "Value is greater than 128: %x - 0x80 = %x"%(g, g-0x80)
      g = g - 0x80
    m = (0x80 ** j) * (g)
    #print "%x = (0x80 ** %x) * (%x)"%(m,j,g), ord(int_str[i])
    result = result + m
    i += 1
    j += 1
  return result

def decodeint64(s, pos=0):
    length  = int(ord(s[pos])) # first byte is how long the string is
    int64    = long(s[pos+1:pos+length+1])
    return decode, length+1

def encodeint64(val):
  return encodestring(val)

def decodedouble(s, pos=0):
  dbl = s[pos:pos+8]
  #TODO Identify how to convert doubles
  return dbl, 8

def encodedouble(dbl):
  #TODO firgure out how to encode after figuring out how to decode
  return dbl


if __name__ == "__main__":
    main()
else:
    buildtypelookup()
    buildassemblylookup()

