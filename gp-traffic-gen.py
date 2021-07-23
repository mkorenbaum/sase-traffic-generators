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
import datetime
import os
import sys

# Global Vars

timer = 10800
SCRIPT_NAME = "SASE Demo Traffic Generator"
TIME_BETWEEN_REQUESTS = 0       # default no delay between requests

# Set NON-SYSLOG logging to use function name
logger = logging.getLogger(__name__)

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
    debug_group.add_argument("--debug", "-D", help="Verbose Debug info, levels 0-2", type=int,
                             default=0)

    args = vars(parser.parse_args())

    if args['debug'] == 1:
        logging.basicConfig(level=logging.INFO,
                            format="%(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")
        logger.setLevel(logging.INFO)
    elif args['debug'] >= 2:
        logging.basicConfig(level=logging.DEBUG,
                            format="%(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")
        logger.setLevel(logging.DEBUG)
    else:
        # Remove all handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        # set logging level to default
        logger.setLevel(logging.WARNING)

    # ##########################################################################
    # Draw Interactive login banner
    ############################################################################

    print("{0} \n".format(SCRIPT_NAME))

    ############################################################################
    # End Login handling, begin script..
    ############################################################################

    while True:
        # pull in list of hostnames
        mylist = readFile(args['domains'])
        myurl = getRandomUrl(mylist)
        mykey = 'http_' + myurl

        if isBackedoff(mykey, BACKOFF_DB):
            print("Currently backed off for:  " + mykey)
        else:
            try:
                print("trying to connect to http://"+ myurl)
                resp = requests.get("http://" + myurl + "/robots.txt", timeout=1)
                print("Request to "+myurl+" status= "+str(resp.status_code))
            except requests.exceptions.RequestException as e:
                print(e)
                mydate = time.time()
                BACKOFF_DB['http_' + myurl] = mydate + timer
                print("Backoff Val: " + str(BACKOFF_DB['http_' + myurl]))

        mykey = 'https_' + myurl
        if isBackedoff(mykey, BACKOFF_DB):
            print("Currently backed off for:  " + mykey)
        else:
            try:
                print("trying to connect to https://"+ myurl)
                resp2 = requests.get("https://" + myurl + "/robots.txt", timeout=1)
                print("Request to "+myurl+" status= "+str(resp2.status_code))


            except requests.exceptions.RequestException as e:
                print(e)
                mydate = time.time()
                BACKOFF_DB['https_' + myurl] = mydate + timer
                print("Backoff Val: " + str(BACKOFF_DB['https_' + myurl]))


if __name__ == "__main__":
    go()