#!/usr/bin/env python2
"""
Dirwatcher exercise
Demonstrate long-running applications by monitoring text files in a directory
and scanning for a specified search text.
Users can use the command line options to specify the directory to monitor,
the extension type of files to monitor, the time interval between each scan,
and the text for which to scan('magic text').
"""
import time
import os
import argparse
import logging
from datetime import datetime as dt
import signal


__author__ = 'jontaylor224'


exit_flag = False
logger = logging.getLogger(__name__)

# keys are filenames, values are last line read
watched_files = {}

signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                if v.startswith('SIG') and not v.startswith('SIG_'))


def scan_single_file(filename, start_line, magic):
    '''Scan file for magic, starting at start_line'''
    line_num = 0
    with open(filename) as f:
        for line_num, line in enumerate(f):
            if line_num >= start_line:
                if magic in line:
                    logger.info('File={}: found text={} on line={}'
                                .format(filename, magic, line_num + 1))
    return line_num + 1


def watch_directory(path, ext, magic):
    '''Monitors the path directory for files with extension type ext
    containing magic text'''
    dir_files = os.listdir(path)

    # Check for new files
    for file in dir_files:
        if file.endswith(ext):
            if file not in watched_files:
                logger.info('Watching new file={}'.format(file))
                watched_files[file] = 1

    # Stop watching deleted files
    for file in watched_files.keys():
        if file not in dir_files:
            logger.info('Removed file={}'.format(file))
            watched_files.pop(file)

    # Scan watched files
    for f in watched_files:
        file_path = os.path.join(path, f)
        start_line = watched_files[f]
        watched_files[f] = scan_single_file(file_path, start_line, magic)


def create_parser():
    '''Returns a command line parser'''
    parser = argparse.ArgumentParser(
        description='Watches directory for target string in text files'
    )
    parser.add_argument('-e', '--ext', type=str, default='.txt',
                        help='Text file extension to monitor. eg. .txt, .log')
    parser.add_argument('-i', '--int', type=float, default=1.0,
                        help='Number of seconds of polling interval.')
    parser.add_argument('path', help='Directory to monitor.')
    parser.add_argument(
        'magic', help='Text string the program is seeking.')
    return parser


def signal_handler(sig_num, frame):
    """
   Handler for SIGTERM and SIGINT.
   Sets a global flag which will cause main() to exit its loop if either
   signal is trapped.
   :param sig_num: The integer signal number that was trapped from the OS.
   :param frame: Not used
   :return None
   """
    # log the signal name (the python2 way)
    logger.warn('Received OS Signal ' + signames[sig_num])
    global exit_flag
    exit_flag = True


def main():
    # Set up logger to print to console
    log_format = ('%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s'
                  '%(message)s')
    logging.basicConfig(
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger.setLevel(logging.DEBUG)

    # Set start time for running app
    app_start_time = dt.now()

    parser = create_parser()
    args = parser.parse_args()

    # Setup Startup Banner
    logger.info(
        '\n'
        '********************************************************\n'
        '   Running {0}\n'
        '   Started on {1}\n'
        '********************************************************\n'
        .format(__file__, app_start_time.isoformat())
    )

    # Hook these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info(
        'Watching dir={} for files with extension={} containing text={}'
        .format(args.path, args.ext, args.magic))
    while not exit_flag:
        try:
            # logger.debug('looping...')
            watch_directory(args.path, args.ext, args.magic)
        except OSError as e:
            logger.error("ERROR: {}".format(e))
        except Exception as e:
            logger.error("UNHANDLED EXCEPTION: {}".format(e))
            time.sleep(4)

        time.sleep(args.int)

    # Setup Shutdown Banner
    uptime = dt.now() - app_start_time
    logger.info(
        '\n'
        '********************************************************\n'
        '   Shutting down {0}\n'
        '   Uptime was {1}\n'
        '********************************************************\n'
        .format(__file__, str(uptime))
    )

    logging.shutdown()


if __name__ == '__main__':
    main()
