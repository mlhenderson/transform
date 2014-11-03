#!/usr/bin/python
import argparse
import sys
import os
import time
import traceback
import sys
import ctypes
import subprocess
from subprocess import Popen, PIPE
import shutil
from optparse import OptionParser
from biokbase.workspace.client import Workspace
import urllib
import urllib2
import re
import json

desc1 = '''
NAME
      trns_validate_KBaseGenomes.GBK -- convert CSV format to Pair for Transform module (version 1.0)

SYNOPSIS      
      
'''

desc2 = '''
DESCRIPTION
  trns_validate_KBaseGenomes.GBK convert input GBK (GenBank) format to KBaseGenomes.Genome
  json string file for KBaseGenomes module.

  TODO: It will support KBase log format.
'''

desc3 = '''
EXAMPLES
      CSV conversion case
      > trns_validate_KBaseGenomes.GBK -i input_file.csv -o ouput_file.json
      
SEE ALSO
      trns_transform_hndlr

AUTHORS
First Last.
'''

impt = "$KB_TOP/lib/jars/kbase/genomes/kbase-genomes-20140411.jar:$KB_TOP/lib/jars/kbase/common/kbase-common-0.0.6.jar:$KB_TOP/lib/jars/jackson/jackson-annotations-2.2.3.jar:$KB_TOP/lib/jars/jackson/jackson-core-2.2.3.jar:$KB_TOP/lib/jars/jackson/jackson-databind-2.2.3.jar:$KB_TOP/lib/jars/kbase/transform/GenBankTransform.jar"

mc = 'us.kbase.genbank.test.CommandLineTest'

def transform (args) :
#    try:
      kb_top = os.environ.get('KB_TOP', '/kb/deployment')
      cp = impt.replace('$KB_TOP', kb_top);


      in_dir = re.sub(r'/[^/]*$','', args.in_file)

      tcmd_lst = ['java', '-cp', cp, mc, in_dir]

      p1 = Popen(tcmd_lst, stdout=PIPE)
      out_str = p1.communicate()

      # print output message for error tracking
      if out_str[0] is not None : print out_str[0]
      if out_str[1] is not None : print >> sys.stderr, out_str[1]
     
     
      if p1.returncode != 0: 
          exit(p1.returncode) 

#    except:
#      raise Exception("Error writing to {}".format(args.out_file))

if __name__ == "__main__":
    # Parse options.
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, prog='trns_validate_KBaseGenomes.GBK', epilog=desc3)
    parser.add_argument('-i', '--in_file', help='Input file', action='store', dest='in_file', default=None, required=True)
    usage = parser.format_usage()
    parser.description = desc1 + '      ' + usage + desc2
    parser.usage = argparse.SUPPRESS
    args = parser.parse_args()

    # main loop
    if not args.in_file.endswith(".gbk"):
      in_file = "{}.gbk".format(args.in_file)
      shutil.copy(args.in_file, in_file)
      args.in_file = in_file
    transform(args)
    exit(0);
