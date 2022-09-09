#! /usr/bin/env python

"""
Palo Alto Networks
Generate traffic for lab environments
mkorenbaum@paloaltonetworks.com
"""

import requests
import time
import random
import argparse
import getpass
import json
import logging
from logging.handlers import RotatingFileHandler
import datetime
import os
import sys
import urllib3

urllib3.disable_warnings()
# Global Vars

timer = 10800
SCRIPT_NAME = "SASE Demo Traffic Generator"
TIME_BETWEEN_REQUESTS = 5
MY_LOG_FILE = "sase-traffic-log.txt"

if not os.path.exists(MY_LOG_FILE):
    with open(MY_LOG_FILE, 'w') as fp:
        fp.write("Creating SASE Traffic Generator Log File \n")
        pass


#function to read a file of hostnames separated by carriage returns
def readFile(fileName):
    fileObj = open(fileName, "r")  # opens the file in read mode
    words = fileObj.read().splitlines()  # puts the file into an array
    fileObj.close()
    return words

# function to grab random entry from a list
def getRandomUrl(mylist):
    return mylist[random.randrange(0, len(mylist) - 1)]


# build dictionary where key = protocol_host and backoff value is t in seconds
# check to see if this URL is backed off
def isBackedoff(key, db):
    try:
        if db[key] is None:
            return False
    except:
        return False

    return (time.time() < db[key])


def go():
    ############################################################################
    # Begin Script, parse arguments.
    ############################################################################
    BACKOFF_DB = {}

    # Parse arguments
    parser = argparse.ArgumentParser(description="{0}.".format(SCRIPT_NAME))


    # Specify domain list file and other optional arguments
    options = parser.add_argument_group('Options')
    options.add_argument("--domains", "-d",
                                  help="List of hosts with /r as delimeter, ex. C:/Users/Admin/Desktop/appdomain.txt", required=True,
                                  default=None)

    options.add_argument("--insecure", "-I", help="Disable SSL certificate and hostname verification",
                                  dest='verify', action='store_false', default=True)

    debug_group = parser.add_argument_group('Debug', 'These options enable debugging output')
    debug_group.add_argument("--debug", "-D", help="Print Debug info to stdout", action='store_true')

    args = vars(parser.parse_args())


    ############################################################################
    # End Login handling, begin script..
    ############################################################################

    # Set NON-SYSLOG logging to use function name
    logger = logging.getLogger(__name__)

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s',
                                  '%m-%d-%Y %H:%M:%S')

    file_handler = RotatingFileHandler(MY_LOG_FILE, maxBytes=10000000, backupCount=2)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Print to stdout if debug flag enabled
    if args['debug']:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)

    # Start main loop
    logger.info("Running {0} Against Provided List: {1} \n".format(SCRIPT_NAME, args['domains']))
    while True:

        # pull in list of hostnames
        mylist = readFile(args['domains'])
        myurl = getRandomUrl(mylist)
        mykey = 'http_' + myurl

        if isBackedoff(mykey, BACKOFF_DB):
            logger.error("Currently backed off for:  " + mykey)
        else:
            try:
                logger.info("trying to connect to http://"+ myurl)
                resp = requests.get("http://" + myurl, timeout=15, verify=False)
                logger.info("Request to "+myurl+" status= "+str(resp.status_code))
            except requests.exceptions.RequestException as e:
                logger.error(e)
                mydate = time.time()
                BACKOFF_DB['http_' + myurl] = mydate + timer
                logger.error("Backoff Val: " + str(BACKOFF_DB['http_' + myurl]))

        mykey = 'https_' + myurl
        if isBackedoff(mykey, BACKOFF_DB):
            logger.error("Currently backed off for:  " + mykey)
        else:
            try:
                logger.info("trying to connect to https://"+ myurl)
                resp2 = requests.get("https://" + myurl, timeout=15, verify=False)
                logger.info("Request to "+myurl+" status= "+str(resp2.status_code))

            except requests.exceptions.RequestException as e:
                logger.error(e)
                mydate = time.time()
                BACKOFF_DB['https_' + myurl] = mydate + timer
                logger.error("Backoff Val: " + str(BACKOFF_DB['https_' + myurl]))
        time.sleep(random.randrange(0,TIME_BETWEEN_REQUESTS))

if __name__ == "__main__":
    go()
