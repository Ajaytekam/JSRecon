#!/bin/bash 

GB='\033[1;32m'
YB='\033[1;33m'
NC='\033[0m' 

# Install gau 
echo -e "${YB}[*]${NC} Install gau..."
GO111MODULE=on go get -u -v github.com/lc/gau
echo -e "${YB}[*]${NC} gau installed.."

# Install subjs 
echo -e "${YB}[*]${NC} Install subjs..."
GO111MODULE=on go get -u -v github.com/lc/subjs
echo -e "${YB}[*]${NC} subjs installed.."

# install hakrawler 
echo -e "${YB}[*]${NC} Install hackrawler..."
go get github.com/hakluke/hakrawler
echo -e "${YB}[*]${NC} subjs installed.."

# install httpx
echo -e "${YB}[*]${NC} Install httpx..."
go get github.com/hakluke/hakrawler
echo -e "${YB}[*]${NC} httpx installed.."

mkdir -p ~/tools 

# Install linkfinder 
echo -e "${YB}[*]${NC} Install linkfinder..."
cd ~/tools 
git clone https://github.com/GerbenJavado/LinkFinder.git
cd LinkFinder
python3 setup.py install 
chmod +x linkfinder.py
# add to bashrc file 
echo 'alias linkfinder="/root/tools/LinkFinder/linkfinder.py"' >> ~/.bashrc
echo -e "${YB}[*]${NC} linkfinder installed.."
cd ..

# install secret-finder 
echo -e "${YB}[*]${NC} Install secretfinder..."
git clone https://github.com/Ajaytekam/SecretFinder.git
cd SecretFinder
chmod +x SecretFinder.py
pip3 install -r requirements.txt
echo -e "${YB}[*]${NC} secretfinder installed.."
echo "alias secretfinder='/root/tools/SecretFinder/SecretFinder.py'" >> ~/.bashrc
cd ..

# install relative-url-extractor 
echo -e "${YB}[*]${NC} Install relative-url-extractor..."
mkdir relative-url-extractor
cd relative-url-extractor
wget https://raw.githubusercontent.com/jobertabma/relative-url-extractor/master/extract.rb  
chmod +x extract.rb
echo "alias extracturl='/root/tools/relative-url-extractor/extract.rb'" >> ~/.bashrc 
echo -e "${YB}[*]${NC} relative-url-extractor installed.."
cd ..

