Prisma SASE Traffic Generator

This set of scripts are used to generate traffic in the SASE Demo Environment

#### Synopsis

Set of scripts and config files required to do client side traffic generation of the following type. 

* gp-traffic-gen.py - script to be run on client machines that are connected to Prisma Access via GP, or MU
* appdomain.txt - list of domains that will simulate a user doing generic internet browsing 
* badsites.txt - list of domains (mostly external) that will trigger various security rules in Prisma Access


#### Requirements

* Host OS (Ubuntu => 18.04, Windows => 10)
* Global Protect Installed or Explicit Proxy configured to point to Prisma Acess
* Python => 3.7
* Python modules:
  * requests

#### License

MIT

#### Installation

1. Install python and requests library 
2. Upload appdomain.txt, badsites.txt, and gp-traffic-gen.py to the host machine
3. Install GP client or set proxy settings from Prisma Access
4. Create or edit the rc.local file or similar in Windows to have 2 instances of the script launch at machine startup
   * Each instance will reference appdomain.txt and badsites.txt respectively
5. Make all scripts and rc.local file executable (chmod +x *.*) or equivalent in Windows
6. Optionally edit the .txt files to include additional domains
7. Reboot and check the scripts auto start on login

#### Usage 
```
usage: gp-traffic-gen.py [-h] --domains DOMAINS [--insecure] [--debug DEBUG]

SASE Demo Traffic Generator.

optional arguments:
  -h, --help            show this help message and exit

Options:
  --domains DOMAINS, -d DOMAINS
                        List of hosts with /r as delimeter, ex. C:/Users/Admin/Desktop/appdomain.txt
  --insecure, -I        Disable SSL certificate and hostname verification

Debug:
  These options enable debugging output

  --debug DEBUG, -D DEBUG
                        Verbose Debug info, levels 0-2

```

#### Version

| Version | Build | Changes |
| ------- | ----- | ------- |
| **1.0.0** | **b1** | Initial Release. |



