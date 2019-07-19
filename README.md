# Dirwatcher

This program monitors a directory, checking whether text files in the directory contain a particular word.

## Usage
The user can call this program from the command line with several parameters:
-e, --ext: extension of text files to watch. eg. .txt, .log
-i, --int: time interval between each scan in seconds
dir: directory to monitor
magic: word  for which to search in each text file

eg.  python2 dirwatcher.py --ext .log --int 2 logdirectory testphrase


