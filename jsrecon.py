#!/usr/bin/python3  

from pathlib import Path
import os
import datetime
import re
import requests
import subprocess 
import argparse 
import sys
import configparser

def executeCommand(COMMAND, verbose=False):
    try:
        subprocess.run(COMMAND, shell=True, check=True, text=True)
        if verbose:
            print("\t[*] Command Executed Successfully.")
    except subprocess.CalledProcessError as e:
        print("\t[-] Error During Command Execution.!!")
        print(e.output)
    return 

def NotifyTelegramBot(textMessage):
    ConfigPath = "/root/notificationConfig.ini"
    print("[+] Sending notification to telegram bot")
    config = configparser.RawConfigParser()
    if os.path.isfile(ConfigPath):
        config.read(ConfigPath)
        if config.has_option("telegram","apiToken") and config.has_option("telegram","chatId"): 
            apiToken = config.get("telegram","apiToken")
            chatId = config.get("telegram","chatId")
            send_text = 'https://api.telegram.org/bot'+apiToken+'/sendMessage?chat_id='+chatId+'&parse_mode=Markdown&text='+textMessage
            response = requests.post(send_text)
            if response.status_code == 200:
                print("\t[!] Message Send successfully")
        else:
            print("[-] Error : no credentials are setted for Telegram bot (API token and ChatId)")
    else:
        print("[-] Error : There is no config file available '/root/notificationConfig.ini'")

def ValideteDomain(domain):
    regex =  "^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\\.)+[A-Za-z]{2,6}"
    d = re.compile(regex)
    if(re.search(d, domain)):
        return True
    else:
        return False
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="Domain name to perform reconnaissance")
    parser.add_argument("-o", "--out", help="Filename to perform operations on")
    parser.add_argument("-d", "--download", help="Download javascript Files on local machine", action="store_true")
    args = parser.parse_args()
    # Check argument
    if args.url is None:
        print("JSRecon\tversion0.1")
        print("Developed by : securebitlabs.com\n")
        parser.print_help()
        sys.exit()
    ## GLOBAL Vars
    tDomain = "" # raw domain name
    Domain = ""  # Domain name with protocol 
    OPDir = ""   # Output Directory 
    # validae url
    if(ValideteDomain(args.url)):
        tDomain = args.url 
    else:
        print("[-] Invalid Domain: {}".format(args.url))
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
            print("[-] Error : Could not resolve the Http protocol.!!")
            sys.exit(1)
    # Sending telegram message
    txtmessage = "JSRecon staretd for domain : {}".format(Domain)
    NotifyTelegramBot(txtmessage)
    # Create output dir 
    if args.out is not None:
        OPDir = args.out
        if os.path.isdir(OPDir):
            print("[+] {} already exists...".format(OPDir))
            print("[+] Adding time-stamp into the directory name as suffix")
            Date = str(datetime.datetime.now())
            WORKDIR = re.sub("-|:|\.|\ ", "_", Date)
            OPDir += "_{}".format(WORKDIR)
    else:
        OPDir = "./jsrecon_{}".format(tDomain)
        if os.path.isdir(OPDir):
            print("[+] {} already exists...".format(OPDir))
            print("[+] Adding time-stamp into the directory name as suffix")
            Date = str(datetime.datetime.now())
            WORKDIR = re.sub("-|:|\.|\ ", "_", Date)
            OPDir += "_{}".format(WORKDIR)
    os.mkdir(OPDir) 
    #################
    ## Collecting Javascript urls
    os.chdir(OPDir)
    COMMAND = 'gau {} | grep -iE "\.js$" >> tempgau'.format(tDomain)
    print("[+] Collecting JS urls using gau ")
    executeCommand(COMMAND)
    ## Collecting Javascript subjs 
    UserAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    COMMAND = 'echo {} | subjs -c 10 -ua "{}" >> tempsubjs'.format(Domain, UserAgent)
    print("[+] Collecting JS urls using subjs ")
    executeCommand(COMMAND)
    ## Collecting Javascript hakrawler 
    COMMAND = 'echo {} | hakrawler -d 3 -insecure | grep -iE "\.js$" >> temphakrawler'.format(Domain)
    print("[+] Collecting JS urls using hakrawler ")
    executeCommand(COMMAND)
    ## merging all JS files
    COMMAND = 'cat tempgau tempsubjs temphakrawler | sort -u >> jsurls'
    print("[+] Merging all collected URLs")
    executeCommand(COMMAND)
    ## Get the JS files with status 200
    COMMAND = 'cat jsurls | httpx -silent -mc 200 >> js_200'
    print("[+] Filtering collected URLs for HTTP Status 200 ")
    executeCommand(COMMAND)
    # Count Number of JS found
    JSfile = open("js_200", "r").read()
    NoOfJS = JSfile.count("\n") - 1
    if NoOfJS > 0:
        print("[!] {} Javascript files found".format(NoOfJS))
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
        print("[+] Downloading JS files into local machine")
        os.mkdir("JSFiles")
        os.chdir("JSFiles")
        try:
            subprocess.run('cat ../js_200 | parallel -j50 -q curl -O -J -sk', shell=True, text=True)
            print("\t[*] Files Downloaded Successfully..") 
        except subprocess.CalledProcessError as e:
            print("There are some problem during downloading of JS Files.")
            print(e.output)
        os.chdir("..")
    ################## 
    ## Get JS Endpoints  
    COMMAND = 'while read -r jsurl; do echo "[ + ] URL: $jsurl" >> linkfinderResult.txt;linkfinder -d -i $jsurl -o cli >> linkfinderResult.txt; printf "\n\n" >> linkfinderResult.txt; done < js_200'
    print("[+] Scraping Endpoints with linkfinder ")
    executeCommand(COMMAND)
    ################## 
    ## Get Javascript Secrets   
    COMMAND = 'while read -r jsurl; do secretfinder -i $jsurl -o cli >> secretfinderResults.txt;printf "\n\n" >> secretfinderResults.txt; done < js_200'
    print("[+] Scraping Secrets with secretfinder ")
    executeCommand(COMMAND)
    print("[+] Javascript Reconnaissance Completed.. ")
    # Sending telegram message
    txtmessage = "JSRecon Completed for Domain : {}".format(Domain)
    NotifyTelegramBot(txtmessage)
    txtmessage = "results are stored on : {}".format(OPDir)
    NotifyTelegramBot(txtmessage)
     
if __name__ == "__main__":
    main()

