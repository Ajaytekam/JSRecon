#!/usr/bin/python3  

from libs.telegramText import NotifyTelegramBot 
import libs.coloredOP as co
from pathlib import Path
import os
import datetime
import re
import requests
import subprocess 
import argparse 
import sys

def executeCommand(COMMAND, verbose=False):
    try:
        subprocess.run(COMMAND, shell=True, check=True, text=True)
        if verbose:
            print("\t"+co.bullets.OK, co.colors.GREEN++"Command Executed Successfully."+co.END)
    except subprocess.CalledProcessError as e:
        print("\t"+co.bullets.ERROR, co.colors.BRED++"Error During Command Execution.!!"+co.END)
        print(e.output)
    return 

def ValideteDomain(domain):
    regex =  "^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\\.)+[A-Za-z]{2,6}"
    d = re.compile(regex)
    if(re.search(d, domain)):
        return True
    else:
        return False

def Banner():
    print("############################################")
    print("# "+co.BOLD+co.colors.GREEN+"JSRecon"+co.END+co.BOLD+" : Javascript Reconnaissance Tool"+co.END)
    print("# "+co.BOLD+"Developed by : "+co.colors.RED+"securebitlabs.com"+co.END)
    print("# version : 0.1")
    print("############################################\n")

def printInfo(Domain, OPDir):
    print(co.bullets.INFO, co.colors.CYAN+"Target Domain : {}".format(Domain)+co.END)
    print(co.bullets.INFO, co.colors.CYAN+"Result Dir    : {}\n".format(OPDir)+co.END)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="Domain name to perform reconnaissance")
    parser.add_argument("-o", "--out", help="Filename to perform operations on")
    parser.add_argument("-d", "--download", help="Download javascript Files on local machine", action="store_true")
    args = parser.parse_args()
    # Check argument
    if args.url is None:
        Banner()
        parser.print_help()
        sys.exit()
    ## GLOBAL Vars
    Banner()
    tDomain = "" # raw domain name
    Domain = ""  # Domain name with protocol 
    OPDir = ""   # Output Directory 
    # validae url
    if(ValideteDomain(args.url)):
        tDomain = args.url 
    else:
        print(co.bullets.ERROR, co.colors.BRED+"Invalid Domain:{}".format(args.url)+co.END)
        sys.exit()
    # get the http protocol 
    try:
        tempD = requests.head("https://"+tDomain, allow_redirects=True, timeout=8) 
        Domain = tempD.url
        Domain = re.sub(":443/$", "", Domain)
    except:
        try:
            tempD = requests.head("http://"+tDomain, allow_redirects=True, timeout=8) 
            Domain = tempD.url
            Domain = re.sub(":80/$", "", Domain)
        except:
            print(co.bullets.ERROR, co.colors.BRED+" Error : Could not resolve the Http protocol.!!"+co.END)
            sys.exit(1)
    # Sending telegram message
    txtmessage = "JSRecon staretd for domain : {}".format(tDomain)
    NotifyTelegramBot(txtmessage)
    # Create output dir 
    if args.out is not None:
        OPDir = args.out
        if os.path.isdir(OPDir):
            print(co.bullets.INFO+co.colors.CYAN+"{} already exists...".format(OPDir)+co.END)
            print(co.bullets.INFO+co.colors.CYAN+"Adding time-stamp into the directory name as suffix"+co.END)
            Date = str(datetime.datetime.now())
            WORKDIR = re.sub("-|:|\.|\ ", "_", Date)
            OPDir += "_{}".format(WORKDIR)
    else:
        OPDir = "./jsrecon_{}".format(tDomain)
        if os.path.isdir(OPDir):
            print(co.bullets.INFO+co.colors.CYAN+"{} already exists...".format(OPDir)+co.END)
            print(co.bullets.INFO+co.colors.CYAN+"Adding time-stamp into the directory name as suffix"+co.END)
            Date = str(datetime.datetime.now())
            WORKDIR = re.sub("-|:|\.|\ ", "_", Date)
            OPDir += "_{}".format(WORKDIR)
    os.mkdir(OPDir) 
    printInfo(Domain, OPDir)
    #################
    ## Collecting Javascript urls
    os.chdir(OPDir)
    COMMAND = 'gau {} | grep -iE "\.js$" >> tempgau'.format(tDomain)
    print(co.bullets.CProcess, co.colors.GREEN+"Collecting JS urls using gau"+co.END)
    executeCommand(COMMAND)
    ## Collecting Javascript subjs 
    UserAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    COMMAND = 'echo {} | subjs -c 10 -ua "{}" >> tempsubjs'.format(Domain, UserAgent)
    print(co.bullets.CProcess, co.colors.GREEN+"Collecting JS urls using subjs"+co.END)
    executeCommand(COMMAND)
    ## Collecting Javascript hakrawler 
    COMMAND = 'echo {} | hakrawler -d 3 -insecure | grep -iE "\.js$" >> temphakrawler'.format(Domain)
    print(co.bullets.CProcess, co.colors.GREEN+"Collecting JS urls using hakrawler "+co.END)
    executeCommand(COMMAND)
    ## merging all JS files
    COMMAND = 'cat tempgau tempsubjs temphakrawler | sort -u >> jsurls'
    print(co.bullets.CProcess, co.colors.GREEN+"Merging all collected URLs"+co.END)
    executeCommand(COMMAND)
    ## Get the JS files with status 200
    COMMAND = 'cat jsurls | httpx -silent -mc 200 >> js_200'
    print(co.bullets.CProcess, co.colors.GREEN+"Filtering collected URLs for HTTP Status 200 "+co.END)
    executeCommand(COMMAND)
    # Count Number of JS found
    JSfile = open("js_200", "r").read()
    NoOfJS = JSfile.count("\n") - 1
    if NoOfJS > 0:
        print(co.bullets.INFO+co.colors.CYAN+" {} Javascript files found".format(NoOfJS)+co.END)
    # Delete temp files 
    if os.path.isfile("tempgau"):
        os.remove("tempgau")
    if os.path.isfile("tempsubjs"):
        os.remove("tempsubjs")
    if os.path.isfile("temphakrawler"):
        os.remove("temphakrawler")
    ##################
    ## Download JS Files 
    if args.download:
        print(co.bullets.CProcess, co.colors.GREEN+"Downloading JS files into local machine"+co.END)
        os.mkdir("JSFiles")
        os.chdir("JSFiles")
        try:
            subprocess.run('cat ../js_200 | parallel -j50 -q curl -O -J -sk', shell=True, text=True)
            print("\t"+co.bullets.OK, co.colors.CYAN+"Files Downloaded Successfully.."+co.END) 
        except subprocess.CalledProcessError as e:
            print(co.bullets.ERROR, co.colors.BRED+"There are some problem during downloading of JS Files."+co.END)
            print(e.output)
        os.chdir("..")
    ################## 
    ## Get JS Endpoints  
    COMMAND = 'while read -r jsurl; do echo "[ + ] URL: $jsurl" >> linkfinderResult.txt;python3 /root/tools/LinkFinder/linkfinder.py -d -i $jsurl -o cli >> linkfinderResult.txt; printf "\n\n" >> linkfinderResult.txt; done < js_200'
    print(co.bullets.CProcess, co.colors.GREEN+"Scraping Endpoints with linkfinder "+co.END)
    executeCommand(COMMAND)
    ################## 
    ## Get Javascript Secrets   
    COMMAND = 'while read -r jsurl; do /root/tools/SecretFinder/SecretFinder.py -i $jsurl -o cli >> secretfinderResults.txt;printf "\n\n" >> secretfinderResults.txt; done < js_200'
    print(co.bullets.CProcess, co.colors.GREEN+"Scraping Secrets with secretfinder "+co.END)
    executeCommand(COMMAND)
    print(co.bullets.OK, co.colors.CYAN+"Javascript Reconnaissance Completed.."+co.END)
    # Sending telegram message
    txtmessage = "JSRecon Completed for Domain : {}".format(tDomain)
    NotifyTelegramBot(txtmessage)
    txtmessage = "results are stored on : {}".format(OPDir)
    NotifyTelegramBot(txtmessage)
     
if __name__ == "__main__":
    main()

