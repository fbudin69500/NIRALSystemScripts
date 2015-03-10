#!/bin/env python
import urllib2
from urllib2 import HTTPError
import re
import subprocess
import os
import errno
import shutil
import argparse
import sys


parser = argparse.ArgumentParser(
prog=sys.argv[0],
description="This script downloads the nightly package of Slicer",
usage=sys.argv[0]+" [<args>]")
parser.add_argument("output_folder", help="Directory to install the nightly package")
args = parser.parse_args()
output_folder = args.output_folder
# Hard coded parameters
output_file_name = "/tmp/Slicer-nightly.tar.gz"
erase_older_nightly_slicer = True
# Tries to find URL to download Slicer nightly
download_page_url = 'http://download.slicer.org'
download_url = ''
# TO DO: improve search for URLs to work for Windows and MacOS
regexForLinux = 'nightly 64 bit archive'
try:
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0')]
    response = opener.open(download_page_url)
except HTTPError as e:
    content = e.read()
    print content
    exit(1)
finally:
    html = response.read()
try:
    # URL should match the RegEx pattern below for linux
    found = re.search('<a href="(.+?)" class="btn btn-warning">'+regexForLinux, html).group(1)
    # Creation of the "absolute URL"
    download_url = "http://download.slicer.org"+found
    print "URL to download Slicer nightly: "+download_url
except AttributeError:
    print "Did not find download URL"
    exit(1)

# Download Slicer
u = urllib2.urlopen(download_url)
f = open(output_file_name, 'wb')
meta = u.info()
file_size = int(meta.getheaders("Content-Length")[0])
print "Downloading in: %s (%s MBytes)" % (output_file_name, file_size/1024/1024)

file_size_dl = 0
block_sz = 8192
while True:
    buffer = u.read(block_sz)
    if not buffer:
         break

    file_size_dl += len(buffer)
    f.write(buffer)
    status = r"[%3.2f%%]" % (file_size_dl * 100. / file_size)
    # char(8) ->goes one character to the left without erase current character
    # This line allows to print the download progress allows at the same location of the terminal.
    status += chr(8)*(len(status)+1)
    print status,
f.close()
print " [done]  "
# Get Slicer directory
print "Looking for Slicer nightly directory name (exploring the archive)"
process = subprocess.Popen(["tar", "-tf", output_file_name], stdout=subprocess.PIPE)
output = process.communicate()[0]
process.wait()
current_nightly = re.search('(.+?)'+os.sep+'Slicer', output).group(1)
print "Directory found: "+current_nightly
try:
    os.makedirs(output_folder)
except OSError as exc:  # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(output_folder):
        pass
    else:
        raise
# Extracting Slicer archive
print "Extracting Slicer archive in "+output_folder
process = subprocess.Popen(["tar", "-xvzf", output_file_name, "-C", output_folder], stdout=subprocess.PIPE)
output = process.communicate()[0]
process.wait()
if erase_older_nightly_slicer:
    print "Removing previous nightly packages (from "+output_folder+")"
    list_previous_nightly = [p for p in os.listdir(output_folder) if p != current_nightly]
    for p in list_previous_nightly:
        old_nightly = os.path.join(output_folder, p)
        print "Removing: "+old_nightly
        try:
            shutil.rmtree(old_nightly)
        except OSError:
            print "Failed to remove "+old_nightly
            pass
if os.name == "posix":
    current_slicer_exec = os.path.join(output_folder, current_nightly, "Slicer")
    symlink_name = os.path.join(output_folder, "SlicerCurrentNightly")
    try:
        os.remove(symlink_name)
    except OSError:
        pass
    os.symlink(current_slicer_exec, symlink_name)