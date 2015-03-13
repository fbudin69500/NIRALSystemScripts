#!/bin/env python
from __future__ import print_function
import urllib2
from urllib2 import HTTPError
import re
import subprocess
import os
import errno
import shutil
import argparse
import sys
import tempfile
import platform

parser = argparse.ArgumentParser(
prog=sys.argv[0],
description="This script downloads the nightly package of Slicer",
usage=sys.argv[0]+" [<args>]")
parser.add_argument("output_folder", help="Directory to install the nightly package")
parser.add_argument("--log_file", help="File in which the log of the process will be stored")
parser.add_argument('--remove_older_nightly_slicer', action="store_true", default=False)
parser.add_argument('--keep_downloaded_archive', action="store_true", default=False)
args = parser.parse_args()
output_folder = args.output_folder
erase_older_nightly_slicer = args.remove_older_nightly_slicer
keep_downloaded_archive = args.keep_downloaded_archive
if args.log_file:
  try:
    log = open(args.log_file, 'w')
  except Exception as e:
    print(e)
    exit(1)
else:
  log = sys.stdout
# Tries to find URL to download Slicer nightly
download_page_url = 'http://download.slicer.org'
download_url = ''
# TO DO: improve search for URLs to work for Windows and MacOS
current_system = platform.system()
if(current_system == 'Linux'):
  regexForLinux = 'nightly 64 bit archive'
else:
  print("System detected:", current_system)
  print("System not yet supported")
  exit(1)
try:
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0')]
    response = opener.open(download_page_url)
except HTTPError as e:
    content = e.read()
    print(content,file=log)
    exit(1)
finally:
    html = response.read()
try:
    # URL should match the RegEx pattern below for linux
    found = re.search('<a href="(.+?)" class="btn btn-warning">'+regexForLinux, html).group(1)
    # Creation of the "absolute URL"
    download_url = "http://download.slicer.org"+found
    print("URL to download Slicer nightly:", download_url, file=log)
except AttributeError:
    print("Did not find download URL", file=log)
    exit(1)

# Download Slicer
u = urllib2.urlopen(download_url)
f = tempfile.NamedTemporaryFile('wb', suffix=".tar.gz", prefix='tmp_Slicer', delete=False)
tempFileName = f.name
meta = u.info()
file_size = int(meta.getheaders("Content-Length")[0])
print ("Downloading in : ", tempFileName," (", file_size/1024/1024,"MB)", sep="", file=log)

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
    print(status,end="",file=log)
f.close()
print(" [done]  ",file=log)
if erase_older_nightly_slicer:
    print("Removing previous nightly packages (from ",output_folder,")",sep="",file=log)
    list_previous_nightly = [p for p in os.listdir(output_folder) if p != "SlicerCurrentNightly" ]
    for p in list_previous_nightly:
        old_nightly = os.path.join(output_folder, p)
        print("Removing:",old_nightly,file=log)
        try:
            shutil.rmtree(old_nightly)
        except OSError:
            print("Failed to remove",old_nightly,file=log)
            pass
# Get Slicer directory
print("Looking for Slicer nightly directory name (exploring the archive)",file=log)
process = subprocess.Popen(["tar", "-tf", tempFileName], stdout=subprocess.PIPE)
output = process.communicate()[0]
process.wait()
current_nightly = re.search('(.+?)'+os.sep+'Slicer', output).group(1)
print("Directory found:",current_nightly,file=log)
try:
    os.makedirs(output_folder)
except OSError as exc:  # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(output_folder):
        pass
    else:
        raise
# Extracting Slicer archive
print("Extracting Slicer archive in",output_folder,file=log)
process = subprocess.Popen(["tar", "-xvzf", tempFileName, "-C", output_folder], stdout=subprocess.PIPE)
output = process.communicate()[0]
process.wait()
if os.name == "posix":
    current_slicer_exec = os.path.join(output_folder, current_nightly, "Slicer")
    symlink_name = os.path.join(output_folder, "SlicerCurrentNightly")
    try:
        os.remove(symlink_name)
        print("Old link removed",file=log)
    except OSError:
        pass
    os.symlink(current_slicer_exec, symlink_name)
    print("New link created",file=log)
if log is not sys.stdout:
  log.close()
# Remove temporary file
if not keep_downloaded_archive:
  os.remove(tempFileName)
